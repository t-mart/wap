from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Generic, Mapping, Optional, Sequence, TypeVar

import attr
import strictyaml
from strictyaml.validators import Validator

from wap import log
from wap.exception import (
    ConfigFileException,
    ConfigSchemaException,
    ConfigSemanticException,
)

_T = TypeVar("_T")


@attr.s(kw_only=True, auto_attribs=True, order=False)
class _YAMLDeserializable(Generic[_T], metaclass=ABCMeta):
    @classmethod
    def from_yaml(cls, yaml: str, label: str = "string") -> _T:
        """
        label improves strictyaml's error messaging with the source of the yaml. if a
        filename is available, use that.
        """
        try:
            config_dict = strictyaml.load(
                yaml_string=yaml, schema=cls.yaml_schema(), label=label
            )
        except strictyaml.YAMLValidationError as yve:
            raise ConfigSchemaException(str(yve))

        return cls._from_dict(config_dict.data)

    @classmethod
    @abstractmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> _T:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def yaml_schema(cls) -> strictyaml.Validator:
        raise NotImplementedError()


@attr.s(kw_only=True, auto_attribs=True, order=False)
class PackageConfig(_YAMLDeserializable["PackageConfig"]):
    name: str
    wow_version_configs: list[WowVersionConfig]
    curseforge_config: Optional[CurseforgeConfig] = attr.ib(default=None)
    dir_configs: list[DirConfig]

    @classmethod
    def yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "name": strictyaml.Str(),
                "wow-versions": strictyaml.Seq(WowVersionConfig.yaml_schema()),
                strictyaml.Optional("curseforge"): CurseforgeConfig.yaml_schema(),
                "dirs": strictyaml.Seq(DirConfig.yaml_schema()),
            }
        )

    @classmethod
    def from_path(cls, path: Path) -> PackageConfig:
        if path.suffix not in {".yml", ".yaml"}:
            # not too important, but a good sign that wap may be running incorrectly
            log.warn("Reading config from file without YAML extension")

        if not path.is_file():
            raise ConfigFileException(f'No such config file "{path}"')

        with path.open("r") as file:
            contents = file.read()

        return cls.from_yaml(yaml=contents, label=str(path))

    @classmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> PackageConfig:

        name: str = config_dict["name"]

        wow_version_configs = [
            WowVersionConfig._from_dict(wow_version)
            for wow_version in config_dict["wow-versions"]
        ]
        wow_version_config_types = {wvc.type_ for wvc in wow_version_configs}

        if len(wow_version_configs) != len(wow_version_config_types):
            raise ConfigSemanticException(
                "May only specify one retail and one classic version in wow-versions "
                "section"
            )

        curseforge_config = None
        if "curseforge" in config_dict:
            curseforge_config = CurseforgeConfig._from_dict(config_dict["curseforge"])

        dir_configs = [DirConfig._from_dict(dir_) for dir_ in config_dict["dirs"]]

        return cls(
            name=name,
            wow_version_configs=wow_version_configs,
            curseforge_config=curseforge_config,
            dir_configs=dir_configs,
        )

    def wow_version_by_type(self, type_: str) -> Optional[WowVersionConfig]:
        if type_ not in WowVersionConfig.TYPES:
            raise ValueError(
                f"type_ must be one of {', '.join(WowVersionConfig.TYPES)}"
            )

        version_map = {
            wow_version.type_: wow_version for wow_version in self.wow_version_configs
        }

        return version_map.get(type_, None)


