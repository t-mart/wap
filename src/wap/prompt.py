import getpass
from pathlib import Path
from typing import Literal

from rich.prompt import Confirm, Prompt

from wap.config import AddonConfig, Config, TocConfig
from wap.console import STDERR_CONSOLE, info
from wap.wow import FLAVORS, Flavor


def get_package_name_new_project() -> str:
    while True:
        package_name = Prompt.ask("Package name", console=STDERR_CONSOLE)
        if not (Path() / package_name).exists():
            return package_name
        info("Cannot be the name of an existing file")


def get_package_name_new_config() -> str:
    return Prompt.ask("Package name", default=Path.cwd().name, console=STDERR_CONSOLE)


def get_author() -> str:
    return Prompt.ask("Author", default=getpass.getuser(), console=STDERR_CONSOLE)


def get_desc() -> str:
    return Prompt.ask("Description", console=STDERR_CONSOLE)


def get_version() -> str:
    return Prompt.ask("Version", console=STDERR_CONSOLE)


def get_supported_flavors() -> list[Flavor]:
    supported_flavors: list[Flavor] = []
    while True:
        for flavor in FLAVORS:
            if Confirm.ask(f"Support {flavor.canon_name}", console=STDERR_CONSOLE):
                supported_flavors.append(flavor)
        if supported_flavors:
            return supported_flavors
        info("You must support at least one flavor")


def prompt_for_config(mode: Literal["new-project", "new-config"]) -> Config:
    intro = """\
    These questions will walk you through creating a new wap configuration file.

    It will cover only the most basic settings, and you should edit it later.

    See `wap help` for more detailed documentation.

    Press Ctrl-C at any time to quit.
    """

    info(intro, dedent=True)

    if mode == "new-config":
        package_name = get_package_name_new_config()
    elif mode == "new-project":
        package_name = get_package_name_new_project()

    author = get_author()
    desc = get_desc()
    version = get_version()
    supported_flavors = get_supported_flavors()

    return Config(
        name=package_name,
        version=version,
        wow_versions={
            flavor.name: flavor.latest_version.dotted for flavor in supported_flavors
        },
        package=[
            AddonConfig(
                path=f"./{package_name}",
                toc=TocConfig(
                    tags={
                        "Title": package_name,
                        "Author": author,
                        "Notes": desc,
                    },
                    files=["Main.lua"],
                ),
            )
        ],
    )
