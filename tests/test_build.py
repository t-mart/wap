from __future__ import annotations

import os
from collections.abc import Iterable, Iterator, Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from attrs import frozen
from glom import T, assign, glom  # type: ignore

from tests.cmd_util import invoke_build
from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv
from tests.fixture.time import TEST_TIME
from wap import __version__ as wap_version
from wap.exception import (
    ConfigError,
    EncodingError,
    PathExistsError,
    PathMissingError,
    PathTypeError,
    TagError,
)

INSTALLATION_ADDON_DIRS = {
    "mainline": "wow/_retail_/Interface/AddOns",
    "wrath": "wow/_classic_/Interface/AddOns",
    "vanilla": "wow/_classic_era_/Interface/AddOns",
}
SUFFIX_INTERFACE_PAIRS = [
    ("_Mainline", "90207"),
    ("_Vanilla", "11403"),
    ("_Wrath", "30400"),
    ("", "90207"),
]
PACKAGE_VERSION: str = get_basic_config()["version"]
PACKAGE_NAME = get_basic_config()["name"]


def check_basic_addon(addon_root: Path) -> None:
    config = get_basic_config()
    expected_toc_files = ["Main.lua", "Extra.lua"]
    expected_toc_tags: dict[str, str] = {
        "Title": glom(config, "package.0.toc.tags.Title"),
        "Version": PACKAGE_VERSION,
        # first consult tag Author, then top-level author key
        "Author": (
            glom(config, "package.0.toc.tags.Author", default=None)
            or glom(config, "author", default=None)
        ),
        "Notes": glom(config, "package.0.toc.tags.Notes"),
        "X-BuildDateTime": str(TEST_TIME),
        "X-BuildTool": f"wap {wap_version}",
    }
    for suffix, interface in SUFFIX_INTERFACE_PAIRS:
        path = addon_root / f"{addon_root.name}{suffix}.toc"
        toc = Toc.parse(path)
        assert toc == Toc(
            tags={k: v for k, v in expected_toc_tags.items() if v is not None}
            | {"Interface": interface},
            files=expected_toc_files,
        )

    expected_files = {
        addon_root / "Main.lua",
        addon_root / "Extra.lua",
        addon_root / "LICENSE",
    }
    for expected_file in expected_files:
        assert expected_file.is_file()


@frozen(kw_only=True)
class Toc:
    """
    Rudimentary recreation of toc parsing. just good enough for testing. dont want
    to use the SOT's code to do this.
    """

    tags: Mapping[str, str]
    files: Sequence[str]

    @classmethod
    def parse(cls, path: Path) -> Toc:
        contents = path.read_text()
        tags: dict[str, str] = {}
        files: list[str] = []
        for line in contents.splitlines():
            if line.startswith("##"):
                key, _, value = line.removeprefix("##").partition(":")
                tags[key.strip()] = value.strip()
            elif not line.startswith("#") and line:
                files.append(line.strip())

        return Toc(tags=tags, files=files)


