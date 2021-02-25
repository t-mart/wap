import json
from pathlib import Path
from typing import Optional

import click

from wap import addon, log
from wap.commands.common import (
    WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
    addon_version_option,
    config_path_option,
    json_option,
)
from wap.config import Config
from wap.exception import DevInstallException
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
        'Your WoW addons path, such as "/path/to/WoW/Interface/Addons". May also be '
        "specified in the environment variable WAP_WOW_ADDONS_PATH."
    ),
)
def dev_install(
    config_path: Path,
    addon_version: str,
    wow_addons_path: Path,
    show_json: bool,
) -> int:
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

    build_path = addon.get_build_path(
        addon_name=config.name,
        wow_version=wow_version,
        addon_version=addon_version,
    )

    if not build_path.is_dir():
        log.error(
            "Expected build directory not found. Have you run `"
            + click.style(f"wap build --addon-version {addon_version}", fg="blue")
            + "` yet?"
        )
        raise DevInstallException(f'Build directory "{build_path}" not found.')

    dev_install_paths = addon.dev_install_addon(
        build_path=build_path,
        wow_addons_path=wow_addons_path,
        wow_version=wow_version,
    )

    output_map[wow_version.type()] = {
        "installed_dir_paths": [str(path) for path in dev_install_paths],
    }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))

    return 0
