from __future__ import annotations

import json
import os
import re
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar, Optional, Union
from zipfile import ZipFile
import arrow
from freezegun import freeze_time

import attr
from click.testing import CliRunner, Result
from pyfakefs.fake_filesystem import FakeFilesystem
from requests_mock import Mocker as RequestsMocker
from requests_mock.request import _RequestObjectProxy
from requests_toolbelt import MultipartDecoder
from requests_toolbelt.multipart.decoder import BodyPart

from tests import fixtures
from wap.commands import base
from wap.commands.common import DEFAULT_CONFIG_PATH
from wap.curseforge import CurseForgeAPI


def normalized_path_string(path: str) -> str:
    """
    Return a string representing a POSIX path with the correct path separators for this
    system. This is to aid test writing, so that tests may be written as if always on
    a POSIX system.

    For example, on Windows:
      path_string("foo/bar") -> "foo\\bar"
      path_string("foo\\bar") -> "foo\\bar"

    or on unix-like systems:
      path_string("foo/bar") -> "foo/bar"
      path_string("foo\\bar") -> "foo/bar"
    """
    return str(Path(PurePosixPath(path)))


def fileset(root: Path) -> set[Path]:
    return {
        (Path(dirpath) / filename).relative_to(root)
        for dirpath, _, filenames in os.walk(root)
        for filename in filenames
    }


def zip_fileset(zip_path: Path) -> set[Path]:
    with ZipFile(zip_path, mode="r") as zip_file:
        return {
            Path(zip_info.filename)
            for zip_info in zip_file.infolist()
            if not zip_info.is_dir()
        }


TOC_TAG_RE = re.compile(r"^## (?P<name>[^:]+): (?P<value>.+)$", flags=re.MULTILINE)
TOC_FILE_RE = re.compile(r"^(?P<filepath>[^#\s].*)$", flags=re.MULTILINE)


def toc_tagmap(path: Path) -> Mapping[str, str]:
    with path.open("r") as file:
        contents = file.read()

    return {match["name"]: match["value"] for match in TOC_TAG_RE.finditer(contents)}


def toc_fileset(path: Path) -> set[str]:
    with path.open("r") as file:
        contents = file.read()

    return {match["filepath"] for match in TOC_FILE_RE.finditer(contents)}


VERSION_ID_MAP = {"retail-dummy": 99, "retail": 100, "classic": 200}
GAME_VERSION_ID_MAP = {"retail": 1, "classic": 2}


