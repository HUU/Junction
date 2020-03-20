import logging
from pathlib import Path
from enum import Enum
from typing import List, Optional, Generator, Union, Iterable
from git import Repo, Commit, NULL_TREE, Diff, Tree


logger = logging.getLogger(__name__)


def find_repository_root(path: Path) -> Optional[Path]:
    """Locates the root of the git repository a given path is located within.  Searches upwards for a folder
    containing a ".git" directory.

    Arguments:
        path {Path} -- A path to any location inside a git repository--can be a file or a folder.

    Returns:
        Optional[Path] -- The root of the git repository (the parent of .git) or None if no git repository is found.
    """

    path = path.resolve()

    def _find_repository_root(path: Path) -> Optional[Path]:
        if path.joinpath("./.git").exists():
            logger.debug("Located .git folder under %s.", path)
            return path
        elif path.parent == path:
            # when at a root, the parent will be the same as path, so we bottomed out; no repository found
            logger.debug(
                "Searched all parent directories until hitting a root and found no .git folder."
            )
            return None
        else:
            return _find_repository_root(path.parent)

    return _find_repository_root(path)


def find_commits_on_branch_after(
    branch_name: str, start_commit_sha: Optional[str], repo: Repo
) -> List[Commit]:
    """Gets a list of commits on a given branch after a particular starting point.  The starting commit
    is NOT included in the result.  The commits will be ordered chronologically from oldest to newest.

    If start_commit_sha is None, the result will include every commit on the branch since it was created.

    Arguments:
        branch_name {str} -- The name of the branch whose history will be sampled.
        start_commit_sha {str} -- The commit hash to start from or None if the entire branch history should be included.
        repo {Repo} -- The repository to sample commits from.

    Returns:
        List[Commit] -- A generator that returns commits after start_commit_sha in chronological order up to the HEAD of branch_name
    """

    rev = (
        branch_name
        if start_commit_sha is None
        else f"{start_commit_sha}..{branch_name}"
    )
    reverse_chronological_commits = list(repo.iter_commits(rev, first_parent=True))
    reverse_chronological_commits.reverse()
    return reverse_chronological_commits


class ModificationType(Enum):
    ADD = 1
    RENAME = 2
    DELETE = 3
    MODIFY = 4
    UNKNOWN = 5


class Modification:
    """ Represents a modification to the filesystem.  This is used to abstract the details of git from other subsystems that consume information
    about changes such as the Delta API. """

    def __init__(
        self,
        old_path: Optional[Union[str, Path]],
        new_path: Optional[Union[str, Path]],
        change_type: ModificationType,
        source_code: Optional[str] = None,
    ):
        """Initializes an instance of Modification.

        Arguments:
            old_path {Optional[Union[str, Path]]} -- The original path to the modified file.  May be None for all modifications except renames.
            new_path {Optional[Union[str, Path]] -- The current path to the modified file.  May be None if old_path is set.
            change_type {ModificationType} -- The modification made to this file.

        Keyword Arguments:
            source_code {Optional[str]} -- The contents of the file after the modification; should only be None for deletes (default: {None}).
        """
        self._old_path = Path(old_path) if old_path is not None else None
        self._new_path = Path(new_path) if new_path is not None else None
        self.change_type = change_type
        self.source_code = source_code

    @property
    def previous_path(self) -> Optional[Path]:
        return self._old_path if self.change_type == ModificationType.RENAME else None

    @property
    def path(self) -> Optional[Path]:
        return self._new_path if self._new_path else self._old_path

    @staticmethod
    def _determine_modification_type(diff: Diff) -> ModificationType:
        """Inspects a Diff from PythonGit to determine the type of modification.

        Arguments:
            diff {Diff} -- a Diff to inspect.

        Returns:
            ModificationType -- Add if a new file is committed; delete if a file is removed; rename if a file is moved; and modify otherwise.
        """
        if diff.new_file:
            return ModificationType.ADD
        if diff.deleted_file:
            return ModificationType.DELETE
        if diff.renamed_file:
            return ModificationType.RENAME
        if diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
            return ModificationType.MODIFY

        return ModificationType.UNKNOWN

    @staticmethod
    def from_diff(diff: Diff, tree: Tree) -> "Modification":
        """Builds a modification out of a diff and the tree of the commit.

        Arguments:
            diff {Diff} -- a Diff to inspect
            tree {Tree} -- the Tree of the commit this diff comes from, used to extract source code

        Returns:
            Modification -- A modification representing the provided diff.
        """
        old_path = diff.a_path
        new_path = diff.b_path
        change_type = Modification._determine_modification_type(diff)

        tree_path = new_path if new_path else old_path
        source_code = (
            tree[tree_path].data_stream.read()
            if change_type != ModificationType.DELETE
            else None
        )

        mod = Modification(old_path, new_path, change_type, source_code)
        logger.debug(
            "%s, with %s bytes of source code.",
            mod,
            len(source_code) if source_code else 0,
        )
        return mod

    def __repr__(self) -> str:
        return f"{self.change_type} {self.path}"


def get_modifications(commit: Commit) -> List[Modification]:
    """Extracts all the modifications from a given commit.

    Arguments:
        commit {Commit} -- A git commit.

    Returns:
        List[Modification] -- All modifications contained within the git commit.
    """

    if commit.parents:
        diffs = commit.parents[0].diff(commit)
    else:
        # initial commit
        diffs = commit.diff(NULL_TREE)

    return [Modification.from_diff(d, tree=commit.tree) for d in diffs]


def filter_modifications_to_folder(
    modifications: Iterable[Modification], folder: Path
) -> Generator[Modification, None, None]:
    """Filters modifications to only those within a given folder.  It rewrites all paths in the modifications to be
    relative to the specified folder.  That is, if a modification is to "foobar/hello.md" and folder is set to "foobar/"
    the resulting modification will have a path of "hello.md" instead of "foobar/hello.md"


    Arguments:
        modifications {List[Modification]} -- A collection of modifications to filter.
        folder {Path} -- A path within the git repository.

    Yields:
        Modification -- A modification with all paths relative to the specified folder.
    """

    for mod in modifications:
        new_path_in_folder = folder in mod.path.parents if mod.path else False
        old_path_in_folder = (
            folder in mod.previous_path.parents if mod.previous_path else False
        )
        if new_path_in_folder or old_path_in_folder:

            if new_path_in_folder and not old_path_in_folder and mod.previous_path:
                modification_type = ModificationType.ADD
            elif not new_path_in_folder and old_path_in_folder and mod.previous_path:
                modification_type = ModificationType.DELETE
            else:
                modification_type = mod.change_type

            yield Modification(
                mod.previous_path.relative_to(folder)
                if mod.previous_path and old_path_in_folder
                else None,
                mod.path.relative_to(folder)
                if mod.path and new_path_in_folder
                else None,
                modification_type,
                mod.source_code,
            )
