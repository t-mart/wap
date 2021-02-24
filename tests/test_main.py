"""
Other modules in tests are, more or less, blackbox tests. They work by calling the Click
base command using a CliRunner, which gives us an interface similar to that of a user
using wap on the command line. Unfortunately, this bypasses the main entrypoint of the
application at __main__.py.

There is some logic in __main__.py that still requires testing though, and we do that
here. We mock out the base command and give it particular side effects, so these tests
are more whitebox tests (tests that have an understanding of the internals of the
program). There does not seem to be any other way to test __main__.py functionality from
within Python.
"""

import pytest
from click import Abort, ClickException
from pytest_mock import MockerFixture

from wap import __main__
from wap.exception import WAPException

MAIN = __main__.main


def test_normal_execution(mocker: MockerFixture) -> None:
    mock = mocker.patch("wap.commands.base.main")
    mock.return_value = 0

    # this method from
    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as se:
        MAIN()

    assert se.value.code == 0


@pytest.mark.parametrize(
    ("exc_to_throw", "expected_exit_code"),
    [
        [KeyboardInterrupt(), 130],
        [Abort(), 130],
        [WAPException(""), 1],
        [ClickException(""), 1],
    ],
    ids=["keyboard interrupt", "click abort", "wap exception", "click exception"],
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
