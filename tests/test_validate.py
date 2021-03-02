import json

from tests.util import Environment, contains_warn_error


def test_validate(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="basic",
    )

    result = env.run_wap("validate", "--json")

    assert not contains_warn_error(result.stderr)

    config_json = json.loads(result.stdout)

    assert config_json["name"] == "MyAddon"
    assert set(config_json["wow-versions"]) == {"9.0.2", "1.13.6"}
    assert config_json["curseforge"]["project-id"] == "123456"
    assert config_json["curseforge"]["changelog-file"] == "CHANGELOG.md"
    assert config_json["curseforge"]["project-slug"] == "myaddon"
    assert config_json["addons"][0]["path"] == "Dir1"
    assert config_json["addons"][0]["toc"]["tags"] == {
        "Title": "MyAddon Dir1",
        "X-Custom-Tag": "foobar",
    }
    assert config_json["addons"][0]["toc"]["files"] == ["Dir1.lua", "Sub/Another.lua"]

    assert result.exit_code == 0

    assert "is valid" in result.stderr


def test_validate_fail(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="basic",
        config_file_name="does_not_follow_schema",
    )

    result = env.run_wap("validate", "--json", catch_exceptions=True)

    assert result.exit_code != 0

    assert "is not valid" in result.stderr
