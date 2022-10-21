import getpass
import re
import textwrap
from pathlib import Path
from typing import Literal

from rich.panel import Panel

from wap.config import AddonConfig, Config, CurseforgeConfig, PublishConfig, TocConfig
from wap.console import confirm_ask, print, print_json, prompt_ask
from wap.exception import AbortError
from wap.wow import FLAVORS, Flavor

_CURSEFORGE_CREATE_PROJECT_LINK = "https://www.curseforge.com/project/1/1/create"


def get_package_name_new_project() -> str:
    while True:
        package_name = prompt_ask("\nPackage name")
        if package_name == "":
            print("[prompta]No package name given. You must provide a package name.")
        elif (Path() / package_name).exists():
            print(
                "[prompta]Package name conflicts with existing file name. Choose "
                "another name."
            )
        else:
            return package_name


def get_package_name_new_config() -> str:
    while True:
        package_name = prompt_ask("\nPackage name")
        if package_name == "":
            print("[prompta]No package name given. You must provide a package name.")
        else:
            return package_name


def get_author() -> str:
    return prompt_ask("\nAuthor", default=getpass.getuser())


def get_desc() -> str:
    return prompt_ask("\nDescription")


def get_version() -> str:
    return prompt_ask("\nVersion", default="0.0.1")


def get_supported_flavors() -> list[Flavor]:
    supported_flavors: list[Flavor] = []
    while True:
        for flavor in FLAVORS:
            if confirm_ask(f"\nSupport {flavor.canon_name}"):
                supported_flavors.append(flavor)
        if supported_flavors:
            return supported_flavors
        print("[prompta]No flavors chosen. You must support at least one flavor.")


def get_project_id() -> str:
    print(
        "\n[hint]If you do not yet have a project, create one at "
        f"[link]{_CURSEFORGE_CREATE_PROJECT_LINK}"
    )
    while True:
        project_id = prompt_ask("Curseforge project ID")
        if not re.fullmatch(r"\d+", project_id):
            print("[prompta]Invalid project ID. It must be a number.")
            continue
        return project_id


def get_project_slug() -> str | None:
    # https://www.curseforge.com/wow/addons/details
    print(
        "\n[hint]Your project slug is in your project's URL. For example, if the URL "
        'is "https://www.curseforge.com/wow/addons/my-addon", then the slug is '
        '"my-addon".'
    )
    return prompt_ask("Curseforge project slug (Press enter to skip)", default=None)


def confirm_publish() -> bool:
    return confirm_ask("\nWill you want to publish to Curseforge?")


def get_publish_config() -> PublishConfig | None:
    if not confirm_publish():
        return None

    project_id = get_project_id()
    project_slug = get_project_slug()

    return PublishConfig(
        curseforge=CurseforgeConfig(
            project_id=project_id,
            slug=project_slug,
            changelog_text="",
        )
    )


def confirm_all_ok() -> bool:
    return confirm_ask("\nIs this OK")


def prompt_for_config(mode: Literal["new-project", "new-config"]) -> Config:
    intro = """\
    These questions will walk you through creating a new wap configuration file.

    It will cover only the most basic settings, and you should edit it later.

    See `[command]wap help[/command]` for more detailed documentation.

    Press [key]Ctrl-C[/key] at any time to quit.\
    """

    print(
        Panel.fit(textwrap.dedent(intro), title=f"wap {mode}", padding=(1, 2), width=80)
    )

    if mode == "new-config":
        package_name = get_package_name_new_config()
    elif mode == "new-project":
        package_name = get_package_name_new_project()

    author = get_author()
    desc = get_desc()
    version = get_version()
    supported_flavors = get_supported_flavors()
    publish_config = get_publish_config()

    config = Config(
        name=package_name,
        version=version,
        author=author,
        wow_versions={
            flavor.name: flavor.latest_version.dotted for flavor in supported_flavors
        },
        publish=publish_config,
        package=[
            AddonConfig(
                path=f"./{package_name}",
                toc=TocConfig(
                    tags={
                        "Title": package_name,
                        "Notes": desc,
                    },
                    files=["Main.lua"],
                ),
            )
        ],
    )

    # i like this for learning reasons. it maps the previous questions to a real config
    print_json(config.to_json())
    if confirm_all_ok():
        return config

    raise AbortError("Aborted!")
