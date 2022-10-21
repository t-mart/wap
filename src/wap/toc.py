from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import ClassVar

import arrow
from attrs import frozen

from wap import __version__
from wap.config import Config, TocConfig
from wap.exception import PathMissingError, TagError
from wap.wow import Version

# Just some notes about TOC files I found
# - Folder name must match toc prefix. E.g. Foo/Foo.toc, but not Foo/Bar.toc
# - Title not required. If not, addon list shows folder name
# - Localizable tags logic:
#   - For a given player with a given locale named `<locale>`, that player can match
#     to both `Title-<locale>` and `Title` (same for notes). Which one is chosen is
#     based on ordering: last always wins.
#   - Official tag names are case insensitive EXCEPT for locales
#   - Presumably, only Title and Notes may be localized
# - If no Notes are given, title is used
# - Files are optional (but we will require them in our config file)
# - Tags are optional (ditto)
# - Tags do not require values (default to empty string)

# this list comes from some blizzard wow addon code.
# https://www.townlong-yak.com/framexml/beta/VideoOptionsPanels.lua#1270
_LANGUAGE_REGIONS = {
    "deDE",
    "enCN",
    "enGB",
    "enTW",
    "enUS",
    "esES",
    "esMX",
    "frFR",
    "itIT",
    "koKR",
    "ptBR",
    "ptPT",
    "ruRU",
    "zhCN",
    "zhTW",
}

# tag names from https://wowwiki-archive.fandom.com/wiki/TOC_format
_BARE_LOCALIZABLE_TAGS = {"Title", "Notes"}
_LOCALIZED_TAGS = {
    f"{tag}-{lr}" for tag in _BARE_LOCALIZABLE_TAGS for lr in _LANGUAGE_REGIONS
}
_METADATA_TAG_PREFIX = "X-"


@frozen
class Toc:
    tags: Sequence[tuple[str, str]]
    files: Sequence[str]
    flavor_suffix: str | None

    _TAG_LINE_PREFIX: ClassVar[str] = "##"
    _COMMENT_LINE_PREFIX: ClassVar[str] = "#"

    @classmethod
    def parse(cls, contents: str, flavor_suffix: str) -> Toc:
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

        return cls(tags=tags, files=files, flavor_suffix=flavor_suffix)

    @classmethod
    def from_toc_config(
        cls,
        toc_config: TocConfig,
        source_path: Path,
        config: Config,
        wow_version: Version,
        flavor_suffix: str | None = None,
    ) -> Toc:
        default_tags = {}
        if config.author is not None:
            default_tags["Author"] = config.author
        if config.description is not None:
            default_tags["Description"] = config.description
        default_tags["Title"] = source_path.name
        default_tags["Version"] = config.version
        default_tags["Interface"] = wow_version.interface_version
        default_tags[
            f"{_METADATA_TAG_PREFIX}BuildDateTime"
        ] = arrow.utcnow().isoformat()
        default_tags[f"{_METADATA_TAG_PREFIX}BuildTool"] = f"wap {__version__}"

        # all default tags are overrideable
        merged_tags = default_tags | toc_config.serialized_tags

        # sort the tags, for Title and Notes
        # TOC parsing logic is that, for a given user locale "xxXX" and tag name "Tag"
        # in {"Title", "Notes"}, the realized value will the LAST declaration of "Tag"
        # or "Tag-xxXX" in the TOC file. If neither are present, the realized value will
        # be the game client's default value. For "Title", the default is the name of
        # the directory, and for "Notes", the default is an empty string.
        # Since locale tags are probably more applicable, we want them last.
        tag_pairs = list(merged_tags.items())
        # this sort should only reorder localized tags. everything else should be in
        # config order (insertion order) because this python sort is stable.
        tag_pairs.sort(key=lambda kv: 1 if kv[0] in _LOCALIZED_TAGS else 0)

        return cls(tags=tag_pairs, files=toc_config.files, flavor_suffix=flavor_suffix)

    @property
    def tag_map(self) -> Mapping[str, str]:
        return dict(self.tags)

    def validate(self, source_dir: Path) -> None:
        """
        Check various things about a toc, including testing that the paths in the files
        list actually exist in source_dir
        """
        illegal_tag_chars = ["\n", " ", ":"]
        for tag in self.tag_map:
            for ill_char in illegal_tag_chars:
                if ill_char in tag:
                    raise TagError(
                        f'Tag {tag} contains illegal character "{ill_char!r}". Please '
                        "remove it and try again"
                    )
        for file_path in self.files:
            joined_path = source_dir / file_path
            if not joined_path.is_file():
                raise PathMissingError(
                    f"TOC file path {joined_path} does not exist. Please fix the path "
                    "in your configuration file or remove it."
                )

    @classmethod
    def _create_tag_line(cls, key: str, value: str) -> str:
        return f"{cls._TAG_LINE_PREFIX} {key}: {value}"

    @staticmethod
    def _create_file_line(path: str) -> str:
        # TOC file use windows path separators
        windows_path = PureWindowsPath(path)
        return f"{windows_path}"

    def filename(self, addon_name: str) -> str:
        return f"{addon_name}{self.flavor_suffix or ''}.toc"

    def generate(self) -> str:
        return "\n".join(
            (
                *(self._create_tag_line(key, value) for key, value in self.tags),
                "",
                *(self._create_file_line(files) for files in self.files),
            )
        )
