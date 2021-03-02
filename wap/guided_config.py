import re
from pathlib import PurePosixPath
from typing import Any, Optional, Pattern, cast

import click

from wap import log
from wap.config import AddonConfig, Config, CurseforgeConfig, TocConfig
from wap.wowversion import LATEST_CLASSIC_VERSION, LATEST_RETAIL_VERSION

DEFAULT_CHANGELOG_PATH = PurePosixPath("CHANGELOG.md")


def _prompt_until_matching(
    pattern: Pattern[str],
    text: str,
    default: Optional[str] = None,
    **prompt_kwargs: Any,
) -> re.Match[str]:
    text = click.style(text, fg="blue")
    if default is not None:
        text += " [" + click.style(default, fg="green") + "]"
    while True:
        value = cast(
            str,
            click.prompt(
                text, default=default, show_default=False, err=True, **prompt_kwargs
            ),
        )
        if (match := pattern.match(value)) is not None:
            return match
        log.info(f'Value "{value}" does not match pattern: {pattern.pattern}')


def _prompt_yes_no(text: str, **prompt_kwargs: Any) -> bool:
    yes_no_pattern = re.compile(r"^(y|(?:yes)|n|(?:no))$", flags=re.IGNORECASE)
    text = (
        click.style(text, fg="blue")
        + " <"
        + click.style("yes", fg="magenta")
        + "|"
        + click.style("y", fg="magenta")
        + "|"
        + click.style("no", fg="magenta")
        + "|"
        + click.style("n", fg="magenta")
        + ">"
    )
    while True:
        value = cast(str, click.prompt(text=text, err=True, **prompt_kwargs))
        if (match := yes_no_pattern.match(value)) is not None:
            return "y" in match[0].lower()
        log.info(f'Value "{value}" does not match pattern: {yes_no_pattern.pattern}')


def guide(project_dir_name: str) -> Config:
    addon_name_pattern = re.compile(r"\S+")
    author_pattern = re.compile(r".+")
    notes_pattern = re.compile(r".+")
    project_id_pattern = re.compile(r"\d+")
    curseforge_url_pattern = re.compile(
        r"https:\/\/www\.curseforge\.com\/wow\/addons\/(?P<addon_name>\S+)"
    )

    log.info(
        "This command will guide you through creating your "
        + click.style(".wap.yml", fg="blue")
        + " config.\n",
    )

    # addon name
    name = _prompt_until_matching(
        addon_name_pattern,
        text="Addon name",
        default=project_dir_name,
    )[0]

    # author for TOC
    author = _prompt_until_matching(
        author_pattern,
        text="Author name",
    )[0]

    # notes for TOC
    notes = _prompt_until_matching(
        notes_pattern,
        text="Addon description",
    )[0]

    toc_config = TocConfig(
        tags={"Title": name, "Author": author, "Notes": notes},
        files=[PurePosixPath("Init.lua")],
    )

    addon_configs = [AddonConfig(path=PurePosixPath(name), toc_config=toc_config)]

    # wow versions supported
    wow_versions = []

    if _prompt_yes_no(text="Will this addon support retail WoW?"):
        wow_versions.append(LATEST_RETAIL_VERSION)
        if _prompt_yes_no(text="Will this addon support classic WoW?"):
            wow_versions.append(LATEST_CLASSIC_VERSION)
    else:
        wow_versions.append(LATEST_CLASSIC_VERSION)
        log.info("If not supporting retail, must be supporting classic")

    # curseforge
    curseforge_config = None
    if _prompt_yes_no(text="Do you have a CurseForge project?"):

        project_id = _prompt_until_matching(
            project_id_pattern,
            text="CurseForge project id (found in top-right of addon page)",
        )[0]

        project_slug = _prompt_until_matching(
            curseforge_url_pattern,
            text="CurseForge URL",
        )["addon_name"]

        curseforge_config = CurseforgeConfig(
            project_id=project_id,
            changelog_path=DEFAULT_CHANGELOG_PATH,
            project_slug=project_slug,
        )

    return Config(
        name=name,
        addon_configs=addon_configs,
        wow_versions=wow_versions,
        curseforge_config=curseforge_config,
    )
