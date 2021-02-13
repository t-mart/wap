from pathlib import Path
from wap.exception import NewConfigException

import click

from wap.commands.common import (
    DEFAULT_CONFIG_PATH,
    PATH_TYPE,
)
from wap.config import default_config
from wap.log import info


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
) -> None:
    """
    Creates a new configuration file.
    """
    if config_path.exists():
        raise NewConfigException(f"{config_path} exists. Aborting to avoid data loss.")


    project_name = Path(".").resolve().name

    config = default_config(project_name)
    info(f"Creating config file at {config_path}")
    config.to_path(config_path)
