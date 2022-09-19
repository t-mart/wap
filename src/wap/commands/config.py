import json
from pathlib import Path
from typing import Literal

import click
from glom import GlomError, assign, delete, glom

from wap.commands.util import config_path_option
from wap.config import Config
from wap.console import print_out
from wap.exception import ConfigPathException, ConfigValueException


@click.command()
@config_path_option()
@click.option(
    "--get",
    "mode",
    flag_value="get",
    default=True,
    help="Print a value at PATH to stdout",
)
@click.option("--set", "mode", flag_value="set", help="Set the value at PATH to VALUE")
@click.option("--delete", "mode", flag_value="delete", help="Delete the value at PATH")
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help=(
        "With --get, if the value at PATH is a string, write it without quotes. With "
        "--set/--delete, read the VALUE as a string without quotes."
    ),
)
@click.argument("path")
@click.argument("value", required=False)
def config(
    path: str,
    value: str | None,
    config_path: Path,
    mode: Literal["get", "set", "delete"],
    raw: bool,
) -> None:
    """
    Get, set, or delete the JSON configuration value specified by PATH. Objects can be
    accessed by property names and arrays by their zero-based indexes, such as
    "package.0.path".

    All mutations (--set/--delete) will be validated before being written.

    Examples:

    \b
    Read the version without quotes:
        wap config --raw version

    \b
    Write a new version:
        wap config --set --raw version 1.2.3
    """
    config = Config.from_path(config_path)

    if mode == "get":
        try:
            value = glom(config.to_python_object(), path)
        except GlomError as glom_error:
            raise ConfigPathException(str(glom_error))
        if isinstance(value, str) and raw:
            print_out(value)
        else:
            print_out(json.dumps(value, indent=2))
    elif mode == "set":
        if not value:
            raise click.BadArgumentUsage("Must provide a value to set")
        if not raw:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ConfigValueException("Cannot decode value to JSON")
        try:
            config_obj = assign(config.to_python_object(), path, value)
        except GlomError as glom_error:
            raise ConfigPathException(str(glom_error))
        Config.from_python_object(config_obj).write_to_path(config_path, indent=True)
    elif mode == "delete":
        try:
            config_obj = delete(config.to_python_object(), path)
        except GlomError as glom_error:
            raise ConfigPathException(str(glom_error))
        Config.from_python_object(config_obj).write_to_path(config_path, indent=True)
