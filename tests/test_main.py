from typing import Callable
from unittest.mock import patch

import pytest
from click import ClickException
from pytest_mock import MockerFixture

from tests.fixtures import capsys_err
from wap import __main__
from wap.exception import WAPException

_EXCEPTIONS_THROWN = [
    ("wap exception", WAPException, 1),
    ("click exception", ClickException, 1),
    (__main__._INTERRUPTED_STR, KeyboardInterrupt, 130),
]


@pytest.mark.parametrize(
    ("exc", "expected_log", "expected_exit_code"),
    [
        (
            exc(msg),
            msg,
            exit_code,
        )
        for msg, exc, exit_code in _EXCEPTIONS_THROWN
    ],
    ids=list(t[1].__name__ for t in _EXCEPTIONS_THROWN),
)
def test_main_handled_exception_thrown(
    exc: Exception,
    expected_log: str,
    expected_exit_code: int,
    capsys_err: Callable[[], str],
    mocker: MockerFixture,
) -> None:
    mock_cli = mocker.patch("wap.cli.base", spec_set=True)
    mock_cli.main.side_effect = exc

    with pytest.raises(SystemExit) as exc:  # type: ignore
        __main__.main()

        assert exc.value.code == expected_exit_code  # type: ignore

    assert mock_cli.main.called

    assert expected_log in capsys_err()


def test_main_unhandled_exception_thrown(mocker: MockerFixture) -> None:
    exc = Exception("a bug!")

    mock_cli = mocker.patch("wap.cli.base", spec_set=True)
    mock_cli.main.side_effect = exc

    with pytest.raises(type(exc)):
        __main__.main()


def test_main_normal(mocker: MockerFixture) -> None:
    mock_cli = mocker.patch("wap.cli.base", spec_set=True)

    with pytest.raises(SystemExit) as exc:
        __main__.main()

        assert exc.value.code == 0

    assert mock_cli.main.called
