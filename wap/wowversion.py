from __future__ import annotations

import re
from typing import ClassVar, Mapping

import attr

from wap.exception import WoWVersionException


@attr.s(kw_only=True, auto_attribs=True, order=True, frozen=True)
class WoWVersion:

    _CLASSIC: ClassVar[str] = "classic"
    _RETAIL: ClassVar[str] = "retail"
    _DOT_PATTERN: ClassVar[str] = r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$"
    _INTERFACE_PATTERN: ClassVar[
        str
    ] = r"^(?P<major>\d+)(?P<minor>\d{2})(?P<patch>\d{2})$"
    _CLASSIC_MAJOR_THRESHOLD: ClassVar[int] = 1
    ADDONS_PATH_TYPE_MAP: ClassVar[Mapping[str, str]] = {
        "_retail_": _RETAIL,
        "_classic_": _CLASSIC,
    }

    major: int
    minor: int
    patch: int

    @classmethod
    def from_dot_version(cls, version: str) -> WoWVersion:
        if not (match := re.match(cls._DOT_PATTERN, version)):
            raise WoWVersionException(
                'WoW versions must be of form "x.y.z" where x, y, and z are integers'
            )

        return WoWVersion(
            major=int(match["major"]),
            minor=int(match["minor"]),
            patch=int(match["patch"]),
        )

    def dot_version(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def interface_version(self) -> str:
        return f"{self.major}{self.minor:0>2}{self.patch:0>2}"

    def type(self) -> str:
        if self.major > self._CLASSIC_MAJOR_THRESHOLD:
            return self._RETAIL
        return self._CLASSIC

    @classmethod
    def addons_path_type(cls, type_part: str) -> str:
        return cls.ADDONS_PATH_TYPE_MAP[type_part]


LATEST_RETAIL_VERSION = WoWVersion.from_dot_version("9.0.2")
LATEST_CLASSIC_VERSION = WoWVersion.from_dot_version("1.13.6")
