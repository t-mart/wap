"""
Main entrypoint to the module
"""
import sys

import click

from wap.commands.base import base
from wap.console import error
from wap.exception import WapError


def main() -> None:
    try:
        # standalone causes ClickExceptions to bubble here, where we will catch them
        # otherwise, ugly stack trace
        exit_code: int | None = base.main(standalone_mode=False, color=True)
        if exit_code is None:
            exit_code = 0
    except WapError as wap_exc:
        error(wap_exc.message)
        exit_code = 1
    except click.ClickException as click_exc:
        error(str(click_exc))
        exit_code = 1
    except click.Abort:
        error("Aborted!")
        exit_code = 130  # http://tldp.org/LDP/abs/html/exitcodes.html

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
