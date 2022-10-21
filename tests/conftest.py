import os
from collections.abc import Iterator
from pathlib import Path

import pytest
import respx
from freezegun import freeze_time as _freeze_time
from respx.router import MockRouter

from tests.fixture.curseforge import setup_mock_cf_api
from tests.fixture.fsenv import FSEnv
from tests.fixture.time import TEST_TIME


@pytest.fixture(autouse=True)
def ch_tmp_dir(tmp_path: Path) -> Iterator[None]:
    restore_cwd = Path.cwd()
    os.chdir(tmp_path)
    yield
    os.chdir(restore_cwd)


@pytest.fixture(autouse=True)
def freeze_time() -> Iterator[None]:
    with _freeze_time(TEST_TIME.datetime):
        yield


@pytest.fixture
def fs_env(tmp_path: Path) -> Iterator[FSEnv]:
    yield FSEnv(root=tmp_path)


@pytest.fixture(autouse=True)
def cf_api_respx() -> Iterator[MockRouter]:
    with respx.mock(assert_all_called=False) as respx_mock:
        yield setup_mock_cf_api(respx_mock)
