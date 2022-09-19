from __future__ import annotations

import importlib.resources
import json
import re
import sys
from functools import cached_property, total_ordering
from pathlib import Path
from typing import ClassVar, Literal, Mapping, Match, cast, get_args

from attr import frozen

import wap
from wap.exception import PlatformException


@frozen(slots=False)
@total_ordering
class Version:

    _INTERFACE_PATTERN: ClassVar[
        str
    ] = r"""(?x)
        ^
        (?P<major>\d+)
        (?P<minor>\d{2})
        (?P<patch>\d{2})
        $
    """
    DOT_PATTERN: ClassVar[
        str
    ] = r"""(?x)
        ^
        (?P<major>\d+)
        \.
        (?P<minor>\d+)
        \.
        (?P<patch>\d+)
        $
    """

    dotted: str

    @cached_property
    def _parse(self) -> Mapping[str, int]:
        # we know not None because versions come from schema-validated wap.json
        match = cast(Match[str], re.match(self.DOT_PATTERN, self.dotted))
        return {key: int(value) for key, value in match.groupdict().items()}

    @property
    def major(self) -> int:
        return self._parse["major"]

    @property
    def minor(self) -> int:
        return self._parse["minor"]

    @property
    def patch(self) -> int:
        return self._parse["patch"]

    @property
    def interface_version(self) -> str:
        return f"{self.major}{self.minor:0>2}{self.patch:0>2}"

    @property
    def as_tuple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.dotted == other.dotted

    def __lt__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.as_tuple < other.as_tuple


FlavorName = Literal[
    "mainline",
    "wrath",
    "vanilla",
]
FLAVOR_NAMES: tuple[FlavorName, ...] = get_args(FlavorName)


@frozen(kw_only=True)
class Flavor:
    name: FlavorName
    canon_name: str
    toc_suffix: str
    latest_version: Version
    installation_dir_name: str


def _get_latest_versions() -> Mapping[FlavorName, str]:
    path = importlib.resources.files(wap).joinpath("versions/latest.json")
    data = path.read_text(encoding="utf-8")
    obj: Mapping[FlavorName, str] = json.loads(data)
    return obj


_latest_versions = _get_latest_versions()

MAINLINE_FLAVOR = Flavor(
    name="mainline",
    canon_name="Mainline",
    toc_suffix="_Mainline",
    latest_version=Version(_latest_versions["mainline"]),
    installation_dir_name="_retail_",
)
WRATH_FLAVOR = Flavor(
    name="wrath",
    canon_name="Wrath of the Lich King Classic",
    toc_suffix="_Wrath",
    latest_version=Version(_latest_versions["wrath"]),
    installation_dir_name="_classic_",
)
VANILLA_FLAVOR = Flavor(
    name="vanilla",
    canon_name="WoW Classic",
    toc_suffix="_Vanilla",
    latest_version=Version(_latest_versions["vanilla"]),
    installation_dir_name="_classic_era_",
)

FLAVORS = [
    MAINLINE_FLAVOR,
    WRATH_FLAVOR,
    VANILLA_FLAVOR,
]

FLAVOR_MAP = {flavor.name: flavor for flavor in FLAVORS}

_DEFAULT_INSTALL_PATH_FOR_PLATFORM = {
    "win32": R"C:\Program Files (x86)\World of Warcraft",
    "darwin": "/Applications/World of Warcraft",
}


def get_default_addons_path(flavor: Flavor, platform: str | None = None) -> Path:
    if not platform:
        platform = sys.platform

    if platform not in _DEFAULT_INSTALL_PATH_FOR_PLATFORM:
        raise PlatformException(f"No default addon path for platform {platform}")

    return (
        Path(_DEFAULT_INSTALL_PATH_FOR_PLATFORM[platform])
        / flavor.installation_dir_name
        / "Interface"
        / "AddOns"
    )
