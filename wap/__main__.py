"""
Main entrypoint to the module
"""

# for tests that check stderr contents on exception
_INTERRUPTED_STR = "Interrupted"


def main() -> None:
    # imports are done here to reduce the amount of time spent outside the try-except
    # block, where a user can potentially interrupt the program

    # exit code reference http://www.tldp.org/LDP/abs/html/exitcodes.html

    try:
        import wap.cli

        wap.cli.base.main(standalone_mode=False)
        exit_code = 0

    except BaseException as exc:
        from click import ClickException

        from wap import log
        from wap.exception import WAPException

        if isinstance(exc, KeyboardInterrupt):
            log.error(_INTERRUPTED_STR)
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
