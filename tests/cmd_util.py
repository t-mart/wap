from __future__ import annotations

import re
from collections.abc import Sequence

from attr import frozen
from click import BaseCommand
from click.testing import CliRunner, Result

# we need to patch some functions in these module, so we gotta import the module itself
# -- can't import specific things from the module because then the references wouldn't
# be patchable.
from wap.commands import base, build, new_config, new_project, publish, validate

_WHITESPACE_PATTERN = r"\s+"


@frozen(kw_only=True)
class RunResult:  # yeesh, this name is derivative
    """
    The result of an invoked Click command with some quality-of-life improvements.
    """

    stdout_raw: str
    stderr_raw: str
    exit_code: int
    exception: BaseException | None

    @classmethod
    def from_result(cls, result: Result) -> RunResult:
        return RunResult(
            stdout_raw=result.stdout,
            stderr_raw=result.stderr,
            exit_code=result.exit_code,
            exception=result.exception,
        )

    @property
    def stdout(self) -> str:
        # ensures there's no line breaks to mess up __contains__ calls
        return re.sub(_WHITESPACE_PATTERN, " ", self.stdout_raw).strip()

    @property
    def stderr(self) -> str:
        return re.sub(_WHITESPACE_PATTERN, " ", self.stderr_raw).strip()

    @property
    def success(self) -> bool:
        return self.exit_code == 0


def invoke(command: BaseCommand, args: Sequence[str] | None = None) -> RunResult:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(command, args or [])
    return RunResult.from_result(result)


def invoke_build(args: Sequence[str] | None = None) -> RunResult:
    return invoke(build.build, args)


def invoke_validate(args: Sequence[str] | None = None) -> RunResult:
    return invoke(validate.validate, args)


def invoke_help(args: Sequence[str] | None = None) -> RunResult:
    return invoke(base.help_command, args)


def invoke_new_config(args: Sequence[str] | None = None) -> RunResult:
    return invoke(new_config.new_config, args)


def invoke_new_project(args: Sequence[str] | None = None) -> RunResult:
    return invoke(new_project.new_project, args)


def invoke_publish(args: Sequence[str] | None = None) -> RunResult:
    return invoke(publish.publish, args)
