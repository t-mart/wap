import json
from pathlib import Path

import click

from wap import log
from wap.commands.common import config_path_option, json_option
from wap.config import Config
from wap.exception import ConfigException


@click.command()
@config_path_option()
@json_option(help="Prints the config file in JSON format.")
def validate(
    config_path: Path,
    show_json: bool,
) -> int:
    """
    Validates a wap config file. An exit code of 0 means the validation was successful.

    Successful validation does not indicate that you can use all the wap commands. It
    merely means that there were no errors parsing it.
    """
    try:
        config = Config.from_path(config_path)

        log.info(f'✔️ "{config_path}" is valid')

        if show_json:
            click.echo(json.dumps(config.to_python_object(), indent=2))

        return 0
    except ConfigException as ce:
        log.error(f'❌ "{config_path}" is not valid')
        log.error(str(ce))
        return 1
