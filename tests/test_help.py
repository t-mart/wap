import webbrowser
from unittest.mock import patch

import pytest

from tests.cmd_util import invoke_help


@pytest.mark.parametrize(
    "subcommand",
    ["build", "validate", "help", "new-config", "new-project", "publish", None],
)
def test_help(subcommand: str | None) -> None:
    with patch("tests.cmd_util.base.webbrowser.open") as webbrowser_open_mock:
        args = []
        if subcommand is not None:
            args.append(subcommand)
        result = invoke_help(args)

        assert result.success

        expected_url = "http://t-mart.github.io/wap"
        if subcommand is not None:
            expected_url += f"/commands/{subcommand}"
        webbrowser_open_mock.assert_called_once_with(expected_url)


@pytest.mark.parametrize(
    "subcommand",
    ["build", "validate", "help", "new-config", "new-project", "publish", None],
)
def test_help_no_browser(subcommand: str | None) -> None:
    with patch("tests.cmd_util.base.webbrowser.open", side_effect=webbrowser.Error):
        args = []
        if subcommand is not None:
            args.append(subcommand)
        result = invoke_help(args)

        assert result.success

        assert "See documentation at" in result.stderr
