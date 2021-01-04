import os
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Callable, Optional
from unittest.mock import MagicMock, create_autospec, patch
from zipfile import ZipFile

import attr
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from tests.fixtures import (
    PackageEnv,
    capsys_err,
    classic_wow_addons_path,
    package_env,
    ref_config,
    ref_config_obj,
    retail_wow_addons_path,
    wow_addons_path_parameterized,
)
from wap import package
from wap.addonspath import WoWAddonsPath
from wap.config import DirConfig, WowVersionConfig
from wap.curseforge import CurseForgeAPI
from wap.exception import BuildException, DevInstallException, WowAddonPathException

_TEST_ADDON_VERSION = "1.2.3"
_TEST_CF_VERSION_ID = 5234
_TEST_CF_FILE_ID = 33456


@pytest.fixture
def mock_curseforge_api() -> CurseForgeAPI:
    curseforge_api = CurseForgeAPI(api_token="wasd")

    curseforge_api.get_version_id = create_autospec(  # type: ignore
        spec=curseforge_api.get_version_id
    )
    curseforge_api.get_version_id.return_value = _TEST_CF_VERSION_ID  # type: ignore

    curseforge_api.upload_addon_file = create_autospec(  # type: ignore
        spec=curseforge_api.upload_addon_file
    )
    curseforge_api.upload_addon_file.return_value = _TEST_CF_FILE_ID  # type: ignore

    return curseforge_api


def write_toc_mock_side_effect() -> Callable[..., None]:
    def write_toc_mock(
        toc_path: Path,
        addon_version: str,
        interface_version: str,
        tags: Mapping[str, str],
        files: Sequence[Path],
    ) -> None:
        toc_path.touch()

    return write_toc_mock


def get_files(*search_dirs: Path) -> set[Path]:
    """
    Walk all search dirs and produce a set of paths for files within them
    """
    files = set()
    for search_dir in search_dirs:
        for dirpath, _, filenames in os.walk(search_dir):
            files |= set(Path(dirpath) / file for file in filenames)

    return files


def check_build_dir(
    package_env: PackageEnv,
    dir_configs: list[DirConfig],
    build_path: Path,
    wow_version: WowVersionConfig,
) -> None:

    assert build_path.is_dir()
    assert _TEST_ADDON_VERSION in build_path.name
    assert wow_version.type_ in build_path.name

    source_files: set[Path] = set()
    for dir_config in dir_configs:
        source_files |= get_files(package_env.addon_root_path / dir_config.path)
        if dir_config.toc_config:
            # add a toc to the expected files if it will be generated
            source_files.add(
                package_env.addon_root_path
                / dir_config.path
                / f"{dir_config.path.name}.toc"
            )

    for source_file in source_files:
        assert (
            build_path / source_file.relative_to(package_env.addon_root_path)
        ).exists()


def check_zip_file(
    zip_path: Path,
    wow_version: WowVersionConfig,
    capsys_err: Callable[[], str],
    package_env: PackageEnv,
) -> None:

    assert zip_path.is_file()
    assert zip_path.suffix == ".zip"
    assert _TEST_ADDON_VERSION in zip_path.name
    assert wow_version.type_ in zip_path.name

    with ZipFile(zip_path, mode="r") as zip_file:
        zipped_files = {
            (package_env.addon_root_path / Path(zip_info.filename))
            for zip_info in zip_file.filelist
            if not zip_info.is_dir()
        }

    expected_files = {path for path in get_files(package_env.addon_root_path)}

    assert zipped_files == expected_files

    assert "Zipped package" in capsys_err()


def test_build_normal(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]

    build_path = (
        package_env.output_path
        / f"{config.name}-{_TEST_ADDON_VERSION}-{wow_version.type_}"
    )
    # garbage file that tests that deletions work properly
    package_env.fs.create_dir(build_path / "will-be-deleted.lua")

    # write_toc is not the SUT, mock it to keep tests separate and not have cascading
    # failures.
    with patch(
        "wap.package.write_toc",
        new=MagicMock(side_effect=write_toc_mock_side_effect()),
    ):
        build_path_generated = package.build(
            config_path=package_env.config_path,
            package_name=config.name,
            dir_configs=config.dir_configs,
            output_path=package_env.output_path,
            addon_version=_TEST_ADDON_VERSION,
            wow_version_config=wow_version,
        )

    assert build_path_generated == build_path

    check_build_dir(
        package_env=package_env,
        dir_configs=config.dir_configs,
        build_path=build_path,
        wow_version=wow_version,
    )

    assert "Built package" in capsys_err()


