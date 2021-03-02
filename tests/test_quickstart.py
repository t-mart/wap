import json
from pathlib import Path

import pytest

from tests.util import Environment, contains_warn_error, fileset
from wap.exception import QuickstartException
from wap.wowversion import LATEST_CLASSIC_VERSION, LATEST_RETAIL_VERSION

# These tests have a timeout because they take input from prompts on stdin. wap will
# hang forver if the prompts are not answered correctly, and therefore, so will pytest.
# adding a timeout at least allows pytest to fail deterministically in these cases.
#
# 10 seconds should be long enough?


@pytest.mark.timeout(5)
class TestQuickstart:
    @pytest.mark.parametrize(
        "project_dir_path",
        [
            "MyAddon",
            "subdir/MyAddon",
        ],
        ids=["at cwd", "subdir"],
    )
    def test_quickstart(self, env: Environment, project_dir_path: str) -> None:
        env.prepare(
            project_dir_name="empty",
        )

        addon_name = "foo"
        author = "John Doe"
        description = "My description"
        cf_addon_name = "mycooladdon"
        changelog_name = "CHANGELOG.md"

        input_lines = [
            addon_name,  # addon name (default)
            author,  # author name
            description,  # notes
            "Y",  # yes to retail wow
            "y",  # yes to classic wow
            "yes",  # yes to having a curseforge project
            "123456",  # project id
            f"https://www.curseforge.com/wow/addons/{cf_addon_name}",  # CF url
        ]

        result = env.run_wap("quickstart", project_dir_path, input_lines=input_lines)

        assert not contains_warn_error(result.stderr)

        full_project_dir_path = env.project_dir_path / project_dir_path

        # test the config made
        validation_result = env.run_wap(
            "validate",
            "--json",
            "--config-path",
            str(full_project_dir_path / ".wap.yml"),
        )
        config_json = json.loads(validation_result.stdout)

        assert config_json["name"] == addon_name
        assert set(config_json["wow-versions"]) == {
            LATEST_RETAIL_VERSION.dot_version(),
            LATEST_CLASSIC_VERSION.dot_version(),
        }
        assert config_json["curseforge"]["project-id"] == "123456"
        assert config_json["curseforge"]["changelog-file"] == changelog_name
        assert config_json["curseforge"]["project-slug"] == cf_addon_name
        assert config_json["addons"][0]["path"] == addon_name
        assert config_json["addons"][0]["toc"]["tags"] == {
            "Title": addon_name,
            "Author": author,
            "Notes": description,
        }
        assert config_json["addons"][0]["toc"]["files"] == ["Init.lua"]

        # test the files created
        expected_quickstart_files = {
            Path(".wap.yml"),
            Path(changelog_name),
            Path("README.md"),
            Path(f"{addon_name}/Init.lua"),
        }

        # unfortunate naming conflict between env.project_dir_path and project_dir_path.
        # the former is the environment "project directory", but in this case, is just
        # an # empty directory. the latter is where the user has quickstarted the new
        # project. the Environment class wasn't really written with this use case in
        # mind, but offers too nice a test fixture to pass up.
        full_project_dir_path = env.project_dir_path / project_dir_path
        actual_quickstart_files = fileset(full_project_dir_path)

        assert expected_quickstart_files == actual_quickstart_files

        # do a simple wap package in the new project dir. this essentially "roundtrips"
        # the output of quickstart to ensure it is functional
        env.run_wap("package", cwd=full_project_dir_path)

    def test_quickstart_interactive_prompt_retries(self, env: Environment) -> None:
        env.prepare(
            project_dir_name="empty",
        )

        input_lines = [
            "foo",  # addon name (default)
            "John Doe",  # author name
            "My description",  # notes
            "neither yes nor no",  # test the retry
            "blarg blarg",  # test the retry
            "y",  # yes to retail wow
            "y",  # yes to classic wow
            "yes",  # yes to having a curseforge project
            "123456",
            "",  # default changelog
            "not a url",  # test the retry
            "still not a url",  # test the retry
            "https://www.curseforge.com/wow/addons/someaddon",  # CF url
        ]

        env.run_wap("quickstart", "MyAddon", input_lines=input_lines)

    def test_quickstart_dir_exists(self, env: Environment) -> None:
        env.prepare(
            project_dir_name="empty",
        )

        project_dir_path = env.project_dir_path / "exists"
        project_dir_path.mkdir()

        with pytest.raises(QuickstartException, match=r"exists"):
            env.run_wap("quickstart", str(project_dir_path))
