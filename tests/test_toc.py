from pathlib import Path
from typing import Callable

import attr
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from tests.fixtures import capsys_err
from wap import toc
from wap.exception import BuildException


@attr.s(kw_only=True, auto_attribs=True, frozen=True, order=False)
class TOCEnv:
    addon_version: str
    interface_version: str
    tags: dict[str, str]
    files: list[Path]
    toc_path: Path
    fs: FakeFilesystem


@pytest.fixture
def toc_env(fs: FakeFilesystem) -> TOCEnv:
    """
    Sets up data used by test functions in this module. Also creates TOC files that
    should exist in the error-free case (the tests may augment the files to exhibit
    certain behaviors)

    This data might otherwise live in global variables, but with pyfakefs, Path objects
    need to be created inside a function (there is a workaround, but it seems like even
    more boilerplate/ugliness)
    """

    toc_env = TOCEnv(
        addon_version="0.0.1",
        interface_version="90002",
        tags={
            "Title": "MyAddon",
            "Author": "Tim Martin",
        },
        files=[
            Path("MyAddon.lua"),
            Path("MyAddonLib.lua"),
        ],
        toc_path=Path("MyAddon.toc"),
        fs=fs,
    )

    for file in toc_env.files:
        fs.create_file(file)

    return toc_env


def run_write_toc(toc_env: TOCEnv) -> None:
    toc.write_toc(
        toc_path=toc_env.toc_path,
        addon_version=toc_env.addon_version,
        interface_version=toc_env.interface_version,
        tags=toc_env.tags,
        files=toc_env.files,
    )


def test_toc_contents_normal(
    toc_env: TOCEnv,
) -> None:
    run_write_toc(toc_env)

    with toc_env.toc_path.open("r") as toc_file:
        lines = {line.strip() for line in toc_file}

    must_haves = {f"## {key}: {value}" for key, value in toc_env.tags.items()} | {
        f"{file}" for file in toc_env.files
    }

    assert must_haves <= lines


def test_overwrite_toc_file_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    toc_env.fs.create_file(toc_env.toc_path)

    run_write_toc(toc_env)

    assert "Overwriting" in capsys_err()


def test_overwrite_toc_dir_exc(
    toc_env: TOCEnv,
) -> None:
    toc_env.fs.create_dir(toc_env.toc_path)

    with pytest.raises(BuildException):
        run_write_toc(toc_env)


def test_no_tags_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    run_write_toc(attr.evolve(toc_env, tags={}))

    assert "No user-specified tags" in capsys_err()


def test_no_files_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    run_write_toc(attr.evolve(toc_env, files=[]))

    assert "No files" in capsys_err()


def test_preexisting_tag_that_wap_adds_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    run_write_toc(
        attr.evolve(
            toc_env,
            tags={
                "Version": "9.9.9",
                "Interface": "99999",
                **toc_env.tags,
            },
        )
    )

    assert "Version TOC tag found" in capsys_err()
    assert "Interface TOC tag found" in capsys_err()


def test_non_existant_file_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    run_write_toc(attr.evolve(toc_env, files=toc_env.files + [Path("NewFile.lua")]))

    assert "does not exist" in capsys_err()


def test_non_prefixed_tag_warn(
    capsys_err: Callable[[], str],
    toc_env: TOCEnv,
) -> None:
    run_write_toc(
        attr.evolve(
            toc_env,
            tags={"SomeTag": "somevalue"},
        )
    )

    assert "prefix" in capsys_err()
