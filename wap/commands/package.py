import json
from pathlib import Path

import click

from wap import addon
from wap.commands.common import config_path_option, json_option, version_option
from wap.config import Config
from wap.util import delete_path


@click.command()
@config_path_option()
@version_option(help="The version you want to assign your package.")
@json_option()
def package(
    config_path: Path,
    version: str,
    show_json: bool,
) -> None:
    """
    Package your addons.

    For each wow-version specified in your config, create a package directory and
    zip file containing your addons in dist/ (relative to your current
    directory). The contents of the package directory and zip file will be the same as
    the addons directories you provide in your config plus the additional generated TOC
    file.

    The format of the name of the package directory will be
    "<package-name>-<version>-<wow-version-type>". It is the same for the zip
    file, except a ".zip" extension is added.

    Each TOC file generated will have the same name as the addon directory (plus the
    .toc extension). If this file exists in your source directory, it will be
    overrwritten.

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
            package_path = addon.package_addon(
                config_path=config_path,
                addon_name=config.name,
                dir_configs=config.addon_configs,
                version=version,
                wow_version=wow_version,
            )

            zip_path = addon.zip_addon(
                addon_name=config.name,
                wow_version=wow_version,
                version=version,
            )

        except BaseException:
            # catch any exception, keyboard interrupts included, and delete the
            # package path because it may be incomplete. this cleans up the package
            # and helps users not use broken packages in other commands
            package_path = addon.get_package_path(
                addon_name=config.name,
                version=version,
                wow_version=wow_version,
            )
            zip_path = addon.get_zip_path(
                addon_name=config.name,
                version=version,
                wow_version=wow_version,
            )

            for path in [package_path, zip_path]:
                if path.exists():
                    delete_path(path)

            # propogate up
            raise

        output_map[wow_version.type()] = {
            "package_dir_path": str(package_path),
            "zip_file_path": str(zip_path),
        }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))
