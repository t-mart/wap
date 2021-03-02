from functools import update_wrapper
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

import click

from wap.wowversion import WoWVersion


class PathType(click.ParamType):
    name = "PATH"

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Path:
        return Path(value)


PATH_TYPE = PathType()

VERSION_STRING_TEMPLATE = "wap, version %(version)s"

OUTPUT_PATH = Path("dist")

DEFAULT_CONFIG_PATH = Path(".wap.yml")
DEFAULT_PROJECT_VERSION = "dev"
DEFAULT_RELEASE_TYPE = "alpha"

WAP_CURSEFORGE_TOKEN_ENVVAR_NAME = "WAP_CURSEFORGE_TOKEN"
WAP_CONFIG_PATH_ENVVAR_NAME = "WAP_CONFIG_PATH"
WAP_WOW_ADDONS_PATH_ENVVAR_NAME = "WAP_WOW_ADDONS_PATH"

_DECORATED_FUNC_TYPE = TypeVar("_DECORATED_FUNC_TYPE", bound=Callable[..., Any])


def config_path_option() -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-c",
            "--config-path",
            type=PATH_TYPE,
            default=str(DEFAULT_CONFIG_PATH),
            envvar=WAP_CONFIG_PATH_ENVVAR_NAME,
            show_default=str(DEFAULT_CONFIG_PATH),
            help=(
                "The path of the configuration file. May also be specified in the "
                "environment variable WAP_CONFIG_PATH."
            ),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def version_option(
    *, help: str, required: bool = False
) -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-v",
            "--version",
            required=required,
            default=None if required else DEFAULT_PROJECT_VERSION,
            show_default=not required,
            help=help,
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def json_option(
    *, help: Optional[str] = None
) -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    if help is None:
        help = (
            "Output json to stdout of the operations wap performed (so it can be "
            "written to files or piped to other programs)"
        )

    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-j",
            "--json",
            "show_json",
            is_flag=True,
            default=False,
            help=help,
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def wow_addons_path_option() -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-w",
            "--wow-addons-path",
            envvar=WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
            required=True,
            type=WOW_ADDONS_PATH_TYPE,
            help=(
                "Your WoW addons path. May also be specified in the environment "
                "variable WAP_WOW_ADDONS_PATH."
            ),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


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
            self.fail(f'WoW AddOns path "{value}" is not a directory', param, ctx)

        not_addons_dir_exc_str = (
            f'WoW AddOns path "{path}" does not look like a WoW addons directory'
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
