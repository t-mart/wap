import json
from pathlib import Path
from typing import Optional

import click

from wap import addon
from wap.commands.common import (
    WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
    addon_version_option,
    config_path_option,
    json_option,
)
from wap.config import Config
from wap.exception import DevInstallException
from wap.util import DEFAULT_DARWIN_WOW_ADDONS_PATH, DEFAULT_WIN32_WOW_ADDONS_PATH
from wap.wowversion import WoWVersion


class WowAddonsPathType(click.ParamType):
    name = "WOW_ADDONS_PATH"

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Path:
        path = Path(value)
        if not path.is_dir():
            self.fail(f"WoW AddOns path {value} is not a directory", param, ctx)

        not_addons_dir_exc_str = (
            f"WoW AddOns path {path} does not look like a WoW addons directory"
        )

        try:
            *_, wow_part, type_part, interface_part, addons_part = path.parts
        except ValueError:
            self.fail(not_addons_dir_exc_str, param, ctx)

        if (
            wow_part != "World of Warcraft"
            or interface_part != "Interface"
            or addons_part != "AddOns"
        ):
            self.fail(not_addons_dir_exc_str, param, ctx)

        if type_part not in WoWVersion.ADDONS_PATH_TYPE_MAP.keys():
            self.fail(not_addons_dir_exc_str, param, ctx)

        return path


WOW_ADDONS_PATH_TYPE = WowAddonsPathType()


@click.command()
@config_path_option()
@addon_version_option()
@json_option()
@click.option(
    "-w",
    "--wow-addons-path",
    envvar=WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
    required=True,
    type=WOW_ADDONS_PATH_TYPE,
    help=(
        "Your WoW addons path. May also be specified in the environment variable "
        "WAP_WOW_ADDONS_PATH."
    ),
)
def dev_install(
    config_path: Path,
    addon_version: str,
    wow_addons_path: Path,
    show_json: bool,
) -> None:
    f"""
    Install a built addon to the provided WoW addons directory. (wap build must have
    been run before this.)

    This command assists you in testing your addons quickly.

    wap is smart in determining which addon build to install (retail or classic). It
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

    For example, "{DEFAULT_WIN32_WOW_ADDONS_PATH}" (Windows) or
    "{DEFAULT_DARWIN_WOW_ADDONS_PATH}" (macOS) are acceptable.

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
            f'No build exists for WoW addons path "{wow_addons_path}" (which is a '
            f"{wow_addons_path_type} installation). "
        )

    output_map = {}

    dev_install_paths = addon.dev_install_addon(
        wow_addons_path=wow_addons_path,
        addon_name=config.name,
        addon_version=addon_version,
        wow_version=wow_version,
    )

    output_map[wow_version.type()] = {
        "installed_dir_paths": [str(path) for path in dev_install_paths],
    }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))
