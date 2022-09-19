import json
from typing import Any

import pytest
from glom import assign, delete

from tests.cmd_util import invoke_config
from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv
from wap.exception import (
    ConfigPathException,
    ConfigSchemaException,
    ConfigValueException,
)


@pytest.mark.parametrize(
    "path,expected_stdout",
    [
        ("name", "Package"),
        ("wowVersions", {"mainline": "9.2.7", "wrath": "3.4.0", "vanilla": "1.14.3"}),
    ],
)
@pytest.mark.parametrize("raw", [True, False])
def test_config_get(fs_env: FSEnv, path: str, expected_stdout: str, raw: bool) -> None:
    fs_env.write_config(get_basic_config())

    args = [path]
    if raw:
        args.append("--raw")
    result = invoke_config(args)

    assert result.success
    if isinstance(expected_stdout, str) and raw:
        assert result.stdout.strip() == expected_stdout
    else:
        assert json.loads(result.stdout) == expected_stdout


def test_config_get_bad_path(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["this.does.not.exist"])

    assert isinstance(result.exception, ConfigPathException)


@pytest.mark.parametrize(
    "path,value,expected_config",
    [
        ("name", "lol", assign(get_basic_config(), "name", "lol")),
        (
            "wowVersions",
            {"mainline": "1.2.3", "wrath": "4.5.6", "vanilla": "7.8.9"},
            assign(
                get_basic_config(),
                "wowVersions",
                {"mainline": "1.2.3", "wrath": "4.5.6", "vanilla": "7.8.9"},
            ),
        ),
    ],
)
def test_config_set(fs_env: FSEnv, path: str, value: str, expected_config: Any) -> None:
    config_path = fs_env.write_config(get_basic_config())

    result = invoke_config(["--set", path, json.dumps(value)])

    assert result.success

    assert json.loads(config_path.read_text()) == expected_config


@pytest.mark.parametrize(
    "path,value,expected_config",
    [
        ("name", "lol", assign(get_basic_config(), "name", "lol")),
        ("name", '"more quotes"', assign(get_basic_config(), "name", '"more quotes"')),
        ("version", "9.9.9", assign(get_basic_config(), "version", "9.9.9")),
    ],
)
def test_config_set_raw(
    fs_env: FSEnv, path: str, value: str, expected_config: Any
) -> None:
    config_path = fs_env.write_config(get_basic_config())

    result = invoke_config(["--raw", "--set", path, value])

    assert result.success

    assert json.loads(config_path.read_text()) == expected_config


def test_config_set_cant_encode(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["--set", "name", "invalid { json"])

    assert isinstance(result.exception, ConfigValueException)


def test_config_set_fail_validate(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["--set", "name", "1"])

    assert isinstance(result.exception, ConfigSchemaException)


@pytest.mark.parametrize("path", ["this.does.not.exist", "package.99"])
def test_config_set_bad_path(fs_env: FSEnv, path: str) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["--set", path, "1"])

    assert isinstance(result.exception, ConfigPathException)


def test_config_set_no_value_provided(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["--set", "some.path"])

    assert isinstance(result.exception, SystemExit)


@pytest.mark.parametrize(
    "path,expected_config",
    [
        ("publish", delete(get_basic_config(), "publish")),
        ("package.0.include", delete(get_basic_config(), "package.0.include")),
    ],
)
def test_config_delete(fs_env: FSEnv, path: str, expected_config: Any) -> None:
    config_path = fs_env.write_config(get_basic_config())

    result = invoke_config(["--delete", path])

    assert result.success

    assert json.loads(config_path.read_text()) == expected_config


@pytest.mark.parametrize("path", ["this.does.not.exist", "package.99"])
def test_config_delete_bad_path(fs_env: FSEnv, path: str) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_config(["--delete", path])

    assert isinstance(result.exception, ConfigPathException)
