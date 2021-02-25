from collections import ChainMap
from pathlib import Path, PureWindowsPath

import arrow

from wap import __version__, log
from wap.config import TocConfig
from wap.exception import TocException
from wap.wowversion import WoWVersion

# tag names from https://wowwiki-archive.fandom.com/wiki/TOC_format
_OFFICIAL_TAGS = {
    "Interface",
    "Title",
    "Author",
    "Version",
    "Notes",
    "RequiredDeps",  # according to docs, this and the next have the same meaning to wow
    "Dependencies",
    "OptionalDeps",
    "LoadOnDemand",
    "LoadWith",
    "LoadManagers",
    "SavedVariables",
    "DefaultState",
    "Secure",
}

# we will warn about tags not in _OFFICIAL_TAGS that don't have the right prefix
_METADATA_TAG_PREFIX = "X-"


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

    for key, value in extra_wap_tags.items():
        if key in toc_config.tags:
            log.warn(
                f"Overwriting wap-provided tag {key}={value} with "
                "{toc_config.tags[key]}"
            )

    for key, value in toc_config.tags.items():
        if key not in _OFFICIAL_TAGS and not key.startswith(_METADATA_TAG_PREFIX):
            log.warn(
                f"TOC user-specified tag {key} does not have "
                f"{_METADATA_TAG_PREFIX} prefix"
            )

    # TOC file use windows path separators
    windows_files = [PureWindowsPath(f) for f in toc_config.files]

    lines = [
        *[f"## {key}: {value}\n" for key, value in tag_map.items()],
        "\n",
        *[f"{str(file)}\n" for file in windows_files],
    ]

    with write_path.open("w") as toc_file:
        for line in lines:
            toc_file.write(line)
