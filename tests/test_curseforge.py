from io import BytesIO
from typing import Any, MutableMapping
from unittest.mock import MagicMock, patch

import pytest
from requests_mock import Mocker as RequestsMocker

from wap.curseforge import CurseForgeAPI
from wap.exception import CurseForgeAPIException, ReleaseException

_TEST_PROJECT_ID = "1234"
_TEST_FILE_ID = 4321
_TEST_API_TOKEN = "my-api-token"
_TEST_ARCHIVE_FILE = BytesIO(b"file contents")
_TEST_DISPLAY_NAME = "MyAddon-1.2.3"
_TEST_CHANGELOG_CONTENTS = "My changelog has the following changes..."
_TEST_RELEASE_TYPE = "release"
_TEST_CHANGELOG_TYPE = "markdown"
_TEST_FILE_NAME = _TEST_DISPLAY_NAME + ".zip"

_TEST_VERSION = "9.0.2"
_TEST_VERSION_NOT_IN_RESPONSE = "9.9.9"
_TEST_VERSION_ID_EARLIER = 776
# The greatest version id will be returned from get_version_id, so it's by definition
# that this is larger
_TEST_VERSION_ID_LATEST = _TEST_VERSION_ID_EARLIER + 1


@pytest.fixture
def success_mock(requests_mock: RequestsMocker) -> RequestsMocker:
    requests_mock.post(
        CurseForgeAPI.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=_TEST_PROJECT_ID),
        json={"id": _TEST_FILE_ID},
    )
    requests_mock.get(
        CurseForgeAPI.VERSION_ENDPOINT_URL,
        json=[
            {
                "id": 7971,
                "gameVersionTypeID": 517,
                "name": "9.0.1",
                "slug": "9-0-1",
            },
            {
                "id": _TEST_VERSION_ID_EARLIER,
                "gameVersionTypeID": 517,
                "name": _TEST_VERSION,
                "slug": "9-0-2",
            },
            {  # this is here to test the logic with multiple duplicate versions
                "id": _TEST_VERSION_ID_LATEST,
                "gameVersionTypeID": 518,
                "name": _TEST_VERSION,
                "slug": "9-0-2",
            },
            {
                "id": 8171,
                "gameVersionTypeID": 67408,
                "name": "1.13.6",
                "slug": "1-13-6",
            },
        ],
    )


@pytest.fixture
def fail_mock(requests_mock: RequestsMocker) -> RequestsMocker:
    requests_mock.post(
        CurseForgeAPI.UPLOAD_ENDPOINT_URL_TEMPLATE.format(project_id=_TEST_PROJECT_ID),
        status_code=400,
        json={"reason": "something went wrong"},
    )
    requests_mock.get(
        CurseForgeAPI.VERSION_ENDPOINT_URL,
        status_code=400,
        json={"reason": "something went wrong"},
    )


@pytest.fixture
def api() -> CurseForgeAPI:
    return CurseForgeAPI(api_token=_TEST_API_TOKEN)


@pytest.fixture
def normal_upload_args() -> MutableMapping[str, Any]:
    return {
        "project_id": _TEST_PROJECT_ID,
        "archive_file": _TEST_ARCHIVE_FILE,
        "display_name": _TEST_DISPLAY_NAME,
        "changelog_contents": _TEST_CHANGELOG_CONTENTS,
        "wow_version_id": _TEST_VERSION_ID_LATEST,
        "release_type": _TEST_RELEASE_TYPE,
        "changelog_type": _TEST_CHANGELOG_TYPE,
        "file_name": _TEST_FILE_NAME,
    }


def test_upload_addon_file_normal(
    success_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    file_id = api.upload_addon_file(**normal_upload_args)

    assert file_id == _TEST_FILE_ID


def test_upload_addon_file_http_error(
    fail_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:

    with pytest.raises(CurseForgeAPIException):
        api.upload_addon_file(**normal_upload_args)


def test_upload_addon_file_bad_changelog_type(
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    normal_upload_args["changelog_type"] = "fake changelog type"

    with pytest.raises(ReleaseException):
        api.upload_addon_file(**normal_upload_args)


def test_upload_addon_file_bad_release_type(
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    normal_upload_args["release_type"] = "fake release type"

    with pytest.raises(ReleaseException):
        api.upload_addon_file(**normal_upload_args)


def test_get_version_id_normal(
    success_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    version_id = api.get_version_id(version=_TEST_VERSION)

    assert version_id == _TEST_VERSION_ID_LATEST


def test_get_version_id_version_not_found(
    success_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:

    with pytest.raises(ReleaseException):
        api.get_version_id(version=_TEST_VERSION_NOT_IN_RESPONSE)


def test_get_version_id_http_error(
    fail_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:

    with pytest.raises(CurseForgeAPIException):
        api.get_version_id(version=_TEST_VERSION)


def test_get_version_id_normal_with_cache(
    success_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    # make a request with requests-mock to prime the cache
    api.get_version_id(version=_TEST_VERSION)

    # then patch the session with a magic mock because requests-mock mocks don't support
    # getting the call history
    with patch(
        "wap.curseforge.CurseForgeAPI.SESSION",
        new=MagicMock(wraps=CurseForgeAPI.SESSION),
    ) as mock:
        api.get_version_id(version=_TEST_VERSION)

        assert not mock.get.called


def test_get_version_id_normal_without_cache(
    success_mock: RequestsMocker,
    api: CurseForgeAPI,
    normal_upload_args: MutableMapping[str, Any],
) -> None:
    # make a request with requests-mock to prime the cache
    api.get_version_id(version=_TEST_VERSION)

    # then patch the session with a magic mock because requests-mock mocks don't support
    # getting the call history
    with patch(
        "wap.curseforge.CurseForgeAPI.SESSION",
        new=MagicMock(wraps=CurseForgeAPI.SESSION),
    ) as mock:
        api.get_version_id(version=_TEST_VERSION, read_cache=False)

        assert mock.get.called
