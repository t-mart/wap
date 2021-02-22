from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any, Generic, Mapping, Optional, Sequence, TypeVar, cast

import attr
import strictyaml
from strictyaml.validators import Validator

from wap.exception import (
    ConfigFileException,
    ConfigSchemaException,
    ConfigSemanticException,
    WoWVersionException,
)
from wap.wowversion import LATEST_RETAIL_VERSION, WoWVersion

_Type = TypeVar("_Type")
_YamlObjectType = TypeVar("_YamlObjectType")


@attr.s(kw_only=True, auto_attribs=True, order=False)
class YamlType(Generic[_Type, _YamlObjectType], metaclass=ABCMeta):
    @classmethod
    def from_yaml(cls, yaml: str, label: str = "string") -> _Type:
        """
        label improves strictyaml's error messaging with the source of the yaml. if a
        file path is available, use that.
        """
        try:
            obj = strictyaml.load(
                yaml_string=yaml, schema=cls._yaml_schema(), label=label
            )
        except strictyaml.YAMLValidationError as yve:
            raise ConfigSchemaException(str(yve))

        return cls.from_yaml_object(obj.data)

    @classmethod
    @abstractmethod
    def from_yaml_object(
        cls,
        obj: _YamlObjectType,
    ) -> _Type:
        raise NotImplementedError()

    def to_yaml(self) -> str:
        # don't try-except here. we have a bug if the schema validation fails and want
        # to see the stack trace.

        # cast here because mypy thinks this is an Any
        return cast(
            str,
            strictyaml.as_document(
                data=self.to_yaml_object(),
                schema=self._yaml_schema(),
            ).as_yaml(),
        )

    @abstractmethod
    def to_yaml_object(
        self,
    ) -> _YamlObjectType:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def _yaml_schema(cls) -> strictyaml.Validator:
        raise NotImplementedError()


@attr.s(kw_only=True, auto_attribs=True, order=False)
class TocConfig(YamlType["TocConfig", Mapping[str, Any]]):
    tags: Mapping[str, str]
    files: Sequence[Path] = attr.ib()

    @classmethod
    def _yaml_schema(cls) -> strictyaml.Validator:
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
    def from_yaml_object(
        cls,
        obj: Mapping[str, Any],
    ) -> TocConfig:
        tags = obj["tags"]

        files = [Path(file) for file in obj["files"]]

        return cls(
            tags=tags,
            files=files,
        )

    def to_yaml_object(
        self,
    ) -> Mapping[str, Any]:
        return {
            "tags": {key: value for key, value in self.tags.items()},
            "files": [str(file) for file in self.files],
        }


@attr.s(kw_only=True, auto_attribs=True, order=False)
class DirConfig(YamlType["DirConfig", Mapping[str, Any]]):
    path: Path = attr.ib()
    toc_config: TocConfig = attr.ib(default=None)

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
    def _yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "path": strictyaml.Str(),
                "toc": TocConfig._yaml_schema(),
            }
        )

    @classmethod
    def from_yaml_object(
        cls,
        obj: Mapping[str, Any],
    ) -> DirConfig:
        path = Path(obj["path"])

        toc_config = TocConfig.from_yaml_object(obj["toc"])

        return cls(
            path=path,
            toc_config=toc_config,
        )

    def to_yaml_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {"path": str(self.path)}
        if self.toc_config is not None:
            obj["toc"] = self.toc_config.to_yaml_object()
        return obj


