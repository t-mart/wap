"""
The watch command never halts unless the process is killed. This makes it hard
(maybe impossible) to test this command the way we do the others.

Instead, we take a more unit test approach.
"""
from pathlib import Path
from typing import Union

import click
import pytest
from pytest_mock import MockerFixture

from tests.util import Environment
from wap.commands.watch import do_package_and_dev_install
from wap.exception import WAPException
from wap.watcher import watch_project


def test_watch_project(env: Environment) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
        wow_dir_name="retail",
    )

    watcher = watch_project(config_path=env.config_file_path)

    state = next(watcher)

    # modify an addon file
    with (env.project_dir_path / "Dir1" / "Dir1.lua").open("w") as file:
        file.write("something different")

    new_state = next(watcher)
    assert state != new_state
    state = new_state

    # add a new addon file
    new_lua_file_path = env.project_dir_path / "Dir1" / "New.lua"
    with new_lua_file_path.open("w") as file:
        file.write("blah")

    new_state = next(watcher)
    assert state != new_state
    state = new_state

    # delete a file
    new_lua_file_path.unlink()

    new_state = next(watcher)
    assert state != new_state
    state = new_state

    # update the config
    with env.config_file_path.open("r") as config_file:
        contents = config_file.read()

    with env.config_file_path.open("w") as config_file:
        config_file.write(contents.replace("123456", "654321"))

    new_state = next(watcher)
    assert state != new_state


def test_do_package_and_dev_install(mocker: MockerFixture) -> None:
    ctx_mock = mocker.MagicMock(spec_set=click.Context)
    log_mock = mocker.patch("wap.commands.watch.log")

    do_package_and_dev_install(
        ctx=ctx_mock,
        config_path=Path("foo"),
        version="1.2.3",
        wow_addons_path=Path("bar"),
    )

    assert log_mock.info.called


@pytest.mark.parametrize(
    "exc",
    [WAPException("wap"), click.ClickException("click")],
    ids=["wap exception", "click exception"],
)
def test_do_package_and_dev_install_with_exc(
    mocker: MockerFixture, exc: Union[WAPException, click.ClickException]
) -> None:
    ctx_mock = mocker.MagicMock(spec_set=click.Context)
    ctx_mock.invoke.side_effect = exc
    log_mock = mocker.patch("wap.commands.watch.log")

    do_package_and_dev_install(
        ctx=ctx_mock,
        config_path=Path("foo"),
        version="1.2.3",
        wow_addons_path=Path("bar"),
    )

    assert log_mock.error.called_once_with(exc.message + "\n")
