import json

import pytest

from tests.util import VERSION_ID_MAP, Environment, decode_file_upload_multipart_request
from wap.commands.common import (
    DEFAULT_ADDON_VERSION,
    DEFAULT_CONFIG_PATH,
    WAP_CONFIG_PATH_ENVVAR_NAME,
    WAP_CURSEFORGE_TOKEN_ENVVAR_NAME,
)
from wap.exception import ChangelogException, CurseForgeAPIException, UploadException


@pytest.mark.parametrize(
    ("curseforge_token_from_cli",),
    [(True,), (False,)],
    ids=["curseforge token from cli", "curseforge token from env var"],
)
@pytest.mark.parametrize(
    ("config_path_from_cli",),
    [(True,), (False,)],
    ids=["config path from cli", "config path from env var"],
)
@pytest.mark.parametrize(
    ("release_type",),
    [["alpha"], ["beta"], ["release"]],
)
@pytest.mark.parametrize(
    ("changelog_from_cli_options"),
    [(False,), (True,)],
    ids=["changelog from config", "changelog from cli options"],
)
def test_upload(
    env: Environment,
    curseforge_token_from_cli: bool,
    config_path_from_cli: bool,
    release_type: str,
    changelog_from_cli_options: bool,
) -> None:
    env.prepare(
        project_dir_name="basic_built_version_1.2.3",
        config_file_name="basic",
        wow_dir_name="retail",
    )

    addon_version = "1.2.3"

    run_wap_args = [
        "upload",
        "--addon-version",
        addon_version,
        "--release-type",
        release_type,
        "--json",
    ]

    if changelog_from_cli_options:
        changelog_type = "text"
        changelog_contents = "hello, there"
        run_wap_args.extend(
            [
                "--changelog-contents",
                changelog_contents,
                "--changelog-type",
                changelog_type,
            ]
        )
    else:
        # this is from the file
        changelog_contents = "This is my changelog.\n"
        changelog_type = "markdown"

    env_vars: dict[str, str] = {}

    curseforge_token = "abcd-1234"
    if curseforge_token_from_cli:
        run_wap_args.extend(["--curseforge-token", curseforge_token])
    else:
        env_vars[WAP_CURSEFORGE_TOKEN_ENVVAR_NAME] = curseforge_token

    if config_path_from_cli:
        run_wap_args.extend(["--config-path", str(DEFAULT_CONFIG_PATH)])
    else:
        env_vars[WAP_CONFIG_PATH_ENVVAR_NAME] = str(DEFAULT_CONFIG_PATH)

    result = env.run_wap(*run_wap_args, env_vars=env_vars)

    actual_json_output = json.loads(result.stdout)

    # request_history_idx refers to the index in the requests_mock.request_history
    # sequence where the file upload was made. we use this to inspect the data that
    # would be posted to CurseForge. Theses indexes are brittle and may change if wap
    # changes how it makes requests to CF, or if the order of the uploads for classic
    # and retail changes in the config file. be warned.
    for wow_type, request_history_idx in [
        ("retail", 1),
        ("classic", 2),
    ]:
        # check the stdout json
        assert actual_json_output[wow_type]["curseforge_upload_url"] == (
            f"https://www.curseforge.com/wow/addons/myaddon/files/{env.UPLOAD_FILE_ID}"
        )

        decoded_req = decode_file_upload_multipart_request(
            env.requests_mock.request_history[request_history_idx]
        )

        # check the filename of the upload
        assert decoded_req.file_name == f"MyAddon-{addon_version}-{wow_type}.zip"

        # check the data uploaded
        zip_path = env.project_dir_path / f"dist/MyAddon-{addon_version}-{wow_type}.zip"
        with zip_path.open("rb") as zip_file:
            zip_contents = zip_file.read()
        assert decoded_req.file_contents == zip_contents

        # check the metadata
        json_metadata = decoded_req.json_metadata
        assert json_metadata["changelog"] == changelog_contents
        assert json_metadata["changelogType"] == changelog_type
        assert json_metadata["displayName"] == f"MyAddon-{addon_version}-{wow_type}"
        assert json_metadata["gameVersions"] == [VERSION_ID_MAP[wow_type]]
        assert json_metadata["releaseType"] == release_type


def test_upload_no_curseforge_config(env: Environment) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="no_curseforge",
    )

    with pytest.raises(UploadException, match=r'A "curseforge" configuration section'):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


def test_upload_changelog_does_not_exist(env: Environment) -> None:
    env.prepare(
        project_dir_name="basic-built",
        config_file_name="curseforge_changelog_does_not_exist",
    )

    with pytest.raises(UploadException, match=r"but it is not a file"):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


@pytest.mark.parametrize(
    ["config_file_name", "changelog_file_name", "expected_changelog_type"],
    [
        ["basic", "CHANGELOG.md", "markdown"],
        # on windows, there is no case sensitivity on files and therefore, the result of
        # this run will be the same the previous
        ["curseforge_changelog_case_insensitive_ext", "CHANGELOG.MD", "markdown"],
        ["curseforge_changelog_html", "CHANGELOG.html", "html"],
        ["curseforge_changelog_markdown_long_ext", "CHANGELOG.markdown", "markdown"],
        ["curseforge_changelog_txt", "CHANGELOG.txt", "text"],
        ["curseforge_changelog_unknown_ext", "CHANGELOG.unknown", "text"],
    ],
)
def test_upload_changelog_extensions(
    env: Environment,
    config_file_name: str,
    changelog_file_name: str,
    expected_changelog_type: str,
) -> None:
    env.prepare(
        project_dir_name="basic-built",
        config_file_name=config_file_name,
    )

    # rename the changelog file
    orig_changelog = env.project_dir_path / "CHANGELOG.md"
    assert orig_changelog.exists()  # make sure this file is here before we test
    orig_changelog.rename(env.project_dir_path / changelog_file_name)

    env.run_wap(
        "upload",
        "--addon-version",
        DEFAULT_ADDON_VERSION,
        "--curseforge-token",
        "abc123",
    )

    decoded_req = decode_file_upload_multipart_request(
        env.requests_mock.request_history[1]
    )

    json_metadata = decoded_req.json_metadata
    assert json_metadata["changelogType"] == expected_changelog_type


def test_upload_failed_get_version_id_request(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic-built",
        config_file_name="basic",
        success_cf_get_version_id=False,
    )

    with pytest.raises(
        CurseForgeAPIException, match=r"version lookup has error status code"
    ):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


def test_upload_failed_upload_addon_file_request(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic-built",
        config_file_name="basic",
        success_cf_upload_addon_file=False,
    )

    with pytest.raises(
        CurseForgeAPIException, match=r"file upload has error status code"
    ):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


def test_upload_version_does_not_exist(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic-built",
        config_file_name="version_does_not_exist_on_cf",
        success_cf_upload_addon_file=False,
    )

    with pytest.raises(
        CurseForgeAPIException, match=r"could not be found on CurseForge"
    ):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


def test_upload_without_build(env: Environment) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
    )

    with pytest.raises(UploadException, match=r"Zip file .+ not found"):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
        )


@pytest.mark.parametrize(
    "cl_options",
    [("--changelog-type", "text"), ("--changelog-contents", "hello")],
    ids=["just type", "just contents"],
)
def test_upload_changelog_options_xor(env: Environment, cl_options: list[str]) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
    )

    with pytest.raises(ChangelogException, match=r"must be used together or"):
        env.run_wap(
            "upload",
            "--addon-version",
            DEFAULT_ADDON_VERSION,
            "--curseforge-token",
            "abc123",
            *cl_options,
        )
