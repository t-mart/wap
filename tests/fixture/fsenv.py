import importlib.resources
import json
import shutil
from pathlib import Path
from typing import Any, Optional

from attr import frozen

import tests.fixture


def _get_fixture_file_path(subpath: Path) -> Path:
    return Path(
        str(importlib.resources.files(tests.fixture).joinpath(Path("data") / subpath))
    )


def copy_path(src: Path, dst: Path) -> None:
    if src.is_file():
        shutil.copyfile(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        raise Exception(f"{src} is not a file or directory")


@frozen(kw_only=True)
class FSEnv:
    root: Path

    # def place_config(
    #     self, config_fixture_file_name: str, target_name: Optional[str] = None
    # ) -> Path:
    #     return self._place_fixture_path(
    #         data_path=Path("configs") / config_fixture_file_name,
    #         target_name=target_name or "wap.json",
    #     )

    def place_addon(
        self, addon_fixture_dir_name: str, target_name: Optional[str] = None
    ) -> Path:
        return self._place_fixture_path(
            data_path=Path("addons") / addon_fixture_dir_name,
            target_name=target_name or "Addon",
        )

    def place_output_dir(
        self, output_dir_name: str, target_name: Optional[str] = None
    ) -> Path:
        return self._place_fixture_path(
            data_path=Path("output_dirs") / output_dir_name,
            target_name=target_name or "dist/",
        )

    def _place_fixture_path(self, data_path: Path, target_name: str) -> Path:
        full_target_path = self.root / target_name
        source_path = _get_fixture_file_path(data_path)
        copy_path(source_path, full_target_path)

        return full_target_path

    def place_file(
        self,
        target_name: str,
        parents: bool = False,
        exist_ok: bool = False,
        text: str = "",
    ) -> Path:
        path = self.root / target_name
        if parents:
            path.parent.mkdir(parents=True, exist_ok=exist_ok)
        path.write_text(text)
        return path

    def place_dir(
        self, target_name: str, parents: bool = False, exist_ok: bool = False
    ) -> Path:
        path = self.root / target_name
        path.mkdir(parents=parents, exist_ok=exist_ok)
        return path

    def get_config_json(
        self,
        config_fixture_file_name: str,
    ) -> Any:
        config_path = _get_fixture_file_path(Path("configs") / config_fixture_file_name)
        text = config_path.read_text()
        return json.loads(text)

    def write_config(
        self,
        config: Any,
        target_name: Optional[str] = None,
    ) -> Path:
        return self.place_file(target_name or "wap.json", text=json.dumps(config))