def test_build_dir_path_is_not_dir(package_env: PackageEnv) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]

    non_dir_dir = package_env.config_path.parent / "NotADir"
    non_dir_dir.touch()
    config.dir_configs.append(
        DirConfig(path=non_dir_dir.relative_to(package_env.config_path.parent))
    )

    with pytest.raises(BuildException):
        with patch(
            "wap.package.write_toc",
            new=MagicMock(side_effect=write_toc_mock_side_effect()),
        ):
            package.build(
                config_path=package_env.config_path,
                package_name=config.name,
                dir_configs=config.dir_configs,
                output_path=package_env.output_path,
                addon_version=_TEST_ADDON_VERSION,
                wow_version_config=wow_version,
            )


def test_build_no_toc(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]

    no_toc_dir_config = attr.evolve(config.dir_configs[0], toc_config=None)
    dir_configs = [no_toc_dir_config]

    with patch(
        "wap.package.write_toc",
        new=MagicMock(side_effect=write_toc_mock_side_effect()),
    ):
        build_path = package.build(
            config_path=package_env.config_path,
            package_name=config.name,
            dir_configs=dir_configs,
            output_path=package_env.output_path,
            addon_version=_TEST_ADDON_VERSION,
            wow_version_config=wow_version,
        )

    check_build_dir(
        package_env=package_env,
        dir_configs=dir_configs,
        build_path=build_path,
        wow_version=wow_version,
    )

    assert "does not have expected TOC file" in capsys_err()


def test_zip_normal(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]

    zip_path = (
        package_env.output_path
        / f"{config.name}-{_TEST_ADDON_VERSION}-{wow_version.type_}.zip"
    )
    # garbage zip that tests that deletions work properly
    package_env.fs.create_file(zip_path)

    zip_path_generated = package.zip(
        build_path=package_env.addon_root_path,
        package_name=config.name,
        output_path=package_env.output_path,
        addon_version=_TEST_ADDON_VERSION,
        wow_version_config=wow_version,
    )

    assert zip_path_generated == zip_path

    check_zip_file(
        zip_path=zip_path_generated,
        wow_version=wow_version,
        capsys_err=capsys_err,
        package_env=package_env,
    )


@pytest.mark.parametrize(
    "ext, changelog_type",
    [
        (
            ".md",
            "markdown",
        ),
        (
            ".MD",
            "markdown",
        ),
        (
            ".html",
            "html",
        ),
        (
            ".txt",
            "text",
        ),
        (
            ".unknown",
            "text",
        ),
    ],
)
def test_release_changelog_types(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
    mock_curseforge_api: CurseForgeAPI,
    ext: str,
    changelog_type: str,
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]
    assert config.curseforge_config is not None
    changelog_path = (
        package_env.config_path.parent / config.curseforge_config.changelog_path
    ).with_suffix(ext)
    changelog_path.touch()
    package_zip_path = Path("/theZip.zip")
    package_zip_path.touch()

    file_id = package.release(
        wow_version=wow_version,
        package_name=config.name,
        package_zip_path=package_zip_path,
        addon_version=_TEST_ADDON_VERSION,
        release_type="doesn't matter",
        project_id="4567",
        changelog_path=changelog_path,
        curseforge_api=mock_curseforge_api,
        addon_name="test_addon",
    )

    upload_call_args = mock_curseforge_api.upload_addon_file.call_args  # type: ignore
    assert upload_call_args.kwargs["changelog_type"] == changelog_type
    assert file_id == _TEST_CF_FILE_ID


@pytest.mark.parametrize(
    "addon_name",
    [None, "test_addon"],
)
def test_release_log_output(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
    mock_curseforge_api: CurseForgeAPI,
    addon_name: Optional[str],
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]
    assert config.curseforge_config is not None
    changelog_path = (
        package_env.config_path.parent / config.curseforge_config.changelog_path
    )
    package_zip_path = Path("/theZip.zip")
    package_zip_path.touch()

    package.release(
        wow_version=wow_version,
        package_name=config.name,
        package_zip_path=package_zip_path,
        addon_version=_TEST_ADDON_VERSION,
        release_type="doesn't matter",
        project_id="4567",
        changelog_path=changelog_path,
        curseforge_api=mock_curseforge_api,
        addon_name=addon_name,
    )

    if addon_name is None:
        assert "to CurseForge with file_id" in capsys_err()
    else:
        assert "to CurseForge at https://" in capsys_err()


