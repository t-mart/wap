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
    help=("The path of the configuration file to create."),
)
def new_config(
    config_path: Path,
) -> None:
    """
    Create a new configuration file with some pre-filled data.

    To avoid data loss, this path must not exist.

    This command is interactive, and will ask you some questions about your project.

    This command targeted towards existing projects that want to start using wap or
    projects that want to migrate from another packager.

    More than likely, you will need to edit this configuration file to fit to your
    project. This just provides a starting point.
    """
    if config_path.exists():
        raise NewConfigException(
            'Path "'
            + click.style(f"{config_path}", fg="green")
            + '" exists. Aborting to avoid data loss.'
        )

    project_name = Path.cwd().name

    config = guide(project_dir_name=project_name)
    log.info('\nCreating config file at "' + click.style(f"{config_path}", fg="green"))
    log.info(click.style("Make sure to edit it to fit your project!", fg="yellow"))
    config.to_path(config_path)
