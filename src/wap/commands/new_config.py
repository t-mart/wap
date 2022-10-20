from pathlib import Path

import click

from wap.commands.util import DEFAULT_CONFIG_PATH
from wap.console import print
from wap.prompt import prompt_for_config


@click.command()
@click.option(
    "-c",
    "--config-path",
    type=click.Path(file_okay=False, dir_okay=False, path_type=Path),
    default=str(DEFAULT_CONFIG_PATH),
    show_default=True,
    help=("The path to the new configuration file."),
)
def new_config(
    config_path: Path,
) -> None:
    """
    Create a new configuration file in the current directory.
    """
    config = prompt_for_config(mode="new-config")

    config.write_to_path(config_path, indent=True)

    print(f"Created config file at [path]{config_path.resolve()}[path]")