@attr.s(kw_only=True, order=False, auto_attribs=True)
class Environment:
    """
    An environment for testing wap functionality
    """

    fs: FakeFilesystem
    requests_mock: RequestsMocker
    frozen_time: arrow.Arrow = attr.ib(
        default=arrow.get("2021-02-23T20:25:06.979923+00:00")
    )
    _config_file_path: Optional[Path] = attr.ib(default=None, init=False)
    _wow_dir_path: Optional[Path] = attr.ib(default=None, init=False)
    _project_dir_path: Optional[Path] = attr.ib(default=None, init=False)
    _prepared: bool = attr.ib(default=False, init=False)

    UPLOAD_FILE_ID: ClassVar[int] = 4321
    _SUCCESS_GET_VERSION_ID_JSON: ClassVar[Any] = [
        # this is a dummy 9.0.2. it has a lesser id which wap will ignore in favor of a
        # greater one
        {
            "id": VERSION_ID_MAP["retail-dummy"],
            "gameVersionTypeID": GAME_VERSION_ID_MAP["retail"],
            "name": "9.0.2",
            "slug": "9-0-2",
        },
        # the 9.0.2 that we want in tests (greater id)
        {
            "id": VERSION_ID_MAP["retail"],
            "gameVersionTypeID": GAME_VERSION_ID_MAP["retail"],
            "name": "9.0.2",
            "slug": "9-0-2",
        },
        # the classic we want in tests
        {
            "id": VERSION_ID_MAP["classic"],
            "gameVersionTypeID": GAME_VERSION_ID_MAP["classic"],
            "name": "1.13.6",
            "slug": "1-13-6",
        },
    ]
    _FAIL_GET_VERSION_ID_JSON: ClassVar[Any] = {"reason": "something went wrong"}
    _SUCCESS_UPLOAD_ADDON_FILE_JSON: ClassVar[Any] = {"id": UPLOAD_FILE_ID}
    _FAIL_UPLOAD_ADDON_FILE_JSON: ClassVar[Any] = _FAIL_GET_VERSION_ID_JSON

    @property
    def config_file_path(self) -> Optional[Path]:
        if not self._prepared:
            raise RuntimeError("Environment must first be prepare()-d")
        return self._config_file_path

    @property
    def wow_dir_path(self) -> Optional[Path]:
        if not self._prepared:
            raise RuntimeError("Environment must first be prepare()-d")
        return self._wow_dir_path

    @property
    def project_dir_path(self) -> Path:
        if not self._prepared:
            raise RuntimeError("Environment must first be prepare()-d")
        # this is always created during prepare()
        return self._project_dir_path  # type: ignore

    def prepare(
        self,
        project_dir_name: str,
        config_file_name: Optional[str] = None,
        wow_dir_name: Optional[str] = None,
        success_cf_get_version_id: bool = True,
        success_cf_upload_addon_file: bool = True,
    ) -> None:
        """
        - Creates a project directory
        - Creates a .wap.yml file
        - Creates a wow addons directory
        - Patches requests to the curseforge API
        """
        fs_root = Path("/")
        project_dir_path = fs_root / "src"

        project_dir_fixture = fixtures.project_dir_path(project_dir_name)
        self.fs.add_real_directory(
            project_dir_fixture, read_only=False, target_path=project_dir_path
        )

        config_file_path: Optional[Path] = None
        if config_file_name:
            config_file_fixture = fixtures.config_file_path(config_file_name)
            config_file_path = project_dir_path / DEFAULT_CONFIG_PATH
            self.fs.add_real_file(config_file_fixture, target_path=config_file_path)

        wow_dir_path: Optional[Path] = None
        if wow_dir_name:
            wow_dir_path = fixtures.wow_dir_path(wow_dir_name)
            self.fs.create_dir(wow_dir_path)

        self._config_file_path = config_file_path
        self._project_dir_path = project_dir_path
        self._wow_dir_path = wow_dir_path

        if success_cf_get_version_id:
            self.requests_mock.get(
                url=CurseForgeAPI.VERSION_ENDPOINT_URL,
                json=self._SUCCESS_GET_VERSION_ID_JSON,
            )
        else:
            self.requests_mock.get(
                url=CurseForgeAPI.VERSION_ENDPOINT_URL,
                json=self._FAIL_GET_VERSION_ID_JSON,
                status_code=400,
            )

        upload_addon_file_url_pattern_text = (
            CurseForgeAPI.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=r"\d+")
        )
        upload_addon_file_url_pattern = re.compile(upload_addon_file_url_pattern_text)
        if success_cf_upload_addon_file:
            self.requests_mock.post(
                url=upload_addon_file_url_pattern,
                json=self._SUCCESS_UPLOAD_ADDON_FILE_JSON,
            )
        else:
            self.requests_mock.post(
                url=upload_addon_file_url_pattern,
                json=self._FAIL_UPLOAD_ADDON_FILE_JSON,
                status_code=400,
            )

        self._prepared = True

    @contextmanager
    def _chdir_ctx(self, path: Path) -> Generator[None, None, None]:
        # this is a contextmanager so that we can set and reset the cwd. don't want to
        # pollute other tests' working directories
        old_cwd = os.getcwd()
        os.chdir(path)

        yield None

        os.chdir(old_cwd)

    def run_wap(
        self,
        *args: str,
        env_vars: Optional[Mapping[str, str]] = None,
        cwd: Optional[Path] = None,
    ) -> Result:
        if env_vars is None:
            env_vars = {}

        if cwd is None:
            cwd = self.project_dir_path

        runner = CliRunner(mix_stderr=False)

        with self._chdir_ctx(cwd):
            with freeze_time(self.frozen_time.datetime):
                return runner.invoke(
                    base,
                    args=args,
                    catch_exceptions=False,
                    standalone_mode=False,
                    env=env_vars,
                )


@attr.s(kw_only=True, frozen=True, auto_attribs=True, order=False)
class DecodedFileUploadMultipartRequest:
    json_metadata: Mapping[str, Union[str, list[int]]]
    file_contents: bytes
    file_name: str

    @classmethod
    def from_parts(
        cls, parts: tuple[BodyPart, ...]
    ) -> DecodedFileUploadMultipartRequest:
        json_metadata = json.loads(parts[0].content)
        file_contents = parts[1].content

        # lord, please forgive me for what i am about to do.
        # this is poor-man's content disposition header parsing for a specific key
        # we're trying to get the 'filename'. this may be brittle.
        # example value of headers[b'Content-Disposition'] (a bytes type):
        #   form-data; name="file"; filename="MyAddon-1.2.3-retail.zip"
        file_name = (
            parts[1]
            .headers[b"Content-Disposition"]
            .decode("utf-8")  # decode
            .split("; ")[-1]  # get the last semicolon-separated part
            .split("=")[-1][1:-1]  # get the value, remove quotes
        )

        return cls(
            json_metadata=json_metadata,
            file_contents=file_contents,
            file_name=file_name,
        )


def decode_file_upload_multipart_request(
    request_object_proxy: _RequestObjectProxy,
) -> DecodedFileUploadMultipartRequest:
    """
    Get the decoded parts of a multipart request from a history entry of
    requests_mock.request_history.

    This method exists because of limitations with requests_mock:
    - requests_mock.request_history[n].text is a property method that attempts utf-8
      decoding on the body of the request. But we have binary data in our body (we're
      uploading zip files), so the decode just fails (understandably). To workaround
      this, we abuse that we have access to the request itself at
      requests_mock.request_history[n]._request. Then we can access .body on that
      without decoding.
    - The object itself from requests_mock.request_history[n] is a private
      _RequestObjectProxy. This shouldn't be so. It's returned from a public API.

    Make issue requests for these when able at
    https://github.com/jamielennox/requests-mock/issues ?
    """
    return DecodedFileUploadMultipartRequest.from_parts(
        MultipartDecoder(
            content=request_object_proxy._request.body,
            content_type=request_object_proxy.headers["Content-Type"],
        ).parts
    )
