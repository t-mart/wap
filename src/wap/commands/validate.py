from pathlib import Path

import click

from wap.commands.util import config_path_option
from wap.config import Config
from wap.console import error, print
from wap.exception import WapError


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
    except WapError as wap_exc:
        error(wap_exc.message)
        print("invalid", stderr=False)
        return 1

    print("valid", stderr=False)
    return 0
