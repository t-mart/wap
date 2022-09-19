from collections.abc import Callable
from functools import update_wrapper
from pathlib import Path
from typing import ParamSpec, TypeVar

import click

from wap.wow import FLAVORS, get_default_addons_path

DEFAULT_OUTPUT_PATH = Path("./dist")
DEFAULT_CONFIG_PATH = Path("./wap.json")

P = ParamSpec("P")
T = TypeVar("T")


def config_path_option() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = click.option(
            "-c",
            "--config-path",
            type=click.Path(dir_okay=False, exists=True, path_type=Path),
            default=str(DEFAULT_CONFIG_PATH),
            show_default=True,
            help=("The path to the configuration file."),
        )(func)

        return update_wrapper(decorated, func)

    return wrapper


def output_path_option() -> Callable[[Callable[P, T]], Callable[P, T]]:
    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        decorated = click.option(
            "-o",
            "--output-path",
            default=DEFAULT_OUTPUT_PATH,
            type=click.Path(file_okay=False, path_type=Path),
            help=("Path to output package artifacts."),
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
