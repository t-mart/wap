"""
Logging setup
"""

from __future__ import annotations

from typing import Optional

import click

# the python standard logging module is the most degenerate shit ever
#   - global state
#   - multiple loggers, handlers, formatters? overengineered
#   - strange filtering (loggers and handlers can have different levels)
#   - need to hack in ISO8601-compliant timestamps
#   - hard to test because different loggers, handlers, etc
#   - warn vs warning functions (not to even mention the additional warnings module)
#   - it uses javaCasing, not python_casing
#
# let's just make some functions that do what we want. this will also allow further
# improvements, like color, in the future

# some logging lines are not covered by code coverage here because they are not
# exercised by wap currently. I'd rather retain the full set of logging functions
# in case we need them in the future. Hopefully, their simplicity should be self-evident

DEBUG_LABEL = "DEBUG"
WARN_LABEL = "WARN"
ERROR_LABEL = "ERROR"


def _log(*, label: Optional[str] = None, msg: str) -> None:
    out = msg
    if label is not None:
        out = f"{label} - {msg}"
    click.echo(out, err=True)


def debug(msg: str) -> None:
    _log(label=click.style(DEBUG_LABEL, fg="cyan"), msg=msg)  # pragma: no cover


def info(msg: str) -> None:
    # no label here. this is the default way we should be communicating with the user
    _log(msg=msg)  # pragma: no cover


def warn(msg: str) -> None:
    _log(label=click.style(WARN_LABEL, fg="yellow"), msg=msg)  # pragma: no cover


def error(msg: str) -> None:
    _log(label=click.style(ERROR_LABEL, fg="red"), msg=msg)  # pragma: no cover
