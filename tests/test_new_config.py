import json

import pytest

from tests.util import Environment, contains_warn_error
from wap.commands.common import DEFAULT_CONFIG_PATH
from wap.exception import NewConfigException
from wap.wowversion import LATEST_CLASSIC_VERSION


@pytest.mark.timeout(5)
class TestNewConfig:
    @pytest.mark.parametrize(
        "use_default_config_path",
        [True, False],
        ids=["default config path", "specified config path"],
    )
    def test_new_config(self, env: Environment, use_default_config_path: bool) -> None:
        env.prepare(
            project_dir_name="new_config",
        )

        addon_name = "foo"
        author = "John Doe"
        description = "My description"

        input_lines = [
            addon_name,  # addon name (default)
            author,  # author name
            description,  # notes
            "N",  # no to retail wow, therefore, classic
            "no",  # no to having a curseforge project
        ]

        run_wap_args = ["new-config"]
        additional_args = []

        if not use_default_config_path:
            config_path = env.project_dir_path / ".wap.custom.yml"
            additional_args = ["--config-path", str(config_path.name)]
        else:
            config_path = env.project_dir_path / DEFAULT_CONFIG_PATH

        assert not config_path.exists()

        result = env.run_wap(*run_wap_args, *additional_args, input_lines=input_lines)

        assert not contains_warn_error(result.stderr)

        assert config_path.exists()

        # test the config made
        validation_result = env.run_wap(
            "validate",
            "--json",
            "--config-path",
            str(config_path),
        )
        config_json = json.loads(validation_result.stdout)

        assert config_json["name"] == addon_name
        assert set(config_json["wow-versions"]) == {
            LATEST_CLASSIC_VERSION.dot_version(),
        }
        assert "curseforge" not in config_json
        assert config_json["dirs"][0]["path"] == addon_name
        assert config_json["dirs"][0]["toc"]["tags"] == {
            "Title": addon_name,
            "Author": author,
            "Notes": description,
        }
        assert config_json["dirs"][0]["toc"]["files"] == ["Init.lua"]

    def test_new_config_file_already_exists(self, env: Environment) -> None:
        env.prepare(project_dir_name="basic", config_file_name="basic")

        assert (env.project_dir_path / DEFAULT_CONFIG_PATH).exists()

        with pytest.raises(NewConfigException, match=r"exists"):
            env.run_wap("new-config")
