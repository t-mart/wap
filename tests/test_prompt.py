from typing import Literal
from unittest.mock import DEFAULT, patch

import pytest

from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv
from wap import prompt
from wap.wow import MAINLINE_FLAVOR


@pytest.mark.parametrize("mode", ["new-config", "new-project"])
def test_prompt_for_config(mode: Literal["new-project", "new-config"]) -> None:
    with patch.multiple(
        "wap.prompt",
        get_package_name_new_project=DEFAULT,
        get_package_name_new_config=DEFAULT,
        get_author=DEFAULT,
        get_desc=DEFAULT,
        get_version=DEFAULT,
        get_supported_flavors=DEFAULT,
    ) as mocks:
        package_name = "package-name"
        mocks["get_package_name_new_config"].return_value = package_name
        mocks["get_package_name_new_project"].return_value = package_name
        author = "the author"
        mocks["get_author"].return_value = author
        desc = "the desc"
        mocks["get_desc"].return_value = desc
        version = "the version"
        mocks["get_version"].return_value = version
        supported_flavors = [MAINLINE_FLAVOR]
        mocks["get_supported_flavors"].return_value = supported_flavors

        config = prompt.prompt_for_config(mode=mode)

        expected_config = {
            "$schema": get_basic_config()["$schema"],
            "name": package_name,
            "version": version,
            "author": author,
            "wowVersions": {
                MAINLINE_FLAVOR.name: MAINLINE_FLAVOR.latest_version.dotted
            },
            "package": [
                {
                    "path": f"./{package_name}",
                    "toc": {
                        "tags": {
                            "Title": package_name,
                            "Notes": desc,
                        },
                        "files": ["Main.lua"],
                    },
                }
            ],
        }

        assert config.to_python_object() == expected_config


def test_get_package_name_new_project(fs_env: FSEnv) -> None:
    fs_env.place_file("foo")
    with patch("wap.prompt.Prompt.ask") as mock:
        mock.side_effect = ["foo", "bar"]
        name = prompt.get_package_name_new_project()
        assert name == "bar"


def test_get_supported_flavors() -> None:
    with patch("wap.prompt.Confirm.ask") as mock:
        # yeesh, this is tightly bound to FLAVORS
        # idea is to say no to first three, then yes to just one
        mock.side_effect = [False, False, False, True, False, False]
        flavors = prompt.get_supported_flavors()
        assert len(flavors) == 1
