from __future__ import annotations

import importlib.resources
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Callable

import jsonschema
from attrs import field, frozen

import wap
from wap.curseforge import ChangelogType, ReleaseType
from wap.wow import FlavorName

from .exception import ConfigSchemaError, EncodingError

SCHEMA_URL = (
    "https://raw.githubusercontent.com/t-mart/wap/master/src/wap/schema/wap.schema.json"
)


def get_schema() -> Any:
    path = importlib.resources.files(wap).joinpath("schema/wap.schema.json")
    data = path.read_text(encoding="utf-8")
    return json.loads(data)


@frozen(kw_only=True)
class Config:
    name: str
    version: str
    author: str | None = field(default=None)
    description: str | None = field(default=None)
    wow_versions: Mapping[FlavorName, str]
    publish: PublishConfig | None = field(default=None)
    package: Sequence[AddonConfig]

    @classmethod
    def from_python_object(cls, obj: Mapping[str, Any]) -> Config:
        try:
            jsonschema.validate(obj, get_schema())
        except jsonschema.ValidationError as validation_error:
            raise ConfigSchemaError(
                f"Invalid configuation: {validation_error.message} at path "
                f"{validation_error.json_path}. Please correct your configuration and "
                "try again."
            ) from validation_error

        publish_obj = obj.get("publish", None)
        if publish_obj is not None:
            publish = PublishConfig.from_python_object(publish_obj)
        else:
            publish = None

        return cls(
            name=obj["name"],
            version=obj["version"],
            author=obj.get("author", None),
            wow_versions=obj["wowVersions"],
            publish=publish,
            package=[AddonConfig.from_python_object(obj) for obj in obj["package"]],
        )

    @classmethod
    def from_path(cls, path: Path) -> Config:
        try:
            return cls.from_python_object(json.loads(path.read_text(encoding="utf-8")))
        except UnicodeDecodeError as unicode_decode_error:
            raise EncodingError(
                f'Config file "{path}" should be utf-8: {unicode_decode_error}'
            ) from unicode_decode_error
        except json.JSONDecodeError as json_decode_error:
            raise EncodingError(
                f'Config file "{path}" should be well-formed JSON: {json_decode_error}.'
            ) from json_decode_error

    def to_python_object(self, with_schema: bool = True) -> Any:
        # i like a certain key order
        obj: dict[str, Any] = {}
        if with_schema:
            obj["$schema"] = SCHEMA_URL
        obj["name"] = self.name
        obj["version"] = self.version
        if self.author is not None:
            obj["author"] = self.author
        if self.description is not None:
            obj["description"] = self.description
        obj["wowVersions"] = self.wow_versions
        if self.publish is not None:
            obj["publish"] = self.publish.to_python_object()
        obj["package"] = [addon.to_python_object() for addon in self.package]
        obj["name"] = self.name

        try:
            jsonschema.validate(obj, get_schema())
        except jsonschema.ValidationError as validation_error:
            raise ConfigSchemaError(
                f"Invalid configuation: {validation_error.message} at path "
                f"{validation_error.json_path}  Please correct your configuration and "
                "try again."
            ) from validation_error

        return obj

    def to_json(self, with_schema: bool = True, indent: bool = False) -> str:
        return json.dumps(
            self.to_python_object(with_schema=with_schema),
            indent=2 if indent else None,
        )

    def write_to_path(
        self, path: Path, with_schema: bool = True, indent: bool = False
    ) -> None:
        path.write_text(self.to_json(with_schema=with_schema, indent=indent))


@frozen(kw_only=True)
class PublishConfig:
    curseforge: CurseforgeConfig | None = field(default=None)

    @classmethod
    def from_python_object(cls, obj: Mapping[str, Any]) -> PublishConfig:
        curseforge_obj = obj.get("curseforge", None)
        if curseforge_obj is not None:
            curseforge = CurseforgeConfig.from_python_object(curseforge_obj)
        else:
            curseforge = None

        return cls(curseforge=curseforge)

    def to_python_object(self) -> dict[str, Any]:
        if self.curseforge is not None:
            return {"curseforge": self.curseforge.to_python_object()}
        return {}


@frozen(kw_only=True)
class CurseforgeConfig:
    project_id: str
    slug: str | None = field(default=None)
    changelog_file: str | None = field(default=None)
    changelog_text: str | None = field(default=None)
    changelog_type: ChangelogType | None = field(default=None)
    release_type: ReleaseType | None = field(default=None)

    @classmethod
    def from_python_object(cls, obj: Mapping[str, Any]) -> CurseforgeConfig:
        return cls(
            project_id=obj["projectId"],
            slug=obj.get("slug", None),
            changelog_file=obj.get("changelogFile", None),
            changelog_text=obj.get("changelogText", None),
            changelog_type=obj.get("changelogType", None),
            release_type=obj.get("releaseType", None),
        )

    def to_python_object(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        obj["projectId"] = self.project_id
        if self.slug:
            obj["slug"] = self.slug
        if self.changelog_file:
            obj["changelogFile"] = self.changelog_file
        if self.changelog_text:
            obj["changelogText"] = self.changelog_text
        if self.changelog_type:
            obj["changelogType"] = self.changelog_type
        if self.release_type:
            obj["releaseType"] = self.release_type
        return obj


@frozen(kw_only=True)
class AddonConfig:
    path: str
    toc: TocConfig | None = field(default=None)
    include: Sequence[str] | None = field(default=None)

    @classmethod
    def from_python_object(cls, obj: Mapping[str, Any]) -> AddonConfig:
        toc_obj = obj.get("toc", None)
        if toc_obj is not None:
            toc = TocConfig.from_python_object(toc_obj)
        else:
            toc = None

        return cls(
            path=obj["path"],
            toc=toc,
            include=obj.get("include", None),
        )

    def to_python_object(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        obj["path"] = self.path
        if self.toc:
            obj["toc"] = self.toc.to_python_object()
        if self.include:
            obj["include"] = self.include
        return obj


@frozen(kw_only=True)
class TocConfig:
    tags: Mapping[str, bool | str | Sequence[str]]
    files: Sequence[str]

    @classmethod
    def from_python_object(cls, obj: Mapping[str, Any]) -> TocConfig:
        return cls(
            tags=obj.get("tags", {}),
            files=obj.get("files", []),
        )

    @property
    def serialized_tags(self) -> Mapping[str, str]:
        def enabled(value: bool) -> str:
            return "enabled" if value else "disabled"

        def zero_one(value: bool) -> str:
            return "1" if value else "0"

        transformer: dict[str, Callable[[Any], str]] = {
            "LoadOnDemand": zero_one,
            "Dependencies": ", ".join,
            "OptionalDeps": ", ".join,
            "LoadWith": ", ".join,
            "LoadManagers": ", ".join,
            "DefaultState": enabled,
            "SavedVariables": ", ".join,
            "SavedVariablesPerCharacter": ", ".join,
        }

        def pass_through(value: str) -> str:
            return value

        return {
            key: transformer.get(key, pass_through)(value)
            for key, value in self.tags.items()
        }

    def to_python_object(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        obj["tags"] = self.tags
        obj["files"] = self.files
        return obj
