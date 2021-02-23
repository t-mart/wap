import json
from pathlib import Path

import pytest
from click.exceptions import BadParameter

from tests.util import Environment, fileset
from tests.util import normalized_path_string as ps
from tests.util import toc_fileset, toc_tagmap
from wap.commands.common import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_OUTPUT_PATH,
    WAP_CONFIG_PATH_ENVVAR_NAME,
    WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
)
from wap.exception import DevInstallException


@pytest.mark.parametrize(
    ("wow_dir_name", "wow_type", "interface"),
    [("retail", "retail", "90002"), ("classic", "classic", "11306")],
    ids=["retail", "classic"],
)
@pytest.mark.parametrize(
    ("wow_addons_path_from_cli",),
    [(True,), (False,)],
    ids=["addons path from cli", "addons path from env var"],
)
@pytest.mark.parametrize(
    ("config_path_from_cli",),
    [(True,), (False,)],
    ids=["config path from cli", "config path from env var"],
)
@pytest.mark.parametrize(
    ("default_output_path",),
    [(True,), (False,)],
    ids=["default output path", "specified output path"],
)
def test_dev_install(
    env: Environment,
    wow_dir_name: str,
    wow_type: str,
    interface: str,
    wow_addons_path_from_cli: bool,
    config_path_from_cli: bool,
    default_output_path: bool,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
        wow_dir_name=wow_dir_name,
    )

    # wow_dir_path is an optional type, and mypy wants to be sure it's set (which it is)
    assert env.wow_dir_path is not None

    run_wap_args = ["dev-install", "--json"]
    env_vars: dict[str, str] = {}

    if wow_addons_path_from_cli:
        run_wap_args.extend(["--wow-addons-path", str(env.wow_dir_path)])
    else:
        env_vars[WAP_WOW_ADDONS_PATH_ENVVAR_NAME] = str(env.wow_dir_path)

    if config_path_from_cli:
        run_wap_args.extend(["--config-path", str(DEFAULT_CONFIG_PATH)])
    else:
        env_vars[WAP_CONFIG_PATH_ENVVAR_NAME] = str(DEFAULT_CONFIG_PATH)

    if default_output_path:
        output_path = str(DEFAULT_OUTPUT_PATH)
    else:
        output_path = "out/path"
        run_wap_args.extend(["--output-path", output_path])

    result = env.run_wap(*run_wap_args, env_vars=env_vars)

    actual_json_output = json.loads(result.stdout)
    expected_build_files = {
        Path("Dir1/Dir1.toc"),
        Path("Dir1/Dir1.lua"),
        Path("Dir1/Sub/Another.lua"),
    }
    expected_toc_files = {
        "Dir1.lua",
        "Sub\\Another.lua",
    }
    expected_toc_tags = {
        "Title": "MyAddon Dir1",
        "Version": "dev",
        "Interface": interface,
    }

    # check the stdout json
    assert actual_json_output[wow_type]["build_dir_path"] == ps(
        f"{output_path}/MyAddon-dev-{wow_type}"
    )
    assert set(actual_json_output[wow_type]["installed_dir_paths"]) == {
        (ps(str(env.wow_dir_path / "Dir1")))
    }

    # check the files in the build dir
    actual_build_files = fileset(
        env.project_dir_path / f"{output_path}/MyAddon-dev-{wow_type}"
    )
    assert expected_build_files == actual_build_files

    # check the tags in the toc
    assert expected_toc_files == toc_fileset(
        env.project_dir_path / f"{output_path}/MyAddon-dev-{wow_type}/Dir1/Dir1.toc"
    )
    assert expected_toc_files == toc_fileset(env.wow_dir_path / "Dir1/Dir1.toc")

    # check the files in the toc
    assert expected_toc_tags == toc_tagmap(
        env.project_dir_path / f"{output_path}/MyAddon-dev-{wow_type}/Dir1/Dir1.toc"
    )
    assert expected_toc_tags == toc_tagmap(env.wow_dir_path / "Dir1/Dir1.toc")


def test_dev_install_overwrites(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
        wow_dir_name="retail",
    )

    # runs two consecutive invocations. the second will overwrite files from the first.
    env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))
    env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))


@pytest.mark.parametrize(
    ("wow_dir_name"),
    [
        "bad_addons_part",
        "bad_interface_part",
        "bad_type_part",
        "bad_wow_part",
        "too_short",
    ],
)
def test_dev_install_bad_wow_addons_dir_format(
    env: Environment,
    wow_dir_name: str,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
        wow_dir_name=wow_dir_name,
    )

    with pytest.raises(BadParameter, match=r"does not look like a WoW addons"):
        env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path), "--json")


@pytest.mark.parametrize(
    ("wow_dir_path"),
    ["/does-not-exist", "/src/CHANGELOG.md"],
    ids=["does not exist", "is a file"],
)
def test_dev_install_wow_addons_dir_is_not_dir(
    env: Environment,
    wow_dir_path: str,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
    )

    with pytest.raises(BadParameter, match=r"is not a directory"):
        env.run_wap("dev-install", "--wow-addons-path", wow_dir_path, "--json")


@pytest.mark.parametrize(
    ("config_file_name", "wow_dir_name"),
    [
        [
            "version_only_classic",
            "retail",
        ],
        [
            "version_only_retail",
            "classic",
        ],
    ],
    ids=[
        "classic build into retail addons path",
        "retail build into classic addons path",
    ],
)
def test_dev_install_no_build_type_for_wow_addons_path_type(
    env: Environment,
    config_file_name: str,
    wow_dir_name: str,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name=config_file_name,
        wow_dir_name=wow_dir_name,
    )

    with pytest.raises(
        DevInstallException, match=r"No build exists for WoW addons path"
    ):
        env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path), "--json")
