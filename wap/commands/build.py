import json
from pathlib import Path

import click

from wap import addon
from wap.commands.common import (
    addon_version_option,
    config_path_option,
    json_option,
    output_path_option,
)
from wap.config import Config


@click.command()
@config_path_option()
@output_path_option()
@addon_version_option()
@json_option()
def build(
    config_path: Path,
    output_path: Path,
    addon_version: str,
    show_json: bool,
) -> None:
    """
    Builds packages, creating a directory with your packaged addon and a zip archive.
    Outputs a JSON object describing the locations of the built files.
    """
    config = Config.from_path(config_path)

    output_map = {}

    for wow_version in config.wow_versions:
        build_path = addon.build_addon(
            config_path=config_path,
            addon_name=config.name,
            dir_configs=config.dir_configs,
            output_path=output_path,
            addon_version=addon_version,
            wow_version=wow_version,
        )

        zip_path = addon.zip_addon(
            addon_name=config.name,
            wow_version=wow_version,
            build_path=build_path,
        )

        output_map[wow_version.type()] = {
            "build_dir_path": str(build_path),
            "zip_file_path": str(zip_path),
        }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))
