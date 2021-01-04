from typing import Any, Callable

import pytest

from wap import log

_TEST_LOG_MESSAGE = "Software testing is an investigation conducted to provide..."


@pytest.mark.parametrize(
    "fn,expected_output",
    [
        (
            log.debug,
            f"DEBUG - {_TEST_LOG_MESSAGE}\n",
        ),
        (
            log.info,
            f"{_TEST_LOG_MESSAGE}\n",
        ),
        (
            log.warn,
            f"WARNING - {_TEST_LOG_MESSAGE}\n",
        ),
        (
            log.error,
            f"ERROR - {_TEST_LOG_MESSAGE}\n",
        ),
    ],
    ids=["debug", "info", "warn", "error"],
)
def test_logging(
    capsys: pytest.CaptureFixture[str],
    fn: Callable[..., Any],
    expected_output: str,
) -> None:
    fn(_TEST_LOG_MESSAGE)

    captured = capsys.readouterr()

    assert captured.err == expected_output
