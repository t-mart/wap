"""
Main entrypoint to the module
"""

import click

from wap.commands.base import base
from wap.console import error
from wap.exception import WapException


def main() -> None:
    try:
        # standalone causes ClickExceptions to bubble here, where we will catch them
        # otherwise, ugly stack trace
        base.main(standalone_mode=False)
    except WapException as wap_exc:
        error(wap_exc.message)
    except click.ClickException as click_exc:
        error(click_exc.message)
    except click.Abort:
        error("Aborted!")


if __name__ == "__main__":
    main()
