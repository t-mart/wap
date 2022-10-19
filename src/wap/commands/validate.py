from pathlib import Path

import click

from wap.commands.util import config_path_option
from wap.config import Config
from wap.console import print_out, error
from wap.exception import WapException


@click.command()
@config_path_option()
def validate(
    config_path: Path,
) -> int:
    """
    Validate a configuration file.
    """
    try:
        Config.from_path(config_path)
    except WapException as wap_exc:
        error(wap_exc.message)
        print_out("invalid")
        return 1

    print_out("valid")
    return 0
