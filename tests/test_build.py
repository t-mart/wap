import json
from collections.abc import Iterable
from pathlib import Path

import pytest

from tests.fixtures import wow_dir_path
from tests.util import Environment, fileset, toc_fileset, toc_tagmap, zip_fileset
from wap.commands.common import (
    DEFAULT_ADDON_VERSION,
    DEFAULT_CONFIG_PATH,
    DEFAULT_OUTPUT_PATH,
    WAP_CONFIG_PATH_ENVVAR_NAME,
)
from wap.exception import BuildException, TocException


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
def test_build(
    env: Environment, config_path_from_cli: bool, default_output_path: bool
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
    )

    run_wap_args = ["build", "--json"]
    env_vars: dict[str, str] = {}

    if config_path_from_cli:
        run_wap_args.extend(["--config-path", str(DEFAULT_CONFIG_PATH)])
    else:
        env_vars[WAP_CONFIG_PATH_ENVVAR_NAME] = str(DEFAULT_CONFIG_PATH)

    if default_output_path:
        output_path = "/out/path"
        run_wap_args.extend(["--output-path", output_path])
    else:
        output_path = str(env.project_dir_path / DEFAULT_OUTPUT_PATH)

    result = env.run_wap(*run_wap_args, env_vars=env_vars)

    actual_json_output = json.loads(result.stdout)
    expected_build_files = {
        Path("Dir1/Dir1.toc"),
        Path("Dir1/Dir1.lua"),
        Path("Dir1/Sub/Another.lua"),
    }
    expected_toc_files = {
        "Dir1.lua",
        "Sub/Another.lua",
    }

    for wow_type, interface in [("retail", "90002"), ("classic", "11306")]:
        # check the stdout json
        assert (
            actual_json_output[wow_type]["build_dir_path"]
            == f"{output_path}/MyAddon-dev-{wow_type}"
        )
        assert (
            actual_json_output[wow_type]["zip_file_path"]
            == f"{output_path}/MyAddon-dev-{wow_type}.zip"
        )

        # check the files in the build dir
        actual_build_files = fileset(Path(f"{output_path}/MyAddon-dev-{wow_type}"))
        assert expected_build_files == actual_build_files

        # # check the files in the zip file
        actual_zip_files = zip_fileset(
            Path(f"{output_path}/MyAddon-dev-{wow_type}.zip")
        )
        assert expected_build_files == actual_zip_files

        expected_toc_tags = {
            "Title": "MyAddon Dir1",
            "Version": "dev",
            "Interface": interface,
        }

        # check the tags in the toc
        assert expected_toc_files == toc_fileset(
            Path(f"{output_path}/MyAddon-dev-{wow_type}/Dir1/Dir1.toc")
        )

        # check the files in the toc
        assert expected_toc_tags == toc_tagmap(
            Path(f"{output_path}/MyAddon-dev-{wow_type}/Dir1/Dir1.toc")
        )


RUN_ARGS_BUILD = [
    (("build", "--json"),),
    (
        (
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
            "--json",
        ),
    ),
    (("dev-install", "--wow-addons-path", str(wow_dir_path("retail")), "--json"),),
]


@pytest.mark.parametrize(
    ("run_args",), RUN_ARGS_BUILD, ids=["build", "upload", "dev-install"]
)
class TestCommandsThatBuild:
    """
    These tests test commands that build (build, dev-install, upload)
    """

    def test_build_overwrites_existing(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="basic",
            wow_dir_name="retail",
        )

        # runs two consecutive invocations. the second will overwrite files from the
        # first.
        env.run_wap(*run_args)
        env.run_wap(*run_args)

    @pytest.mark.parametrize(
        ("config_name",),
        [
            ("dir_path_does_not_exist",),
            ("dir_path_is_file",),
        ],
        ids=["dir does not exist", "dir is file"],
    )
    def test_build_dir_path_not_dir(
        self, env: Environment, config_name: str, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name=config_name,
            wow_dir_name="retail",
        )

        with pytest.raises(BuildException, match=r"is not a directory"):
            env.run_wap(*run_args)

    @pytest.mark.parametrize(
        ("project_dir_name"),
        [
            "with_existing_toc_file",
            "with_existing_toc_dir",
        ],
        ids=["existing TOC file", "existing TOC dir"],
    )
    def test_build_toc_file_exists(
        self, env: Environment, run_args: Iterable[str], project_dir_name: str
    ) -> None:
        env.prepare(
            project_dir_name=project_dir_name,
            config_file_name="basic",
            wow_dir_name="retail",
        )

        result = env.run_wap(*run_args)

        assert "will be overwritten" in result.stderr

    def test_build_toc_file_does_not_exist(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="toc_file_does_not_exist",
            wow_dir_name="retail",
        )

        with pytest.raises(TocException, match=r"but it does not exist"):
            env.run_wap(*run_args)

    @pytest.mark.parametrize(
        ("config_file_name"),
        [
            "toc_overwritten_interface_tag",
            "toc_overwritten_version_tag",
        ],
        ids=("interface", "version"),
    )
    def test_build_toc_tag_overwritten(
        self, env: Environment, run_args: Iterable[str], config_file_name: str
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name=config_file_name,
            wow_dir_name="retail",
        )

        result = env.run_wap(*run_args)

        assert "Overwriting wap-provided tag" in result.stderr

    def test_build_toc_custom_tag_without_prefix(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="toc_custom_tag_without_prefix",
            wow_dir_name="retail",
        )

        result = env.run_wap(*run_args)

        assert "TOC user-specified tag" in result.stderr
