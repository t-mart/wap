import textwrap

from rich.console import Console

STDERR_CONSOLE = Console(stderr=True, highlight=False)
STDOUT_CONSOLE = Console(stderr=False, highlight=False)


def _print(
    text: str, console: Console, newline: bool = True, dedent: bool = False
) -> None:
    if dedent:
        text = textwrap.dedent(text)
    console.print(text, end="\n" if newline else "")


def print_err(text: str, newline: bool = True, dedent: bool = False) -> None:
    _print(text, STDERR_CONSOLE, newline=newline, dedent=dedent)


def print_out(text: str, newline: bool = True, dedent: bool = False) -> None:
    _print(text, STDOUT_CONSOLE, newline=newline, dedent=dedent)


def debug(text: str, newline: bool = True, dedent: bool = False) -> None:
    print_err(f"[cyan]\\[DEBUG][/cyan] {text}", newline=newline, dedent=dedent)


def info(text: str, newline: bool = True, dedent: bool = False) -> None:
    print_err(text, newline=newline, dedent=dedent)


def warn(text: str, newline: bool = True, dedent: bool = False) -> None:
    print_err(f"[yellow]\\[WARN][/yellow] {text}", newline=newline, dedent=dedent)


def error(text: str, newline: bool = True, dedent: bool = False) -> None:
    print_err(f"[red]\\[ERROR][/red] {text}", newline=newline, dedent=dedent)
