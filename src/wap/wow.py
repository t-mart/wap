from __future__ import annotations

import importlib.resources
import json
import re
import sys
from pathlib import Path
from typing import ClassVar, Literal, Mapping, get_args

from attrs import field, frozen

import wap
from wap.exception import VersionError


@frozen(order=True)
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
    _DOT_PATTERN: ClassVar[
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

    major: int
    minor: int
    patch: int

    @classmethod
    def from_dotted(cls, dotted: str) -> Version:
        if match := re.fullmatch(cls._DOT_PATTERN, dotted):
            return Version(
                major=int(match.group("major")),
                minor=int(match.group("minor")),
                patch=int(match.group("patch")),
            )
        raise VersionError(f"Dotted version {dotted} does not appear to be valid.")

    @classmethod
    def from_interface(cls, interface: str) -> Version:
        if match := re.fullmatch(cls._INTERFACE_PATTERN, interface):
            return Version(
                major=int(match.group("major")),
                minor=int(match.group("minor")),
                patch=int(match.group("patch")),
            )
        raise VersionError(
            f"Interface version {interface} does not appear to be valid."
        )

    @property
    def dotted(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def interface_version(self) -> str:
        return f"{self.major}{self.minor:0>2}{self.patch:0>2}"


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
    latest_version: Version = field(eq=False)
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
    latest_version=Version.from_dotted(_latest_versions["mainline"]),
    installation_dir_name="_retail_",
)
WRATH_FLAVOR = Flavor(
    name="wrath",
    canon_name="Wrath of the Lich King Classic",
    toc_suffix="_Wrath",
    latest_version=Version.from_dotted(_latest_versions["wrath"]),
    installation_dir_name="_classic_",
)
VANILLA_FLAVOR = Flavor(
    name="vanilla",
    canon_name="WoW Classic",
    toc_suffix="_Vanilla",
    latest_version=Version.from_dotted(_latest_versions["vanilla"]),
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


def get_default_addons_path(flavor: Flavor, platform: str | None = None) -> Path | None:
    if not platform:
        platform = sys.platform

    if platform not in _DEFAULT_INSTALL_PATH_FOR_PLATFORM:
        return None

    return (
        Path(_DEFAULT_INSTALL_PATH_FOR_PLATFORM[platform])
        / flavor.installation_dir_name
        / "Interface"
        / "AddOns"
    )
