from collections import ChainMap
from pathlib import Path, PurePosixPath, PureWindowsPath

import arrow

from wap import __version__, log
from wap.config import TocConfig
from wap.exception import TocException
from wap.wowversion import WoWVersion

# this list comes from some blizzard wow addon code.
# https://www.townlong-yak.com/framexml/37705/VideoOptionsPanels.lua#1230
_LANGUAGE_REGIONS = {
    "deDE",
    "enGB",
    "enUS",
    "esES",
    "frFR",
    "koKR",
    "zhCN",
    "zhTW",
    "enCN",
    "enTW",
    "esMX",
    "ruRU",
    "ptBR",
    "ptPT",
    "itIT",
}

# tag names from https://wowwiki-archive.fandom.com/wiki/TOC_format
_LOCALIZABLE_TAGS = {"Title", "Notes"}

_SECURE_TAG = "Secure"

_OFFICIAL_TAGS = {
    # add the localized tags like "Title-ptBR" or "Notes-esMX"
    *{f"{tag}-{lr}" for tag in _LOCALIZABLE_TAGS for lr in _LANGUAGE_REGIONS},
    # as well as the bare tags
    *_LOCALIZABLE_TAGS,
    "Interface",
    "Author",
    "Version",
    # according to docs, RequiredDeps and Dependencies have the same meaning
    "RequiredDeps",
    "Dependencies",
    "OptionalDeps",
    "LoadOnDemand",
    "LoadWith",
    "LoadManagers",
    "SavedVariables",
    "SavedVariablesPerCharacter",
    "DefaultState",
    _SECURE_TAG,
}

# we will warn about tags not in _OFFICIAL_TAGS that don't have the right prefix
_METADATA_TAG_PREFIX = "X-"

_MAX_TAG_LINE_LEN = 1023


def _create_tag_line(tag: str, value: str) -> str:
    tag_line = f"## {tag}: {value}"
    tag_line_len = len(tag_line)
    if tag_line_len > _MAX_TAG_LINE_LEN:
        log.warn(
            f'Line length for TOC tag "{tag}" ({tag_line_len}) exceeds '
            f"{_MAX_TAG_LINE_LEN}. Line will be truncated to that length (and may "
            "break your addon)."
        )
    return tag_line + "\n"


def _create_file_line(path: PurePosixPath) -> str:
    # TOC file use windows path separators
    windows_path = PureWindowsPath(path)

    return f"{windows_path}\n"


def write_toc(
    toc_config: TocConfig,
    dir_path: Path,
    write_path: Path,
    addon_version: str,
    wow_version: WoWVersion,
) -> None:
    for file in toc_config.files:
        rooted_file = write_path.parent / file
        if not rooted_file.is_file():
            raise TocException(
                f'TOC config lists file path "{file}", but it is not a file. This path '
                "must point to a file, must be relative to the path in the dir "
                f'config ("{dir_path.resolve()}") and, if it is in a subdirectory, '
                'must only use forward slashes ("/").'
            )

    extra_wap_tags = {
        "Interface": wow_version.interface_version(),
        "Version": addon_version,
        f"{_METADATA_TAG_PREFIX}BuildDateTime": arrow.utcnow().isoformat(),
        f"{_METADATA_TAG_PREFIX}BuildTool": f"wap v{__version__}",
    }

    tag_map = ChainMap(toc_config.tags, extra_wap_tags)

    for tag, value in extra_wap_tags.items():
        if tag in toc_config.tags:
            log.warn(
                f'Overwriting wap-provided tag "{tag}"="{value}" with '
                f"{toc_config.tags[tag]}"
            )

    for tag, value in toc_config.tags.items():
        if tag not in _OFFICIAL_TAGS and not tag.startswith(_METADATA_TAG_PREFIX):
            log.warn(
                f'TOC user-specified tag "{tag}" does not have '
                f'"{_METADATA_TAG_PREFIX}" prefix'
            )

    if _SECURE_TAG in toc_config.tags.keys() and toc_config.tags[_SECURE_TAG] == "1":
        log.warn(
            f"{_SECURE_TAG} found with value equal to 1. Only Blizzard-signed addons "
            "can use the functionality of this setting. "
        )

    lines = [
        *[_create_tag_line(tag, value) for tag, value in tag_map.items()],
        "\n",
        *[_create_file_line(file) for file in toc_config.files],
    ]

    with write_path.open("w") as toc_file:
        for line in lines:
            toc_file.write(line)
