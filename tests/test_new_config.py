import json
from pathlib import Path
from unittest.mock import patch
from wap.config import Config

from tests.cmd_util import invoke_new_config
from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv


def test_new_config() -> None:
    basic_config = get_basic_config()
    with patch(
        "tests.cmd_util.new_config.prompt_for_config",
        return_value=Config.from_python_object(basic_config),
    ):
        result = invoke_new_config()
        assert result.success
        assert json.loads(Path("wap.json").read_text()) == basic_config
