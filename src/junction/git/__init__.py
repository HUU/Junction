import logging
from pathlib import Path
from enum import Enum
from typing import List
from git import Repo, Commit, NULL_TREE, Diff, Tree


logger = logging.getLogger(__name__)


def find_repository_root(path: Path):
    path = path.resolve()

    def _find_repository_root(path: Path):
        if path.joinpath("./.git").exists():
            logger.debug("Located .git folder under %s.", path)
            return path
        elif path.parent == path:
            # when at a root, the parent will be the same as path, so we bottomed out; no repository found
            logger.error(
                "Searched all parent directories until hitting a root and found no .git folder."
            )
            return None
        else:
            return _find_repository_root(path.parent)

    return _find_repository_root(path)


def find_commits_on_branch_after(branch_name: str, start_commit_sha: str, repo: Repo):
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
    def __init__(
        self,
        old_path: str,
        new_path: str,
        change_type: ModificationType,
        source_code: str = None,
    ):
        self._old_path = Path(old_path) if old_path is not None else None
        self._new_path = Path(new_path) if new_path is not None else None
        self.change_type = change_type
        self.source_code = source_code

    @property
    def previous_path(self):
        return self._old_path if self.change_type == ModificationType.RENAME else None

    @property
    def path(self):
        return self._new_path if self._new_path else self._old_path

    @staticmethod
    def _determine_modification_type(diff: Diff):
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
    def from_diff(diff: Diff, tree: Tree):
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

    def __repr__(self):
        return f"{self.change_type} {self.path}"


def get_modifications(commit: Commit):
    if commit.parents:
        diffs = commit.parents[0].diff(commit)
    else:
        # initial commit
        diffs = commit.diff(NULL_TREE)

    return [Modification.from_diff(d, tree=commit.tree) for d in diffs]


def filter_modifications_to_folder(modifications: List[Modification], folder: Path):

    for mod in modifications:
        new_path_in_folder = folder in mod.path.parents
        old_path_in_folder = (
            folder in mod.previous_path.parents if mod.previous_path else False
        )
        if new_path_in_folder or old_path_in_folder:
            yield Modification(
                mod.previous_path.relative_to(folder)
                if old_path_in_folder
                else mod.previous_path,
                mod.path.relative_to(folder) if new_path_in_folder else mod.new_path,
                mod.change_type,
                mod.source_code,
            )
