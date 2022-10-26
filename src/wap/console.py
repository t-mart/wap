from typing import Any, overload

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.theme import Theme

_THEME = Theme(
    {
        # custom rgb hex colors most likely from D3 category 10
        "debug": "bold grey11",
        "info": "bold cyan",
        "warn": "bold yellow",
        "error": "bold red",
        "path": "underline #1f77b4",  # a blue
        "url": "underline #1f77b4",  # a blue
        "hint": "italic",
        "package": "bold #ff7f0e",  # an orange
        "addon": "bold #2ca02c",  # a green
        "promptq": "bold",  # for prompt questions
        "prompta": "italic #bcbd22",  # a yellow, for prompt feedback
        "key": "#d62728",  # a red, for things pressed on the keyboard
        "command": "#2ca02c",  # a green, for commands that can be run
        "flavor": "#9467bd",  # a purple, for wow flavors
    }
)

_STDERR_CONSOLE = Console(stderr=True, highlight=False, theme=_THEME)
_STDOUT_CONSOLE = Console(stderr=False, highlight=False, theme=_THEME)


def print(text: Any, stderr: bool = True, newline: bool = True) -> None:
    """
    Print text to the console.

    If `stderr` is True, print to stderr. Otherwise, print to stdout.

    If `newline` is True, print a newline character after the string.
    """
    if stderr:
        console = _STDERR_CONSOLE
    else:
        console = _STDOUT_CONSOLE

    console.print(text, end="\n" if newline else "")


def debug(text: str, newline: bool = True) -> None:
    print(f"[debug]\\[DEBUG][/debug] {text}", newline=newline)


def info(text: str, newline: bool = True) -> None:
    print(f"[info]\\[INFO][/info] {text}", newline=newline)


def warn(text: str, newline: bool = True) -> None:
    print(f"[warn]\\[WARN][/warn] {text}", newline=newline)


def error(text: str, newline: bool = True) -> None:
    print(f"[error]\\[ERROR][/error] {text}", newline=newline)


def _render_as_style(text: str, style: str) -> str:
    """Produce a text in the style."""
    return _THEME.styles[style].render(text)


# this is only overloaded because rich overloads it. unnecessary...
@overload
def prompt_ask(prompt: str) -> str:
    ...


@overload
def prompt_ask(prompt: str, default: str) -> str:
    ...


@overload
def prompt_ask(prompt: str, default: str | None) -> str | None:
    ...


def prompt_ask(prompt: str, default: str | None = None) -> str | None:
    # this method exists because Prompt.ask text does not parse [markup] tags
    return Prompt.ask(
        _render_as_style(prompt, "promptq"),
        console=_STDERR_CONSOLE,
        # this is how rich does it (strangely)
        default=default if default is not None else ...,  # type: ignore
    )


def confirm_ask(
    prompt: str,
    default: bool | None = None,
) -> bool:
    # ditto
    return Confirm.ask(
        _render_as_style(prompt, "promptq"),
        console=_STDERR_CONSOLE,
        default=default if default is not None else ...,  # type: ignore
    )


def print_json(json_text: str) -> None:
    _STDERR_CONSOLE.print_json(json_text)


if __name__ == "__main__":
    from pathlib import PureWindowsPath

    error("error")
    warn("warn")
    info("info")
    debug("debug")

    print("[path]C:\\Users\\tim\\code\\")
    print(f'[path]{PureWindowsPath("C:/Users/tim/Saved Games/").as_uri()}')
    print("[path]C:/Users/tim/Saved Games/")

    print("[hint]Next time, do this...")
    print("[url]https://rich.readthedocs.io/en/")
    print("this is [package]ThePackage")
    print("this is [addon]MyAddon")

    answer = prompt_ask("How are you?")
    print(f"[prompta]Glad you're doing {answer}")
    confirm_ask("Authorize launch?")

    print("Press [key]Ctrl-C[/key] to exit")
    print("See `[command]wap help[/command]` for more")
