import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner, Result
from pytest_mock import MockerFixture

from tests.fixtures import capsys_err, ref_config_real_path
from wap import cli
from wap.config import PackageConfig
from wap.exception import DevInstallException, ReleaseException

# Something about patching here is funny. Example:
# - DOES NOT WORK: wap.config.PackageConfig
# - DOES WORK: wap.cli.PackageConfig
# Not sure why.

# not using Path objects here because we need to test the json output from the cli
# commands
_TEST_BUILD_DIR = "/addon"
_TEST_ZIP_DIR = "/addon.zip"
_TEST_CURSEFORGE_FILE_ID = 27342
_TEST_RETAIL_WOW_ADDONS_PATH = Path("/World of Warcraft/_retail_/Interface/Addons")
_TEST_CLASSIC_WOW_ADDONS_PATH = Path("/World of Warcraft/_classic_/Interface/Addons")
_TEST_DEV_INSTALL_PATHS = [
    str(_TEST_RETAIL_WOW_ADDONS_PATH / "MyAddonDir1"),
    str(_TEST_RETAIL_WOW_ADDONS_PATH / "MyAddonDir2"),
]


@pytest.fixture
def cli_mock(
    mocker: MockerFixture,
    ref_config_real_path: PackageConfig,
) -> Mapping[str, MagicMock]:
    pacakage_config_mock = mocker.patch("wap.cli.PackageConfig", autospec=True)
    pacakage_config_mock.from_path.return_value = ref_config_real_path

    package_mock = mocker.patch("wap.cli.package", autospec=True)
    package_mock.build.return_value = Path(_TEST_BUILD_DIR)
    package_mock.zip.return_value = Path(_TEST_ZIP_DIR)
    package_mock.release.return_value = _TEST_CURSEFORGE_FILE_ID
    package_mock.dev_install.return_value = _TEST_DEV_INSTALL_PATHS

    wow_addons_path_class_mock = mocker.patch("wap.cli.WoWAddonsPath", autospec=True)
    wow_addons_path_mock = mocker.MagicMock()
    wow_addons_path_mock.type_ = "retail"
    wow_addons_path_class_mock.return_value = wow_addons_path_mock

    return {
        "pacakage_config_mock": pacakage_config_mock,
        "package_mock": package_mock,
        "wow_addons_path_mock": wow_addons_path_mock,
    }


def run_cli_base(
    args: tuple[str, ...], env: Optional[Mapping[str, str]] = None
) -> Result:
    if env is None:
        env = {}
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(
        cli.base,
        args=args,
        catch_exceptions=False,
        standalone_mode=False,
        env=env,
    )


def build_expected_json_output(
    config: PackageConfig,
    include_zip: bool = True,
    include_curseforge: bool = False,
    include_dev_install: bool = False,
    include_retail: bool = True,
    include_classic: bool = True,
) -> dict[str, Any]:
    ret = {}

    for wow_version_config in config.wow_version_configs:
        if (wow_version_config.type_ == "classic" and not include_classic) or (
            wow_version_config.type_ == "retail" and not include_retail
        ):
            continue
        version_object: dict[str, Any] = {
            "build_path": _TEST_BUILD_DIR,
        }

        if include_zip:
            version_object["zip_path"] = _TEST_ZIP_DIR

        if include_curseforge:
            version_object["curseforge_file_id"] = _TEST_CURSEFORGE_FILE_ID

        if include_dev_install:
            version_object["dev_install_paths"] = _TEST_DEV_INSTALL_PATHS

        ret[wow_version_config.type_] = version_object

    return ret


def test_cli_build(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:
    result = run_cli_base(args=("build",))

    json_output = json.loads(result.stdout)
    expected_json_output = build_expected_json_output(ref_config_real_path)

    assert json_output == expected_json_output


def test_cli_release(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:
    result = run_cli_base(
        args=("release", "--version", "0.1.2"),
        env={"WAP_CURSEFORGE_TOKEN": "my-api-token"},
    )

    json_output = json.loads(result.stdout)
    expected_json_output = build_expected_json_output(
        ref_config_real_path, include_curseforge=True
    )

    assert json_output == expected_json_output


def test_cli_release_without_cf_config(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:

    ref_config_real_path.curseforge_config = None

    with pytest.raises(ReleaseException):
        result = run_cli_base(
            args=("release", "--version", "0.1.2"),
            env={"WAP_CURSEFORGE_TOKEN": "my-api-token"},
        )


def test_cli_release_no_file_diff_bc_no_toc_gen(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:

    # delete all of the toc_configs so that retail and classic would be the same zip
    for dir_config in ref_config_real_path.dir_configs:
        dir_config.toc_config = None

    result = run_cli_base(
        args=("release", "--version", "0.1.2"),
        env={"WAP_CURSEFORGE_TOKEN": "my-api-token"},
    )

    assert "CurseForge will reject" in result.stderr


def test_cli_dev_install_normal(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:

    result = run_cli_base(
        args=("dev-install",),
        env={"WAP_WOW_ADDONS_PATH": str(_TEST_RETAIL_WOW_ADDONS_PATH)},
    )

    json_output = json.loads(result.stdout)
    expected_json_output = build_expected_json_output(
        ref_config_real_path,
        include_dev_install=True,
        include_classic=False,
        include_zip=False,
    )

    assert json_output == expected_json_output


def test_cli_dev_install_no_build_for_addon_path(
    cli_mock: Mapping[str, MagicMock],
    ref_config_real_path: PackageConfig,
) -> None:

    del ref_config_real_path.wow_version_configs[0]

    with pytest.raises(DevInstallException):
        run_cli_base(
            args=("dev-install",),
            env={"WAP_WOW_ADDONS_PATH": str(_TEST_CLASSIC_WOW_ADDONS_PATH)},
        )
