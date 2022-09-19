from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import ClassVar

import arrow
from attr import frozen

from wap import __version__
from wap.config import TocConfig
from wap.exception import PathMissingException
from wap.wow import Version

# this list comes from some blizzard wow addon code.
# https://www.townlong-yak.com/framexml/beta/VideoOptionsPanels.lua#1270
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
_BARE_LOCALIZABLE_TAGS = {"Title", "Notes"}
_LOCALIZED_TAGS = {
    f"{tag}-{lr}" for tag in _BARE_LOCALIZABLE_TAGS for lr in _LANGUAGE_REGIONS
}
_SECURE_TAG = "Secure"

_OFFICIAL_TAGS = {
    *_BARE_LOCALIZABLE_TAGS,
    *_LOCALIZED_TAGS,
    "Interface",
    "Author",
    "Version",
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


@frozen
class Toc:
    tags: Sequence[tuple[str, str]]
    files: Sequence[str]
    suffix: str

    _TAG_LINE_PREFIX: ClassVar[str] = "##"
    _COMMENT_LINE_PREFIX: ClassVar[str] = "#"

    @classmethod
    def parse(cls, contents: str, suffix: str) -> Toc:
        tags = []
        files = []

        for line in contents.splitlines():
            if line and not line.startswith(cls._COMMENT_LINE_PREFIX):
                files.append(line)

            elif line.startswith(cls._TAG_LINE_PREFIX):
                name, value = [
                    token.strip()
                    for token in line.removeprefix("##").split(sep=":", maxsplit=1)
                ]
                tags.append((name, value))

        return cls(tags=tags, files=files, suffix=suffix)

    @classmethod
    def from_toc_config(
        cls,
        toc_config: TocConfig,
        wow_version: Version,
        addon_version: str,
        suffix: str,
    ) -> Toc:

        extra_wap_tags = {
            "Interface": wow_version.interface_version,
            "Version": addon_version,
            f"{_METADATA_TAG_PREFIX}BuildDateTime": arrow.utcnow().isoformat(),
            f"{_METADATA_TAG_PREFIX}BuildTool": f"wap {__version__}",
        }

        merged_tags = toc_config.serialized_tags | extra_wap_tags

        # sort the tags, for Title and Notes
        # TOC parsing logic is that, for a given user locale "xxXX" and tag name "Tag"
        # in {"Title", "Notes"}, the realized value will the LAST declaration of "Tag"
        # or "Tag-xxXX" in the TOC file. If neither are present, the realized value will
        # be the game client's default value. For "Title", the default is the name of
        # the directory, and for "Notes", the default is an empty string.
        # Since locale tags are probably more applicable, we want them last.
        tag_pairs = list(merged_tags.items())
        tag_pairs.sort(key=lambda kv: 1 if kv[0] in _LOCALIZED_TAGS else 0)

        return cls(tags=tag_pairs, files=toc_config.files, suffix=suffix)

    @property
    def tag_map(self) -> Mapping[str, str]:
        return dict(self.tags)

    def validate(self, source_dir: Path) -> None:
        # Commented below because schema disallows unknown tags
        # tag_map = self.tag_map
        # for name in tag_map:
        #     if name not in _OFFICIAL_TAGS and not name.startswith(
        #         _METADATA_TAG_PREFIX
        #     ):
        #         log.warn(
        #             f"Unknown tag {name} does not start with {_METADATA_TAG_PREFIX}. "
        #             "Maybe misspelling?"
        #         )

        # if _SECURE_TAG in tag_map.keys():
        #     log.warn(f"Found {_SECURE_TAG} tag in user addon.")

        for file_path in self.files:
            joined_path = source_dir / file_path
            if not joined_path.is_file():
                raise PathMissingException(f"Path {joined_path} at does not exist.")

    @classmethod
    def _create_tag_line(cls, key: str, value: str) -> str:
        return f"{cls._TAG_LINE_PREFIX} {key}: {value}"

    @staticmethod
    def _create_file_line(path: str) -> str:
        # TOC file use windows path separators
        windows_path = PureWindowsPath(path)
        return f"{windows_path}"

    def filename(self, addon_name: str) -> str:
        return f"{addon_name}{self.suffix}.toc"

    def generate(self) -> str:
        return "\n".join(
            (
                *(self._create_tag_line(key, value) for key, value in self.tags),
                "",
                *(self._create_file_line(files) for files in self.files),
            )
        )
