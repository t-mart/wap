import json
from pathlib import Path

import click

from wap import addon
from wap.commands.common import addon_version_option, config_path_option, json_option
from wap.config import Config
from wap.util import delete_path


@click.command()
@config_path_option()
@addon_version_option()
@json_option()
def build(
    config_path: Path,
    addon_version: str,
    show_json: bool,
) -> None:
    """
    Build your addon.

    For each wow-version specified in your config, create a build directory and zip file
    containing your packaged addon in the dist/ directory (relative to your current
    directory). The contents of the build directory and zip file will be the same as the
    dirs you provide in your config and an additional generated TOC file.

    The format of the name of the build directory will be
    "<addon-name>-<addon-version>-<wow-version-type>". It is the same for the zip file,
    except a ".zip" extension is added.

    Each TOC file generated
    will have the same name as the directory (plus the .toc extension). If this file
    exists in your source directory, it will be overrwritten.

    The contents of the TOC file will be those as specified in your toc tags and toc
    files.

    Unless they are overriden in your config, the tags "Interface" and "Version" in the
    generated TOC will correspond to the WoW version and addon version being built,
    respectively. wap also adds "X-BuildDateTime" and "X-BuildTool" tags with
    appropriate values.
    """
    config = Config.from_path(config_path)

    output_map = {}

    for wow_version in config.wow_versions:
        try:
            build_path = addon.build_addon(
                config_path=config_path,
                addon_name=config.name,
                dir_configs=config.dir_configs,
                addon_version=addon_version,
                wow_version=wow_version,
            )

            zip_path = addon.zip_addon(
                addon_name=config.name,
                wow_version=wow_version,
                addon_version=addon_version,
            )

        except BaseException:
            # catch any exception, keyboard interrupts included, and delete the
            # build path because it may be incomplete. this cleans up the build
            # and helps users not use broken builds in other commands
            build_path = addon.get_build_path(
                addon_name=config.name,
                addon_version=addon_version,
                wow_version=wow_version,
            )
            zip_path = addon.get_zip_path(
                addon_name=config.name,
                addon_version=addon_version,
                wow_version=wow_version,
            )

            for path in [build_path, zip_path]:
                if path.exists():
                    delete_path(path)

            # propogate up
            raise

        output_map[wow_version.type()] = {
            "build_dir_path": str(build_path),
            "zip_file_path": str(zip_path),
        }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))