def test_build_normal(fs_env: FSEnv) -> None:
    config = get_basic_config()
    config["package"].append(deepcopy(config["package"][0]))
    assign(config, "package.1.path", "./Addon2")
    fs_env.write_config(config)

    fs_env.place_addon("basic")
    fs_env.place_addon("basic", "Addon2")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert result.success

    check_basic_addon(Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon"))
    check_basic_addon(Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon2"))


def test_build_dupe_addon_path(fs_env: FSEnv) -> None:
    config = get_basic_config()
    config["package"].append(config["package"][0])
    fs_env.write_config(config)

    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, ConfigError)


def test_build_different_output_path(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    output_path = "output"

    result = invoke_build(["--output-path", output_path])

    assert result.success

    check_basic_addon(Path(f"{output_path}/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon"))


def test_build_different_config_path(fs_env: FSEnv) -> None:
    config_path = "config.json"
    fs_env.write_config(get_basic_config(), config_path)
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build(["--config-path", config_path])

    assert result.success

    check_basic_addon(Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon"))


def test_build_config_discovery(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    os.chdir(Path("Addon"))

    result = invoke_build()

    assert result.success

    check_basic_addon(Path(f"../dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon"))


def test_build_config_discovery_fail(fs_env: FSEnv) -> None:
    result = invoke_build()

    assert isinstance(result.exception, SystemExit)


@pytest.mark.parametrize("top_level_author", [True, False])
@pytest.mark.parametrize("toc_author", [True, False])
def test_build_author_fallback(
    fs_env: FSEnv, top_level_author: bool, toc_author: bool
) -> None:
    config = get_basic_config()

    top_level_author_name = "top-level"
    toc_author_name = "toc"
    if top_level_author:
        assign(config, "author", top_level_author_name)
    if toc_author:
        assign(config, "author", toc_author_name)

    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert result.success

    check_basic_addon(Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon"))


def test_build_missing_config() -> None:
    result = invoke_build()

    # i wish a more descriptive exception was thrown than SystemExit, but we have no
    # choice because click controls this raise
    assert isinstance(result.exception, SystemExit)


def test_build_config_is_not_file(fs_env: FSEnv) -> None:
    fs_env.place_dir("wap.json")

    result = invoke_build()

    assert isinstance(result.exception, SystemExit)


def test_build_missing_addon(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, PathTypeError)


def test_build_addon_path_is_not_dir(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_file("Addon")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, PathTypeError)


@pytest.mark.parametrize(
    "link_arg",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_with_linking(fs_env: FSEnv, link_arg: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    args: list[str] = []
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        args.extend((f"--{flavor}-addons-path", path))
        fs_env.place_dir(path, parents=True, exist_ok=True)

    args.extend(["--link", link_arg])

    result = invoke_build(args)

    assert result.success
    assert (
        Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon").resolve()
        == (Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon").resolve()
    )
    assert "Linked" in result.stderr


@pytest.mark.parametrize(
    "link_arg",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_link_already_linked(fs_env: FSEnv, link_arg: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    args: list[str] = []
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        args.extend((f"--{flavor}-addons-path", path))
        fs_env.place_dir(path, parents=True, exist_ok=True)

    # create initial fake output dir so that linking works
    build_dir = fs_env.place_dir(
        f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon", parents=True
    )
    (Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon").symlink_to(
        build_dir, target_is_directory=True
    )

    args.extend(["--link", link_arg])

    result = invoke_build(args)

    assert result.success
    assert (
        Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon").resolve()
        == (Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon").resolve()
    )


@pytest.mark.parametrize(
    "link_arg",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_link_path_exists(fs_env: FSEnv, link_arg: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    args: list[str] = []
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        args.extend((f"--{flavor}-addons-path", path))
        fs_env.place_dir(path, parents=True, exist_ok=True)

    # create a dir in the spot where the link would be made
    fs_env.place_dir(str(Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon"))

    args.extend(["--link", link_arg])

    result = invoke_build(args)

    assert isinstance(result.exception, PathExistsError)


@pytest.mark.parametrize(
    "link_arg",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_link_path_exists_force(fs_env: FSEnv, link_arg: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    args: list[str] = []
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        args.extend((f"--{flavor}-addons-path", path))
        fs_env.place_dir(path, parents=True, exist_ok=True)

    # create a dir in the spot where the link would be made
    fs_env.place_dir(str(Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon"))

    args.extend(["--link", link_arg, "--link-force"])

    result = invoke_build(args)

    assert result.success
    assert (
        Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon").resolve()
        == (Path(INSTALLATION_ADDON_DIRS[link_arg]) / "Addon").resolve()
    )


@pytest.mark.parametrize("add_auto", [True, False])
@pytest.mark.parametrize(
    "exist_flavor",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_with_auto_linking(
    fs_env: FSEnv, add_auto: bool, exist_flavor: str
) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    args: list[str] = []
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        args.extend((f"--{flavor}-addons-path", path))
        if exist_flavor == flavor:
            fs_env.place_dir(path, parents=True, exist_ok=True)

    args.append("--link")
    if add_auto:
        args.append("auto")

    result = invoke_build(args)

    assert result.success
    assert (
        Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon").resolve()
        == (Path(INSTALLATION_ADDON_DIRS[exist_flavor]) / "Addon").resolve()
    )
    for flavor, path in INSTALLATION_ADDON_DIRS.items():
        if exist_flavor != flavor:
            assert not (Path(path) / "Addon").exists()


@pytest.mark.parametrize(
    "other_flavor",
    [
        "mainline",
        "wrath",
        "vanilla",
    ],
)
def test_build_link_auto_and_other(fs_env: FSEnv, other_flavor: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build(["--link", "auto", "--link", other_flavor])

    assert isinstance(result.exception, SystemExit)


def test_build_non_unicode_config(fs_env: FSEnv) -> None:
    config_path = fs_env.write_config(get_basic_config())
    config_path.write_text(
        config_path.read_text().replace("Package", "包裹"), encoding="big5"
    )
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, EncodingError)


def test_build_overwriting_src_include(fs_env: FSEnv) -> None:
    fs_env.write_config(assign(get_basic_config(), "package.0.include", ["./Main.lua"]))
    fs_env.place_addon("basic")
    fs_env.place_file("Main.lua")

    result = invoke_build()

    assert result.success
    assert "already exists" in result.stderr


def test_build_overwriting_toc_include(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./Addon.toc"])
    )
    fs_env.place_addon("basic")
    fs_env.place_file("Addon.toc")

    result = invoke_build()

    assert result.success
    assert "already exists" in result.stderr


def test_build_addon_dir_exists_as_file(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon", parents=True)

    result = invoke_build()

    assert isinstance(result.exception, PathExistsError)


@pytest.mark.parametrize(
    "clean",
    [
        True,
        False,
    ],
)
def test_build_cleaning(fs_env: FSEnv, clean: bool) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    old = fs_env.place_file(
        f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/old", parents=True
    )

    args = ["--clean"] if clean else []
    result = invoke_build(args)

    assert result.success
    assert old.exists() != clean


def test_build_include_missing(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")

    result = invoke_build()

    assert result.success
    assert "none were found" in result.stderr


def test_build_include_dir(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./a-directory"])
    )
    fs_env.place_addon("basic")
    fs_env.place_dir("a-directory")

    result = invoke_build()

    assert result.success
    assert Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/a-directory").is_dir()


def test_build_toc_file_missing(fs_env: FSEnv) -> None:
    config = get_basic_config()
    glom(config, ("package.0.toc.files", T.append("NotExist.lua")))
    fs_env.write_config(config)
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, PathMissingError)


@pytest.mark.parametrize(
    "toc_suffix",
    [
        "",
        "_Wrath",
        "_Vanilla",
    ],
)
def test_build_gen_toc_overwrites(fs_env: FSEnv, toc_suffix: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    fs_env.place_file(f"Addon/Addon{toc_suffix}.toc")

    result = invoke_build()

    assert result.success
    assert "already exists" in result.stderr


def test_build_include_dir_overwrite_file(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./a", "./b/a"])
    )
    fs_env.place_addon("basic")
    fs_env.place_file("a")
    fs_env.place_dir("b/a", parents=True)

    result = invoke_build()

    assert isinstance(result.exception, PathExistsError)


def test_build_include_file_overwrite_file(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./a", "./b/a"])
    )
    fs_env.place_addon("basic")
    fs_env.place_file("a", text="first")
    fs_env.place_file("b/a", parents=True, text="last")

    result = invoke_build()

    assert result.success
    assert Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/a").read_text() == "last"


def test_build_include_dir_overwrite_dir(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./a", "./b/a"])
    )
    fs_env.place_addon("basic")
    fs_env.place_dir("a")
    fs_env.place_dir("b/a", parents=True)

    result = invoke_build()

    assert result.success
    assert Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/a").is_dir()


def test_build_include_file_overwrite_dir(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./a", "./b/a"])
    )
    fs_env.place_addon("basic")
    fs_env.place_dir("a")
    fs_env.place_file("b/a", parents=True)

    result = invoke_build()

    assert isinstance(result.exception, PathExistsError)


def test_build_toc_included(fs_env: FSEnv) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.include", ["./Addon.toc"])
    )
    fs_env.place_addon("basic")
    fs_env.place_dir("Addon.toc")

    result = invoke_build()

    assert isinstance(result.exception, PathExistsError)


@pytest.mark.parametrize("load_on_demand,expected", [(True, "1"), (False, "0")])
def test_build_toc_load_on_demand(
    fs_env: FSEnv, load_on_demand: bool, expected: str
) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.toc.tags.LoadOnDemand", load_on_demand)
    )
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert result.success

    for suffix, _ in SUFFIX_INTERFACE_PAIRS:
        toc_path = Path(
            f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/Addon{suffix}.toc"
        )
        toc = Toc.parse(toc_path)
        assert {("LoadOnDemand", expected)} <= toc.tags.items()


@pytest.mark.parametrize(
    "default_state,expected", [(True, "enabled"), (False, "disabled")]
)
def test_build_toc_default_state(
    fs_env: FSEnv, default_state: bool, expected: str
) -> None:
    fs_env.write_config(
        assign(get_basic_config(), "package.0.toc.tags.DefaultState", default_state)
    )
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert result.success

    for suffix, _ in SUFFIX_INTERFACE_PAIRS:
        toc_path = Path(
            f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/Addon{suffix}.toc"
        )
        toc = Toc.parse(toc_path)
        assert {("DefaultState", expected)} <= toc.tags.items()


@pytest.mark.parametrize(
    "tag_name",
    [
        "Dependencies",
        "OptionalDeps",
        "LoadWith",
        "LoadManagers",
        "SavedVariables",
        "SavedVariablesPerCharacter",
    ],
)
@pytest.mark.parametrize(
    "tag_value,expected", [([], ""), (["a"], "a"), (["a", "b", "c"], "a, b, c")]
)
def test_build_toc_list_type_tags(
    fs_env: FSEnv, tag_name: str, tag_value: list[str], expected: str
) -> None:
    fs_env.write_config(
        assign(get_basic_config(), f"package.0.toc.tags.{tag_name}", tag_value)
    )
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert result.success

    for suffix, _ in SUFFIX_INTERFACE_PAIRS:
        toc_path = Path(
            f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/Addon{suffix}.toc"
        )
        toc = Toc.parse(toc_path)
        assert {(tag_name, expected)} <= toc.tags.items()


@pytest.mark.parametrize("bad_tag", ["foo bar", "foo\nbar", "foo:bar"])
def test_build_toc_bad_tags(fs_env: FSEnv, bad_tag: str) -> None:
    config = get_basic_config()
    config["package"][0]["toc"]["tags"][bad_tag] = "value"
    fs_env.write_config(config)
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    result = invoke_build()

    assert isinstance(result.exception, TagError)


def test_build_watch_edit_source_file(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    addon_path = fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    changing_file_path = addon_path / "Main.lua"
    original_text = "original"
    new_text = "updated"
    assert original_text != new_text

    changing_file_path.write_text(original_text)

    def edit_file(*args: Any, **kwargs: Any) -> Iterator[Iterable[Path]]:
        changing_file_path.write_text(new_text)
        yield {changing_file_path.resolve()}

    with patch("tests.cmd_util.build.watch_paths", side_effect=edit_file):
        result = invoke_build(["--watch"])

    assert result.success

    new_output_file_path = Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/Main.lua")
    assert new_output_file_path.read_text() == new_text


def test_build_watch_new_source_file(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())
    addon_path = fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    # create a new file in a directory
    new_file_path = addon_path / "Dir" / "New.lua"
    new_text = "new"

    def create_file(*args: Any, **kwargs: Any) -> Iterator[Iterable[Path]]:
        new_file_path.parent.mkdir()
        new_file_path.write_text(new_text)
        yield {new_file_path.resolve()}

    with patch("tests.cmd_util.build.watch_paths", side_effect=create_file):
        result = invoke_build(["--watch"])

    assert result.success

    new_output_file_path = Path(
        f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}/Addon/Dir/New.lua"
    )
    assert new_output_file_path.read_text() == new_text


def test_build_watch_config_file(fs_env: FSEnv) -> None:
    config = get_basic_config()
    fs_env.write_config(config)
    fs_env.place_addon("basic")
    fs_env.place_file("LICENSE")

    new_version = "9.9.9"
    new_text = "new"
    fs_env.place_file("New.txt", text=new_text)

    def edit_config(*args: Any, **kwargs: Any) -> Iterator[Iterable[Path]]:
        # do two arbitrary things that we can later test:
        # 1. add another include (so it will show up in the output dir)
        # 2. change the package version (so the output dir path changes)
        config["package"][0]["include"].append("./New.txt")
        config["version"] = new_version
        config_path = fs_env.write_config(config)
        yield {config_path.resolve()}

    with patch("tests.cmd_util.build.watch_paths", side_effect=edit_config):
        result = invoke_build(["--watch"])

    assert result.success

    assert (
        Path(f"dist/{PACKAGE_NAME}-{new_version}/Addon/New.txt").read_text() == new_text
    )
