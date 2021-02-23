from functools import update_wrapper
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

import click


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

DEFAULT_CONFIG_PATH = Path(".wap.yml")
DEFAULT_OUTPUT_PATH = Path("dist")
DEFAULT_ADDON_VERSION = "dev"
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


def output_path_option() -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-o",
            "--output-path",
            type=PATH_TYPE,
            default=str(DEFAULT_OUTPUT_PATH),
            show_default=str(DEFAULT_OUTPUT_PATH),
            help="The output directory in which to create the build.",
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def addon_version_option(
    *, required: bool = False
) -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-v",
            "--addon-version",
            required=required,
            default=None if required else DEFAULT_ADDON_VERSION,
            show_default=not required,
            help="The developer-defined version of your addon package.",
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def json_option() -> Callable[[_DECORATED_FUNC_TYPE], _DECORATED_FUNC_TYPE]:
    def wrapper(func: _DECORATED_FUNC_TYPE) -> _DECORATED_FUNC_TYPE:
        decorated = click.option(
            "-j",
            "--json",
            "show_json",
            is_flag=True,
            default=False,
            help=(
                "Output json to stdout of the operations wap performed (so it can be "
                "written to files or piped to other programs)"
            ),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper
