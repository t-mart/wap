import json
from pathlib import Path
from unittest.mock import patch

from tests.cmd_util import invoke_new_project
from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv
from wap.config import Config


def test_new_project(fs_env: FSEnv) -> None:
    basic_config = get_basic_config()
    with patch(
        "tests.cmd_util.new_project.prompt_for_config",
        return_value=Config.from_python_object(basic_config),
    ):
        result = invoke_new_project()
        assert result.success

        project_root = Path("Package")
        assert json.loads((project_root / "wap.json").read_text()) == basic_config
        assert (project_root / "README.md").is_file()
        assert (project_root / "Package/Main.lua").is_file()
