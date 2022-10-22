import webbrowser
from textwrap import dedent

import click

from wap import __name__ as package_name
from wap import __version__
from wap.commands.build import build
from wap.commands.new_config import new_config
from wap.commands.new_project import new_project
from wap.commands.publish import publish
from wap.commands.validate import validate
from wap.console import print


def open_or_print_help_url(command_name: str | None = None) -> None:
    if command_name is None:
        full_url = BASE_HELP_URL
    else:
        full_url = f"{BASE_HELP_URL}/commands/{command_name}"

    try:
        webbrowser.open(full_url)
    except webbrowser.Error:
        print(f"See documentation at [url]{full_url}[/url]")


# this subcommand is defined here because it uses the list of all subcommands. if it
# were in its own file (like the other subcommands), there'd be a circular dependency.
@click.command("help")
@click.argument("subcommand", required=False)
def help_command(subcommand: str | None) -> None:
    """Open the help webpage for the given SUBCOMMAND in your browser."""
    if subcommand is None:
        open_or_print_help_url()
    elif subcommand not in SUBCOMMAND_NAMES:
        raise click.BadArgumentUsage(
            f"Unknown subcommand {subcommand}. See available subcommands with "
            "`wap help`."
        )
    else:
        open_or_print_help_url(subcommand)


SUBCOMMANDS = [
    build,
    help_command,
    new_config,
    new_project,
    publish,
    validate,
]
SUBCOMMAND_NAMES = {command.name for command in SUBCOMMANDS}
BASE_HELP_URL = "http://t-mart.github.io/wap"


@click.group()
@click.version_option(
    package_name=package_name,
    message=f"wap version {__version__}",
)
def base() -> int | None:
    """World of Warcraft addon packager"""


for subcommand in SUBCOMMANDS:
    base.add_command(subcommand)
    if subcommand.help:
        subcommand.help = (
            dedent(subcommand.help)
            + f"\n\nRun `wap help {subcommand.name}` for more information."
        )
