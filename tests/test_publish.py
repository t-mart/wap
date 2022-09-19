from __future__ import annotations

import hashlib
import random
import string
import uuid
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from zipfile import ZipFile

import pytest
from attrs import frozen
from glom import assign, delete
from respx.router import MockRouter

from tests.cmd_util import invoke_publish
from tests.curseforge_request import CFUploadRequestContent
from tests.fixture.config import get_basic_config
from tests.fixture.curseforge import CURSEFORGE_TOKEN
from tests.fixture.fsenv import FSEnv
from wap.exception import ConfigException, CurseForgeAPIException, PathMissingException

PACKAGE_NAME = get_basic_config()["name"]
PACKAGE_VERSION = get_basic_config()["version"]


@frozen(kw_only=True)
class File:
    """A file in an archive. Contents are represented by their hash only."""

    path: Path
    content_hash: bytes

    @staticmethod
    def _hash(data: bytes) -> bytes:
        return hashlib.new("sha256", data).digest()

    @classmethod
    def from_path(cls, path: Path, root_at: Path) -> File:
        return cls(
            path=path.relative_to(root_at), content_hash=cls._hash(path.read_bytes())
        )

    @classmethod
    def from_zip_path(cls, zipfile: ZipFile, name: str) -> File:
        with zipfile.open(name) as f:
            return cls(path=Path(name), content_hash=cls._hash(f.read()))


@frozen(kw_only=True)
class Archive:
    """
    An archive represents a collection of files, such as a filesystem directory or in a
    zip file.
    """

    files: set[File]

    @classmethod
    def from_dir(cls, dir: Path, root_at: Path) -> Archive:
        return cls(
            files={
                File.from_path(path, root_at)
                for path in dir.rglob("*")
                if path.is_file()
            }
        )

    @classmethod
    def from_zip(cls, source: Path | BinaryIO) -> Archive:
        zip_file = ZipFile(source)
        return cls(
            files={
                File.from_zip_path(zip_file, zip_info.filename)
                for zip_info in zip_file.infolist()
                if not zip_info.is_dir()
            }
        )


def test_publish_normal(fs_env: FSEnv, cf_api_respx: MockRouter) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert result.success

    dir_path = Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}")
    zip_path = Path(f"dist/{PACKAGE_NAME}-{PACKAGE_VERSION}.zip")

    assert zip_path.is_file()

    dir_archive = Archive.from_dir(dir_path, root_at=dir_path)
    zip_archive = Archive.from_zip(zip_path)
    assert dir_archive == zip_archive

    versions_route = cf_api_respx.routes["versions"]
    assert versions_route
    assert versions_route.called

    upload_file_route = cf_api_respx.routes["upload-file"]
    assert upload_file_route

    req_content = CFUploadRequestContent.from_request(
        upload_file_route.calls[0].request
    )
    assert (
        req_content.metadata.items()
        >= {
            "changelog": "",
            "changelogType": "text",
            "displayName": f"{PACKAGE_NAME}-{PACKAGE_VERSION}",
            "releaseType": "alpha",
        }.items()
    )
    # order doesn't matter for versions, so test them this way
    assert set(req_content.metadata["gameVersions"]) == {1001, 1002, 1003}

    assert req_content.file_content_type == "application/zip"
    assert req_content.file_name == f"{PACKAGE_NAME}-{PACKAGE_VERSION}.zip"

    request_archive = Archive.from_zip(BytesIO(req_content.file_stream))
    assert request_archive == zip_archive


def test_publish_without_publish_config(fs_env: FSEnv) -> None:
    fs_env.write_config(delete(get_basic_config(), "publish"))

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert isinstance(result.exception, ConfigException)


