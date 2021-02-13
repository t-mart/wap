"""
Main entrypoint to the module
"""


def main() -> None:
    # imports are done here to reduce the amount of time spent outside the try-except
    # block, where a user can potentially interrupt the program

    # exit code reference http://www.tldp.org/LDP/abs/html/exitcodes.html

    try:
        from wap.commands import base

        base.main(standalone_mode=False)

        exit_code = 0

    # unfortunately, BaseException is the only exception superclass of KeyboardInterrupt
    except BaseException as exc:
        from click import ClickException

        from wap import log
        from wap.exception import WAPException

        if isinstance(exc, KeyboardInterrupt):
            log.error("Interrupted")
            exit_code = 130

        elif isinstance(exc, WAPException):
            log.error(exc.message)
            exit_code = 1

        elif isinstance(exc, ClickException):
            log.error(exc.format_message())
            exit_code = 1

        else:
            raise

    import sys

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
