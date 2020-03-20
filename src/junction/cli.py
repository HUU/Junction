import logging
import click
import click_log
from typing import Dict, Optional
from pathlib import Path
from git import Repo, Commit

from junction import __version__
from junction.confluence import Confluence
from junction.git import (
    find_repository_root,
    find_commits_on_branch_after,
    filter_modifications_to_folder,
    get_modifications,
)
from junction.delta import Delta, MovePage, UpdatePage, CreatePage, DeletePage


class CliContext(object):
    def __init__(self) -> None:
        self.repo: Optional[Repo] = None
        self.confluence: Optional[Confluence] = None


def __verbosity_count_to_log_level(count: int) -> int:
    if count <= 0:
        return logging.ERROR
    elif count == 1:
        return logging.WARN
    elif count == 2:
        return logging.INFO
    else:
        return logging.DEBUG


@click.group()
@click.option(
    "-c",
    "--confluence-api",
    envvar="CONFLUENCE_API",
    required=True,
    help="URL to the Confluence Cloud API i.e. https://<account name>.atlassian.net/wiki/rest/api",
)
@click.option(
    "-u",
    "--user",
    envvar="CONFLUENCE_API_USER",
    required=True,
    help="Login name with which to access the API, usually the account e-mail.",
)
@click.option(
    "-p",
    "--key",
    envvar="CONFLUENCE_API_KEY",
    required=True,
    prompt="Confluence API Key",
    hide_input=True,
    help="API key with which to access the API, can be issued from https://id.atlassian.com/manage/api-tokens",
)
@click.option(
    "-s",
    "--space",
    required=True,
    help="The key of the space which will be updated by Junction; look at the URL in your browser when accessing the wiki in question if you don't know this.",
)
@click.option("-v", "--verbose", count=True, help="Set the verbosity level.")
@click.version_option(__version__)
@click.pass_context
def main(
    ctx: click.Context,
    confluence_api: str,
    user: str,
    key: str,
    space: str,
    verbose: int,
) -> None:
    """Tools for managing and publishing to a Confleunce Cloud wiki using Markdown files."""
    logger = click_log.basic_config()
    logger.setLevel(__verbosity_count_to_log_level(verbose))
    context = CliContext()
    context.confluence = Confluence(confluence_api, user, key, space)
    ctx.obj = context


def _validate_git_dir(ctx: click.Context, param: click.Parameter, value: str) -> Path:
    path = Path(value)
    git_root = find_repository_root(path)
    if git_root is None:
        raise click.BadParameter(
            "junction must be run from within a git repository, or git-dir must point to a git repository"
        )
    else:
        ctx.obj.repo = Repo(git_root)
        return path


def _validate_commitish(ctx: click.Context, param: click.Parameter, value: str) -> str:
    try:
        if ctx.obj.repo.commit(value):
            return value
        else:
            raise click.BadParameter("no commit found by dereferencing that commitish")
    except Exception:
        raise click.BadParameter(
            "this is an invalid commit-ish; valid examples include HEAD~3 or a commit SHA"
        )


def _validate_branch(ctx: click.Context, param: click.Parameter, value: str) -> str:
    if value in ctx.obj.repo.heads:
        return value
    else:
        raise click.BadParameter("you must provide a valid branch name e.g. master")


@main.command()
@click.argument("since", default="HEAD^", callback=_validate_commitish)
@click.argument("branch", default="master", callback=_validate_branch)
@click.option(
    "--git-dir",
    envvar="GIT_DIR",
    is_eager=True,
    default=".",
    type=click.Path(exists=True, file_okay=False),
    callback=_validate_git_dir,
    help="Location of the git repository to scan for changes.  This can be any path within the repository tree, it will automatically be resolved.",
)
@click.option(
    "--content-path",
    type=click.Path(exists=True, file_okay=False),
    help="Path within the git repository to look for within the git repository; evaluated relative to the current path, not the git root.",
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    type=bool,
    help="Do not write any changes to the wiki and instead print out what would have been done and exit.",
)
@click.pass_obj
def delta(
    my_ctx: CliContext,
    branch: str,
    since: str,
    git_dir: Path,
    content_path: str,
    dry_run: bool,
) -> None:
    """Updates Confluence by finding modifications in a git repository.

    Looks for files under [content-path] affected by all commits from [SINCE] to the head of [BRANCH]
    and then performs Confluence API calls to realize those changes onto the wiki.

    [SINCE] must be a valid commitish within the targeted git repository and should be part of the history
    of [BRANCH] i.e. you can get from SINCE to the HEAD of [BRANCH].
    """

    filter_path = Path(content_path) if content_path else git_dir
    commits = find_commits_on_branch_after(branch, since, my_ctx.repo)
    deltas = {
        c: Delta.from_modifications(
            filter_modifications_to_folder(get_modifications(c), filter_path)
        )
        for c in commits
    }

    if dry_run:
        __pretty_print_deltas(deltas)
    else:
        if my_ctx.confluence:
            for delta in deltas.values():
                delta.execute(my_ctx.confluence)
        else:
            raise RuntimeError(
                "Confluence API client was not setup, but this should never happen; file a bug."
            )


def __pretty_print_deltas(deltas: Dict[Commit, Delta]) -> None:
    for commit, delta in deltas.items():

        all_operations = (
            delta.adds
            + delta.updates
            + delta.deletes
            + delta.start_renames
            + delta.finish_renames
        )
        click.echo(
            f"{commit.hexsha} ({click.style(str(len(all_operations)), fg='cyan')} changes)"
        )
        for op in all_operations:
            if isinstance(op, CreatePage):
                click.echo(
                    f"\t{click.style('CREATE', fg='green')} {' / '.join(op.ancestor_titles + [op.title])}"
                )
            elif isinstance(op, UpdatePage):
                click.echo(
                    f"\t{click.style('UPDATE', fg='yellow')} {' / '.join(op.ancestor_titles + [op.title])}"
                )
            elif isinstance(op, DeletePage):
                click.echo(f"\t{click.style('DELETE', fg='red')} ?? / {op.title}")
            elif isinstance(op, MovePage):
                click.echo(
                    f"\t{click.style('RENAME', fg='blue')} ?? / {op.title} -> {' / '.join(op.ancestor_titles + [op.new_title])}"
                )
            else:
                click.echo(
                    f"\t{click.style(type(op).__name__, fg='magenta')} {op.title}"
                )