@attr.s(kw_only=True, auto_attribs=True, order=False)
class CurseforgeConfig(YamlType["CurseforgeConfig", Mapping[str, Any]]):
    project_id: str
    changelog_path: Path = attr.ib()
    addon_name: str

    @classmethod
    def _yaml_schema(cls) -> Validator:
        return strictyaml.Map(
            {
                "project-id": strictyaml.Str(),
                "changelog": strictyaml.Str(),
                "addon-name": strictyaml.Str(),
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
    def from_yaml_object(
        cls,
        obj: Mapping[str, Any],
    ) -> CurseforgeConfig:
        project_id = obj["project-id"]

        changelog_path = Path(obj["changelog"])

        addon_name = obj["addon-name"]

        return cls(
            project_id=project_id,
            changelog_path=changelog_path,
            addon_name=addon_name,
        )

    def to_yaml_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {
            "project-id": self.project_id,
            "changelog": str(self.changelog_path),
            "addon-name": self.addon_name,
        }
        return obj


@attr.s(kw_only=True, auto_attribs=True, order=False)
class Config(YamlType["Config", Mapping[str, Any]]):
    name: str
    wow_versions: Sequence[WoWVersion] = attr.ib()
    curseforge_config: Optional[CurseforgeConfig] = attr.ib(default=None)
    dir_configs: Sequence[DirConfig]

    @wow_versions.validator
    def _check_wow_versions_no_dupe_types(
        self,
        attribute: attr.Attribute[Sequence[WoWVersion]],
        value: Sequence[WoWVersion],
    ) -> None:
        type_versions = defaultdict(list)
        for wow_version in value:
            type_versions[wow_version.type()].append(wow_version.dot_version())

        for type, versions in type_versions.items():
            if len(versions) > 1:
                raise ConfigSemanticException(
                    f"There must be at most one {type} version. Found {versions}"
                )

    @classmethod
    def _yaml_schema(cls) -> strictyaml.Validator:
        return strictyaml.Map(
            {
                "name": strictyaml.Str(),
                "wow-versions": strictyaml.Seq(
                    strictyaml.Str(),
                ),
                strictyaml.Optional("curseforge"): CurseforgeConfig._yaml_schema(),
                "dirs": strictyaml.Seq(DirConfig._yaml_schema()),
            }
        )

    @classmethod
    def from_yaml_object(
        cls,
        obj: Mapping[str, Any],
    ) -> Config:
        name: str = obj["name"]

        try:
            wow_versions = [
                WoWVersion.from_dot_version(wow_version)
                for wow_version in obj["wow-versions"]
            ]
        except WoWVersionException as wve:
            raise ConfigSemanticException(wve.message)

        curseforge_config = None
        if "curseforge" in obj:
            curseforge_config = CurseforgeConfig.from_yaml_object(obj["curseforge"])

        dir_configs = [DirConfig.from_yaml_object(dir_) for dir_ in obj["dirs"]]
        if len({dir_config.path for dir_config in dir_configs}) < len(dir_configs):
            raise ConfigSemanticException(f"Dirs in config must have unique paths")

        return cls(
            name=name,
            wow_versions=wow_versions,
            curseforge_config=curseforge_config,
            dir_configs=dir_configs,
        )

    def to_yaml_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {
            "name": self.name,
            "wow-versions": [
                wow_version.dot_version() for wow_version in self.wow_versions
            ],
        }
        if self.curseforge_config is not None:
            obj["curseforge"] = self.curseforge_config.to_yaml_object()

        # we could hypothetically put this in the map literal above, but I want to
        # normalize order. note that order of key-value pairs in YAML is not recognized,
        # but strictyaml uses an ordered dict to hold them, so this is possible.
        obj["dirs"] = [dir_config.to_yaml_object() for dir_config in self.dir_configs]

        return obj

    @classmethod
    def from_path(cls, path: Path) -> Config:
        if not path.is_file():
            raise ConfigFileException(f'No such config file "{path}"')

        with path.open("r") as file:
            contents = file.read()

        return cls.from_yaml(yaml=contents, label=str(path))

    def to_path(self, path: Path) -> None:
        with path.open("w") as file:
            file.write(self.to_yaml())
            file.write("\n")


def default_config(name: str) -> Config:
    return Config(
        name=name,
        wow_versions=[LATEST_RETAIL_VERSION],
        curseforge_config=CurseforgeConfig(
            project_id="00000",
            changelog_path=Path("CHANGELOG.md"),
            addon_name="fill-this-in",
        ),
        dir_configs=[
            DirConfig(
                path=Path(name),
                toc_config=TocConfig(
                    tags={
                        "Title": name,
                        "Author": "Your name",
                        "Notes": "The description of your addon...",
                        "DefaultState": "Enabled",
                        "LoadOnDemand": "0",
                    },
                    files=[Path(name).with_suffix(".lua")],
                ),
            )
        ],
    )
