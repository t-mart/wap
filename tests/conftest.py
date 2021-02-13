import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from requests_mock import Mocker as RequestsMocker

from tests.util import Environment


@pytest.fixture
def env(fs: FakeFilesystem, requests_mock: RequestsMocker) -> Environment:
    return Environment(
        fs=fs,
        requests_mock=requests_mock,
    )
