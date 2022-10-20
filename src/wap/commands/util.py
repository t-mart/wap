from collections.abc import Callable
from functools import update_wrapper
from pathlib import Path
from typing import Literal, ParamSpec, TypeVar

import click

from wap.wow import FLAVORS, get_default_addons_path

DEFAULT_OUTPUT_PATH = Path("dist")
DEFAULT_CONFIG_PATH = Path("wap.json")
DISCOVER_SENTINEL = object()

P = ParamSpec("P")
T = TypeVar("T")


class DiscoveredConfigPath(click.ParamType):
    # this gives is git-like discovery of the wap.json file, where this directory and
    # its parents are searched until wap.json is found. if it is not found, fail.

    # CAREFUL when testing this on a real filesystem that may have a wap.json somewhere
    # the in the test's directory heirarchy.
    name = "file"

    def convert(
        self,
        value: str | Literal[False],
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Path:
        if value:
            path = Path(value)
            if not path.is_file():
                self.fail(f"{value} is not a file path", param, ctx)
            return path

        cwd = Path().resolve()

        for parent in [cwd, *cwd.parents]:
            config_path = parent / DEFAULT_CONFIG_PATH
            if config_path.is_file():
                return config_path

        self.fail(
            f'could not find config file "{DEFAULT_CONFIG_PATH}" here or in any parent '
            "directories",
            param,
            ctx,
        )


def config_path_option() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = click.option(
            "-c",
            "--config-path",
            type=DiscoveredConfigPath(),
            default=False,
            show_default=f"{DEFAULT_CONFIG_PATH} in this or a parent directory",
            help=("The path to the configuration file."),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def output_path_option() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = click.option(
            "-o",
            "--output-path",
            default=None,
            show_default=f"{DEFAULT_OUTPUT_PATH} directory where config is located",
            type=click.Path(file_okay=False, path_type=Path),
            help=("Root directory path for built packages."),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def clean_option() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = click.option(
            "--clean",
            is_flag=True,
            help=(
                "Clean addon directories of files and subdirectories before packaging."
            ),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def wow_addons_dir_options() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = func
        for flavor in FLAVORS:
            decorated = click.option(
                f"--{flavor.name}-addons-path",
                type=click.Path(file_okay=False, path_type=Path),
                default=get_default_addons_path(flavor),
                help=(
                    f"Path to the AddOns folder of your {flavor.canon_name} "
                    "installation"
                ),
                show_default=True,
            )(decorated)

        return update_wrapper(decorated, func)

    return wrapper
