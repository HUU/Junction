import click
from junction.confluence import Confluence


@click.group()
@click.option("--confluence-api", envvar="CONFLUENCE_API")
@click.option("--username", envvar="CONFLUENCE_USERNAME")
@click.option("--password", envvar="CONFLUENCE_PASSWORD")
def main(ctx: click.Context, confluence_api: str, username: str, password: str):
    ctx.obj = Confluence(confluence_api, username, password)
    click.echo("lol")


@main.command
@click.option("--git-dir", envvar="GIT_DIR")
@click.option("--since", default="HEAD^")
@click.option("--dry-run", default=False)
@click.pass_obj
def delta(confluence: Confluence):
    click.echo("hej")