def test_publish_without_cf_token(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_publish()

    assert isinstance(result.exception, SystemExit)


@pytest.mark.parametrize("cl_type", ["markdown", "text", "html"])
def test_publish_changelog_explicit_type(
    fs_env: FSEnv, cf_api_respx: MockRouter, cl_type: str | None
) -> None:
    # this test also tests the case of no changelog file/text being defined.
    config = get_basic_config()
    changelog_path = "./the-changelog"
    assign(config, "publish.curseforge.changelogFile", changelog_path)
    fs_env.place_file(changelog_path)

    assign(config, "publish.curseforge.changelogType", cl_type)
    expected_type = cl_type

    fs_env.write_config(config)
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert result.success

    upload_file_route = cf_api_respx.routes["upload-file"]
    assert upload_file_route
    req_content = CFUploadRequestContent.from_request(
        upload_file_route.calls[0].request
    )
    assert req_content.metadata["changelogType"] == expected_type
    assert req_content.metadata["changelog"] == ""


@pytest.mark.parametrize(
    "cl_file,expected_type",
    [
        ("cl.md", "markdown"),
        ("cl.markdown", "markdown"),
        ("cl.mArKdOwN", "markdown"),
        ("cl.txt", "text"),
        ("cl.TXT", "text"),
        ("cl.html", "html"),
        ("cl.huh", "text"),
    ],
)
def test_publish_auto_changelog_type_determination(
    fs_env: FSEnv, cf_api_respx: MockRouter, cl_file: str, expected_type: str
) -> None:
    config = get_basic_config()
    assign(config, "publish.curseforge.changelogFile", f"./{cl_file}")
    changelog_text = "".join(random.choice(string.ascii_letters) for _ in range(10))
    fs_env.place_file(cl_file, text=changelog_text)

    fs_env.write_config(config)
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert result.success

    upload_file_route = cf_api_respx.routes["upload-file"]
    assert upload_file_route
    req_content = CFUploadRequestContent.from_request(
        upload_file_route.calls[0].request
    )
    assert req_content.metadata["changelogType"] == expected_type
    assert req_content.metadata["changelog"] == changelog_text


def test_publish_different_config_path(fs_env: FSEnv) -> None:
    config_path = "config.json"
    fs_env.write_config(get_basic_config(), "config.json")
    fs_env.place_output_dir("basic")

    result = invoke_publish(
        ["--curseforge-token", CURSEFORGE_TOKEN, "--config-path", config_path]
    )

    assert result.success


@pytest.mark.parametrize("placed_correctly", [True, False])
def test_publish_different_output_path(fs_env: FSEnv, placed_correctly: bool) -> None:
    fs_env.write_config(get_basic_config())
    output_path = "output"
    fs_env.place_output_dir(
        "basic", output_path if placed_correctly else "somewhere-else/"
    )

    result = invoke_publish(
        ["--curseforge-token", CURSEFORGE_TOKEN, "--output-path", output_path]
    )

    if placed_correctly:
        assert result.success
    else:
        assert isinstance(result.exception, PathMissingException)


@pytest.mark.parametrize("cmd_release_type", ["release", "alpha", "beta", None])
@pytest.mark.parametrize("config_release_type", ["release", "alpha", "beta", None])
def test_publish_release_types(
    fs_env: FSEnv,
    cf_api_respx: MockRouter,
    cmd_release_type: str | None,
    config_release_type: str | None,
) -> None:
    config = get_basic_config()
    if config_release_type:
        assign(config, "publish.curseforge.releaseType", config_release_type)
    fs_env.write_config(config)
    fs_env.place_output_dir("basic")

    args = ["--curseforge-token", CURSEFORGE_TOKEN]
    if cmd_release_type:
        args.extend(["--release-type", cmd_release_type])
    result = invoke_publish(args)

    assert result.success

    upload_file_route = cf_api_respx.routes["upload-file"]
    assert upload_file_route

    req_content = CFUploadRequestContent.from_request(
        upload_file_route.calls[0].request
    )
    expected_release_type = "alpha"
    if config_release_type:
        expected_release_type = config_release_type
    if cmd_release_type:
        expected_release_type = cmd_release_type
    # order doesn't matter for versions, so test them this way
    assert req_content.metadata["releaseType"] == expected_release_type

    if config_release_type is None and cmd_release_type is None:
        assert "No release type specified" in result.stderr


def test_publish_dry_run(
    fs_env: FSEnv,
    cf_api_respx: MockRouter,
) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN, "--dry-run"])

    assert result.success

    upload_file_route = cf_api_respx.routes["upload-file"]
    assert upload_file_route
    assert upload_file_route.call_count == 0


@pytest.mark.parametrize("token", ["malformed", "random"])
def test_publish_bad_auth(fs_env: FSEnv, token: str) -> None:
    fs_env.write_config(get_basic_config())
    fs_env.place_output_dir("basic")

    result = invoke_publish(
        ["--curseforge-token", token if token != "random" else str(uuid.uuid4())]
    )

    assert isinstance(result.exception, CurseForgeAPIException)


def test_publish_unknown_wow_version(fs_env: FSEnv) -> None:
    fs_env.write_config(assign(get_basic_config(), "wowVersions.mainline", "999.0.0"))
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert isinstance(result.exception, CurseForgeAPIException)


@pytest.mark.parametrize("with_slug", [True, False])
def test_publish_slug(fs_env: FSEnv, with_slug: bool) -> None:
    config = get_basic_config()
    if not with_slug:
        delete(config, "publish.curseforge.slug")
    fs_env.write_config(config)
    fs_env.place_output_dir("basic")

    result = invoke_publish(["--curseforge-token", CURSEFORGE_TOKEN])

    assert result.success

    if with_slug:
        assert "Upload available at https:" in result.stderr
    else:
        assert "Uploaded file" in result.stderr
