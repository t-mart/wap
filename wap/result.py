from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

import attr
import click

from wap.config import WowVersionConfig


def _value_serializer(type_: type, attribute: attr.Attribute[Any], value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, int):
        return value
    return value  # not my problem


def _filter(attribute: attr.Attribute[Any], value: Any) -> bool:
    return value is not None


@attr.s(kw_only=True, order=False, auto_attribs=True)
class Result:
    build_path: Optional[Path] = attr.ib(default=None)
    zip_path: Optional[Path] = attr.ib(default=None)
    curseforge_file_id: Optional[int] = attr.ib(default=None)
    dev_install_paths: Optional[list[Path]] = attr.ib(default=None)


@attr.s(kw_only=True, order=False, auto_attribs=True)
class ResultMap:
    results: dict[str, Result] = attr.ib(factory=dict)

    def add_by_wow_version_config(
        self, wow_version_config: WowVersionConfig, result: Result
    ) -> None:
        self.results[wow_version_config.type_] = result

    def as_dict(self) -> dict[str, Any]:
        return attr.asdict(  # type: ignore
            self,
            filter=_filter,
            value_serializer=_value_serializer,
        )["results"]

    def write(self, indent: Optional[int] = 2) -> None:
        click.echo(
            json.dumps(
                self.as_dict(),
                indent=indent,
            )
        )
