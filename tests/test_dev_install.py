import json

import pytest
from click.exceptions import BadParameter

from tests.util import Environment, fileset
from tests.util import normalized_path_string as ps
from wap.commands.common import (
    DEFAULT_CONFIG_PATH,
    WAP_CONFIG_PATH_ENVVAR_NAME,
    WAP_WOW_ADDONS_PATH_ENVVAR_NAME,
)
from wap.exception import DevInstallException


@pytest.mark.parametrize(
    ("wow_dir_name", "wow_type"),
    [("retail", "retail"), ("classic", "classic")],
    ids=["retail", "classic"],
)
@pytest.mark.parametrize(
    "wow_addons_path_from_cli",
    [True, False],
    ids=["addons path from cli", "addons path from env var"],
)
@pytest.mark.parametrize(
    "config_path_from_cli",
    [True, False],
    ids=["config path from cli", "config path from env var"],
)
@pytest.mark.parametrize(
    "use_addon_default_version",
    [True, False],
    ids=["default version", "specified version"],
)
def test_dev_install(
    env: Environment,
    wow_dir_name: str,
    wow_type: str,
    wow_addons_path_from_cli: bool,
    config_path_from_cli: bool,
    use_addon_default_version: bool,
) -> None:

    if use_addon_default_version:
        addon_version = "dev"
        project_dir_name = "basic-built"
    else:
        addon_version = "1.2.3"
        project_dir_name = "basic_built_version_1.2.3"

    env.prepare(
        project_dir_name=project_dir_name,
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

    if not use_addon_default_version:
        run_wap_args.extend(["--addon-version", addon_version])

    result = env.run_wap(*run_wap_args, env_vars=env_vars)

    actual_json_output = json.loads(result.stdout)

    # check the stdout json
    assert set(actual_json_output[wow_type]["installed_dir_paths"]) == {
        (ps(str(env.wow_dir_path / "Dir1")))
    }

    assert fileset(
        env.project_dir_path / "dist" / f"MyAddon-{addon_version}-{wow_type}"
    ) == fileset(env.wow_dir_path)


def test_dev_install_overwrites(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic-built",
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
        project_dir_name="basic-built",
        config_file_name="basic",
        wow_dir_name=wow_dir_name,
    )

    with pytest.raises(BadParameter, match=r"does not look like a WoW addons"):
        env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))


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
        project_dir_name="basic-built",
        config_file_name="basic",
    )

    with pytest.raises(BadParameter, match=r"is not a directory"):
        env.run_wap("dev-install", "--wow-addons-path", wow_dir_path)


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
        project_dir_name="basic-built",
        config_file_name=config_file_name,
        wow_dir_name=wow_dir_name,
    )

    with pytest.raises(
        DevInstallException, match=r"No build exists for WoW addons path"
    ):
        env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))


@pytest.mark.parametrize(["wow_dir_name"], [["retail"], ["classic"]])
def test_dev_install_without_build(env: Environment, wow_dir_name: str) -> None:
    env.prepare(
        project_dir_name="basic", config_file_name="basic", wow_dir_name=wow_dir_name
    )

    assert env.wow_dir_path

    with pytest.raises(DevInstallException, match=r"Build directory .+ not found"):
        env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))
