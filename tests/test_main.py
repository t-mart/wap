"""
Other modules in tests are, more or less, blackbox tests. They work by calling the Click
base command using a CliRunner, which bypasses the main entrypoint of the application at
__main__.py.

There is some logic in __main__.py, and we test it here. We mock out the base command
and give it particular side effects, so these tests are more whitebox tests.
"""

import pytest
from click import ClickException
from pytest_mock import MockerFixture

from wap import __main__
from wap.exception import WAPException

MAIN = __main__.main


def test_normal_execution(mocker: MockerFixture) -> None:
    mocker.patch("wap.commands.base.main")

    # this method from
    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as se:
        MAIN()

    assert se.value.code == 0


@pytest.mark.parametrize(
    ("exc_to_throw", "expected_exit_code"),
    [
        [KeyboardInterrupt(), 130],
        [WAPException(""), 1],
        [ClickException(""), 1],
    ],
    ids=["keyboard interrupt", "wap exception", "click exception"],
)
def test_expected_exceptions(
    mocker: MockerFixture, exc_to_throw: BaseException, expected_exit_code: int
) -> None:
    mock = mocker.patch("wap.commands.base.main")
    mock.side_effect = exc_to_throw

    with pytest.raises(SystemExit) as se:
        MAIN()

    assert se.value.code == expected_exit_code


def test_unexpected_exception(mocker: MockerFixture) -> None:
    mock = mocker.patch("wap.commands.base.main")
    mock.side_effect = RuntimeError("")

    # note here that we're not catching system exit. this is an unexpected exception,
    # so it passes through and produces a stack trace like we expect
    with pytest.raises(RuntimeError):
        MAIN()