def test_release_changelog_file_not_exist(
    package_env: PackageEnv,
    mock_curseforge_api: CurseForgeAPI,
) -> None:
    config = package_env.config
    wow_version = package_env.config.wow_version_configs[0]
    assert config.curseforge_config is not None
    changelog_path = (
        package_env.config_path.parent
        / "does_not_exist"
        / config.curseforge_config.changelog_path
    )
    package_zip_path = Path("/theZip.zip")
    package_zip_path.touch()

    with pytest.raises(BuildException):
        package.release(
            wow_version=wow_version,
            package_name=config.name,
            package_zip_path=package_zip_path,
            addon_version=_TEST_ADDON_VERSION,
            release_type="doesn't matter",
            project_id="4567",
            changelog_path=changelog_path,
            curseforge_api=mock_curseforge_api,
            addon_name=None,
        )


@pytest.mark.parametrize(
    "wow_addons_path_parameterized",
    ["retail", "classic"],
    indirect=True,
)
def test_dev_install_normal(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
    wow_addons_path_parameterized: WoWAddonsPath,
) -> None:
    # don't need to package.build() prior. callers will have built on their own
    config = package_env.config

    for dir_config in config.dir_configs:
        # first put addon dirs in output_dir
        # this isn't quite how the output dir looks (it's output_dir/name/dirs, not
        # output_dir/dirs), FYI
        shutil.copytree(
            src=package_env.addon_root_path / dir_config.path,
            dst=package_env.output_path / dir_config.path,
        )

        # also, to ensure this dev_install can delete existing addon installations
        # in the wow addons folder, build those dirs with some garbage files.
        package_env.fs.create_file(
            wow_addons_path_parameterized.path / dir_config.path / "will-be-deleted.txt"
        )

    package.dev_install(
        build_path=package_env.output_path,
        package_name=config.name,
        wow_addons_path=wow_addons_path_parameterized,
    )

    installed_files = {
        path.relative_to(wow_addons_path_parameterized.path)
        for path in get_files(wow_addons_path_parameterized.path)
    }

    source_files = {
        path.relative_to(package_env.output_path)
        for path in get_files(package_env.output_path)
    }

    assert installed_files == source_files
    assert "Installed" in capsys_err()


def test_dev_install_non_dir_files(
    package_env: PackageEnv,
    retail_wow_addons_path: WoWAddonsPath,
) -> None:
    config = package_env.config

    package_env.fs.create_file(package_env.output_path / "non-dir-file.lua")

    with pytest.raises(DevInstallException):
        package.dev_install(
            build_path=package_env.output_path,
            package_name=config.name,
            wow_addons_path=retail_wow_addons_path,
        )


def test_dev_wow_addons_path_normal(fs: FakeFilesystem) -> None:
    path = Path("/") / "World of Warcraft" / "_classic_" / "Interface" / "AddOns"
    path.mkdir(parents=True)

    wap = WoWAddonsPath(path=path)

    assert wap.type_ == "classic"


def test_wow_addons_path_dir_not_dir(fs: FakeFilesystem) -> None:
    path = Path("/") / "World of Warcraft" / "_classic_" / "Interface" / "AddOns"
    path.parent.mkdir(parents=True)
    path.touch()

    with pytest.raises(WowAddonPathException):
        WoWAddonsPath(path=path)


def test_wow_addons_path_dir_too_few_parts(fs: FakeFilesystem) -> None:
    path = Path("/") / "Interface" / "AddOns"
    path.mkdir(parents=True)

    with pytest.raises(WowAddonPathException):
        WoWAddonsPath(path=path)


def test_wow_addons_path_dir_wrong_parts(fs: FakeFilesystem) -> None:
    paths = [
        Path("/World of Wapcraft/_classic_/Interface/AddOns"),
        Path("/World of Warcraft/_classic_/Outerface/AddOns"),
        Path("/World of Warcraft/_classic_/Interface/AddOffs"),
    ]

    for path in paths:
        path.mkdir(parents=True)

        with pytest.raises(WowAddonPathException):
            WoWAddonsPath(path=path)


def test_wow_addons_path_bad_type(fs: FakeFilesystem) -> None:
    path = Path("/") / "World of Warcraft" / "neither" / "Interface" / "AddOns"
    path.mkdir(parents=True)

    with pytest.raises(WowAddonPathException):
        WoWAddonsPath(path=path)
