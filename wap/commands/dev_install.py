import json
from pathlib import Path
from typing import Optional

import click

from wap import addon
from wap.commands.common import (
    config_path_option,
    json_option,
    version_option,
    wow_addons_path_option,
)
from wap.config import Config
from wap.exception import DevInstallException
from wap.wowversion import WoWVersion


@click.command()
@config_path_option()
@version_option(help="The version of a previously built package")
@json_option()
@wow_addons_path_option()
def dev_install(
    config_path: Path,
    version: str,
    wow_addons_path: Path,
    show_json: bool,
) -> None:
    """Install an addon package to the provided WoW addons directory. (wap package must
    have been run before this.)

    This command assists you in testing your addons quickly.

    wap is smart in determining which package to install (retail or classic). It
    looks at the components of the WoW addons directory path provided and chooses the
    appropriate one.

    The provided WoW addons directory must appear to be valid, or else wap will not
    perform the installation. This is to avoid data loss in unintended directories.
    The actual logic for this is to inspect the path components of the directory
    provided, which must end with the following in order:

        1. "World of Warcraft"

        2. either "_retail_" or "_classic_"

        3. "Interface"

        4. "AddOns"

    For example,

    "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Interface\\AddOns" (Windows)

    or

    "/Applications/World of Warcraft/_retail_/Interface/AddOns" (macOS)

    are acceptable.

    If your addon's directories already exist in the WoW addons directory, they will
    first be deleted to ensure a clean install. Keep this in mind if you have somehow
    put important data in that directory.
    """
    config = Config.from_path(config_path)

    wow_addons_path_type = WoWVersion.addons_path_type(wow_addons_path.parts[-3])

    wow_version: Optional[WoWVersion] = None
    for wow_version_in_config in config.wow_versions:
        if wow_version_in_config.type() == wow_addons_path_type:
            wow_version = wow_version_in_config
            break
    else:
        raise DevInstallException(
            f'No package exists for WoW addons path "{wow_addons_path}" (which is a '
            f"{wow_addons_path_type} installation). "
        )

    output_map = {}

    dev_install_paths = addon.dev_install_addon(
        wow_addons_path=wow_addons_path,
        addon_name=config.name,
        version=version,
        wow_version=wow_version,
    )

    output_map[wow_version.type()] = {
        "installed_dir_paths": [str(path) for path in dev_install_paths],
    }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))
