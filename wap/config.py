from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from pathlib import Path, PurePosixPath
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
from wap.wowversion import WoWVersion

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

        return cls.from_python_object(obj.data)

    @classmethod
    @abstractmethod
    def from_python_object(
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
                data=self.to_python_object(),
                schema=self._yaml_schema(),
            ).as_yaml(),
        )

    @abstractmethod
    def to_python_object(
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
    files: Sequence[PurePosixPath] = attr.ib()

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
        attribute: attr.Attribute[Sequence[PurePosixPath]],
        value: Sequence[PurePosixPath],
    ) -> None:
        if any(path.is_absolute() for path in value):
            raise ConfigSemanticException(
                f'File path "{value}" in TOC config must be relative (not absolute)'
            )

    @classmethod
    def from_python_object(
        cls,
        obj: Mapping[str, Any],
    ) -> TocConfig:
        tags = obj["tags"]

        files = [PurePosixPath(file) for file in obj["files"]]

        return cls(
            tags=tags,
            files=files,
        )

    def to_python_object(
        self,
    ) -> Mapping[str, Any]:
        return {
            "tags": {key: value for key, value in self.tags.items()},
            "files": [str(file) for file in self.files],
        }


@attr.s(kw_only=True, auto_attribs=True, order=False)
class AddonConfig(YamlType["AddonConfig", Mapping[str, Any]]):
    path: PurePosixPath = attr.ib()
    toc_config: TocConfig

    @path.validator
    def _check_path_relative(
        self,
        attribute: attr.Attribute[PurePosixPath],
        value: PurePosixPath,
    ) -> None:
        if value.is_absolute():
            raise ConfigSemanticException(
                f'Directory path "{value}" in addon config must be relative (not '
                "absolute)"
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
    def from_python_object(
        cls,
        obj: Mapping[str, Any],
    ) -> AddonConfig:
        path = PurePosixPath(obj["path"])

        toc_config = TocConfig.from_python_object(obj["toc"])

        return cls(
            path=path,
            toc_config=toc_config,
        )

    def to_python_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {"path": str(self.path)}
        if self.toc_config is not None:
            obj["toc"] = self.toc_config.to_python_object()
        return obj


@attr.s(kw_only=True, auto_attribs=True, order=False)
class CurseforgeConfig(YamlType["CurseforgeConfig", Mapping[str, Any]]):
    project_id: str
    changelog_path: Optional[PurePosixPath] = attr.ib()
    project_slug: str

    @classmethod
    def _yaml_schema(cls) -> Validator:
        return strictyaml.Map(
            {
                "project-id": strictyaml.Str(),
                "project-slug": strictyaml.Str(),
                strictyaml.Optional("changelog-file"): strictyaml.Str(),
            }
        )

    @changelog_path.validator
    def _check_path_relative(
        self,
        attribute: attr.Attribute[Optional[PurePosixPath]],
        value: Optional[PurePosixPath],
    ) -> None:
        if value is not None and value.is_absolute():
            raise ConfigSemanticException(
                f'Changelog path "{value}" in curseforge config must be relative '
                "(not absolute)"
            )

    @classmethod
    def from_python_object(
        cls,
        obj: Mapping[str, Any],
    ) -> CurseforgeConfig:
        project_id = obj["project-id"]

        project_slug = obj["project-slug"]

        changelog_path: Optional[PurePosixPath] = None
        if "changelog-file" in obj:
            changelog_path = PurePosixPath(obj["changelog-file"])

        return cls(
            project_id=project_id,
            changelog_path=changelog_path,
            project_slug=project_slug,
        )

    def to_python_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {
            "project-id": self.project_id,
            "project-slug": self.project_slug,
        }
        if self.changelog_path is not None:
            obj["changelog-file"] = str(self.changelog_path)
        return obj


@attr.s(kw_only=True, auto_attribs=True, order=False)
class Config(YamlType["Config", Mapping[str, Any]]):
    name: str
    wow_versions: Sequence[WoWVersion] = attr.ib()
    curseforge_config: Optional[CurseforgeConfig] = attr.ib(default=None)
    addon_configs: Sequence[AddonConfig]

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
                    f"There must be at most one {type} version. Found {versions}."
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
                "addons": strictyaml.Seq(AddonConfig._yaml_schema()),
            }
        )

    @classmethod
    def from_python_object(
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
            curseforge_config = CurseforgeConfig.from_python_object(obj["curseforge"])

        addon_configs = [
            AddonConfig.from_python_object(addon) for addon in obj["addons"]
        ]
        if len({addon_config.path for addon_config in addon_configs}) < len(
            addon_configs
        ):
            raise ConfigSemanticException(
                "Directory paths in addon configs must have unique paths"
            )

        return cls(
            name=name,
            wow_versions=wow_versions,
            curseforge_config=curseforge_config,
            addon_configs=addon_configs,
        )

    def to_python_object(
        self,
    ) -> Mapping[str, Any]:
        obj: dict[str, Any] = {
            "name": self.name,
            "wow-versions": [
                wow_version.dot_version() for wow_version in self.wow_versions
            ],
        }
        if self.curseforge_config is not None:
            obj["curseforge"] = self.curseforge_config.to_python_object()

        # we could hypothetically put this in the map literal above, but I want to
        # normalize order. note that order of key-value pairs in YAML is not recognized,
        # but strictyaml uses an ordered dict to hold them, so this is possible.
        obj["addons"] = [
            addon_config.to_python_object() for addon_config in self.addon_configs
        ]

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
