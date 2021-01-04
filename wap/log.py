"""
Logging setup
"""

from __future__ import annotations

import sys
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


def _log(*, label: Optional[str] = None, msg: str) -> None:
    out = msg
    if label is not None:
        out = f"{label} - {msg}"
    # print(out, file=sys.stderr)
    click.echo(out, err=True)


def debug(msg: str) -> None:
    _log(label="DEBUG", msg=msg)


def info(msg: str) -> None:
    # no label here. this is the default way we should be communicating with the user
    _log(msg=msg)


def warn(msg: str) -> None:
    _log(label="WARNING", msg=msg)


def error(msg: str) -> None:
    _log(label="ERROR", msg=msg)
