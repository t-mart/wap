from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Mapping

import attr

from wap.exception import WowAddonPathException


@attr.s(auto_attribs=True, frozen=True, kw_only=True, order=False)
class WoWAddonsPath:
    path: Path = attr.ib()

    DEV_INSTALL_WOW_TYPE_PART_MAP: ClassVar[Mapping[str, str]] = {
        "_retail_": "retail",
        "_classic_": "classic",
    }

    @path.validator
    def _check_path_is_wow_addons_dir(
        self,
        attribute: attr.Attribute[Path],
        value: Path,
    ) -> None:
        if not value.is_dir():
            raise WowAddonPathException(f"WoW AddOns path {value} is not a directory")

        try:
            *_, wow_part, type_part, interface_part, addons_part = value.parts
        except ValueError:
            raise WowAddonPathException(
                f"WoW AddOns path {value} does not look like a WoW AddOns " "directory"
            )

        if (
            wow_part != "World of Warcraft"
            or interface_part != "Interface"
            or addons_part != "AddOns"
        ):
            raise WowAddonPathException(
                f"WoW AddOns path {value} does not look like a WoW AddOns " "directory"
            )

        if type_part not in self.DEV_INSTALL_WOW_TYPE_PART_MAP.keys():
            key_str = ", ".join(self.DEV_INSTALL_WOW_TYPE_PART_MAP.keys())
            raise WowAddonPathException(
                f"WoW AddOns path {value} should have a type part in {key_str}"
            )

    @property
    def type_(self) -> str:
        parts = self.path.parts
        return self.DEV_INSTALL_WOW_TYPE_PART_MAP[parts[-3]]
