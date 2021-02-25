from pathlib import Path

import click

from wap import log
from wap.commands.common import DEFAULT_CONFIG_PATH, PATH_TYPE
from wap.exception import NewConfigException
from wap.guided_config import guide


@click.command()
@click.option(
    "-c",
    "--config-path",
    type=PATH_TYPE,
    default=str(DEFAULT_CONFIG_PATH),
    show_default=str(DEFAULT_CONFIG_PATH),
    help=("The path of the configuration file."),
)
def new_config(
    config_path: Path,
) -> int:
    """
    Creates a new configuration file with some pre-filled data.

    The name of the current directory will be used as the name of the addon and as the
    configured directory and lua code file: These are merely suggestions to get you
    started and may be changed at will.
    """
    if config_path.exists():
        raise NewConfigException(
            f'"'
            + click.style(f"{config_path}", fg="green")
            + '" exists. Aborting to avoid data loss.'
        )

    project_name = Path.cwd().name

    config = guide(project_dir_name=project_name)
    log.info('\nCreating config file at "' + click.style(f"{config_path}", fg="green"))
    log.info(click.style("Make sure to edit it to fit your project!", fg="yellow"))
    config.to_path(config_path)

    return 0
