from pathlib import Path

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


# for "wap watch", we need to real filesystem so that we can test FS events
@pytest.fixture
def env_realfs(tmp_path: Path, requests_mock: RequestsMocker) -> Environment:
    return Environment(
        tmp_dir=tmp_path,
        requests_mock=requests_mock,
    )