@attr.s(kw_only=True, auto_attribs=True, order=False)
class CurseforgeConfig(_YAMLDeserializable["CurseforgeConfig"]):
    project_id: str
    changelog_path: Path = attr.ib()
    addon_name: Optional[str] = attr.ib(default=None)

    @classmethod
    def yaml_schema(cls) -> Validator:
        return strictyaml.Map(
            {
                "project-id": strictyaml.Str(),
                "changelog": strictyaml.Str(),
                strictyaml.Optional("addon-name"): strictyaml.Str(),
            }
        )

    @changelog_path.validator
    def _check_path_relative(
        self,
        attribute: attr.Attribute[Path],
        value: Path,
    ) -> None:
        if value.is_absolute():
            raise ConfigSemanticException(
                f"Changelog path {value} must be relative (not absolute)"
            )

    @classmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> CurseforgeConfig:

        project_id = config_dict["project-id"]

        changelog_path = Path(config_dict["changelog"])

        addon_name = config_dict.get("addon-name", None)

        return cls(
            project_id=project_id,
            changelog_path=changelog_path,
            addon_name=addon_name,
        )


@attr.s(kw_only=True, auto_attribs=True, order=False)
class DirConfig(_YAMLDeserializable["DirConfig"]):
    path: Path = attr.ib()
    toc_config: Optional[TocConfig] = attr.ib(default=None)

    @path.validator
    def _check_path_relative(
        self,
        attribute: attr.Attribute[Path],
        value: Path,
    ) -> None:
        if value.is_absolute():
            raise ConfigSemanticException(
                f"Directory path {value} must be relative (not absolute)"
            )

    @classmethod
    def yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "path": strictyaml.Str(),
                strictyaml.Optional("toc"): TocConfig.yaml_schema(),
            }
        )

    @classmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> DirConfig:

        path = Path(config_dict["path"])

        toc_config = None
        if "toc" in config_dict:
            toc_config = TocConfig._from_dict(config_dict["toc"])

        return cls(
            path=path,
            toc_config=toc_config,
        )


@attr.s(kw_only=True, auto_attribs=True, order=False)
class WowVersionConfig(_YAMLDeserializable["WowVersionConfig"]):

    TYPES: ClassVar[set[str]] = {"retail", "classic"}
    _VERSION_PATTERN = r"\d+\.\d+\.\d+"

    type_: str = attr.ib()
    version: str = attr.ib()

    @type_.validator
    def _check_type(
        self,
        attribute: attr.Attribute[Path],
        value: str,
    ) -> None:
        if value not in self.TYPES:
            raise ConfigSemanticException(
                f"wow-versions members must have a type in {self.TYPES}"
            )

    @version.validator
    def _check_version(
        self,
        attribute: attr.Attribute[Path],
        value: str,
    ) -> None:
        if not re.match(self._VERSION_PATTERN, value):
            raise ConfigSemanticException(
                'wow-versions members must have a version of form "x.y.z" where x, y, '
                "and z are integers"
            )

    @classmethod
    def yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "version": strictyaml.Str(),
                "type": strictyaml.Str(),
            }
        )

    def interface_version(self) -> str:
        major, minor, patch = (
            int(part) for part in self.version.split(".", maxsplit=2)
        )

        return f"{major}{minor:0>2}{patch:0>2}"

    @classmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> WowVersionConfig:

        version = config_dict["version"]

        type_ = config_dict["type"]

        return cls(
            version=version,
            type_=type_,
        )


@attr.s(kw_only=True, auto_attribs=True, order=False)
class TocConfig(_YAMLDeserializable["TocConfig"]):
    tags: Mapping[str, str]
    files: Sequence[Path] = attr.ib()

    @classmethod
    def yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "tags": strictyaml.MapPattern(
                    strictyaml.Str(),
                    strictyaml.Str(),
                ),
                "files": strictyaml.Seq(
                    strictyaml.Str(),
                ),
            }
        )

    @files.validator
    def _check_files_relative(
        self,
        attribute: attr.Attribute[Sequence[Path]],
        value: Sequence[Path],
    ) -> None:
        if any(path.is_absolute() for path in value):
            raise ConfigSemanticException(
                f"File path {value} in TOC must be relative (not absolute)"
            )

    @classmethod
    def _from_dict(
        cls,
        config_dict: Mapping[str, Any],
    ) -> TocConfig:

        tags = config_dict["tags"]

        files = [Path(file) for file in config_dict["files"]]

        return cls(
            tags=tags,
            files=files,
        )
