from typing import Literal
from unittest.mock import DEFAULT, patch

import pytest

from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv
from wap import prompt
from wap.wow import FLAVORS, MAINLINE_FLAVOR


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
        get_project_id=DEFAULT,
        get_project_slug=DEFAULT,
        confirm_publish=DEFAULT,
        confirm_all_ok=DEFAULT,
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
        project_id = "1234"
        mocks["get_project_id"].return_value = project_id
        project_slug = "slug"
        mocks["get_project_slug"].return_value = project_slug
        confirm_publish = True
        mocks["confirm_publish"].return_value = confirm_publish
        confirm_all_ok = True
        mocks["confirm_all_ok"].return_value = confirm_all_ok

        config = prompt.prompt_for_config(mode=mode)

        expected_config = {
            "$schema": get_basic_config()["$schema"],
            "name": package_name,
            "version": version,
            "author": author,
            "wowVersions": {
                MAINLINE_FLAVOR.name: MAINLINE_FLAVOR.latest_version.dotted
            },
            "publish": {
                "curseforge": {
                    "projectId": project_id,
                    "slug": project_slug,
                }
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
    with patch("wap.prompt.prompt_ask") as mock:
        mock.side_effect = ["foo", "bar"]
        name = prompt.get_package_name_new_project()
        assert name == "bar"


def test_get_supported_flavors() -> None:
    with patch("wap.prompt.confirm_ask") as mock:
        # simulate answering no to them all first, which is disallowed. then answering
        # yes.
        mock.side_effect = [*[False for _ in FLAVORS], *[True for _ in FLAVORS]]
        flavors = prompt.get_supported_flavors()
        assert set(flavors) == set(FLAVORS)


def test_get_project_id() -> None:
    expected_project_id = "1234"
    with patch("wap.prompt.prompt_ask") as mock:
        mock.side_effect = ["not valid", expected_project_id]
        project_id = prompt.get_project_id()
        assert project_id == expected_project_id


@pytest.mark.parametrize(
    "input, expected_slug",
    [
        (None, None),
        ("slug", "slug"),
    ],
)
def test_get_project_slug(input: str, expected_slug: str) -> None:
    with patch("wap.prompt.prompt_ask") as mock:
        mock.return_value = input
        slug = prompt.get_project_slug()
        assert slug == expected_slug
