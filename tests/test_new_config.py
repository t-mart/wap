import pytest

from tests.util import Environment
from wap.commands.common import DEFAULT_CONFIG_PATH
from wap.exception import NewConfigException


@pytest.mark.parametrize(
    "use_default_config_path",
    [True, False],
    ids=["default config path", "specified config path"],
)
def test_new_config(
    env: Environment,
    use_default_config_path: bool,
) -> None:
    env.prepare(
        project_dir_name="new_config",
    )

    run_wap_args = ["new-config"]
    additional_args = []

    if not use_default_config_path:
        config_path = env.project_dir_path / ".wap.custom.yml"
        additional_args = ["--config-path", str(config_path.name)]
    else:
        config_path = env.project_dir_path / DEFAULT_CONFIG_PATH

    assert not config_path.exists()

    env.run_wap(*run_wap_args, *additional_args)

    assert config_path.exists()

    # do a simple wap build in the new project dir. this essentially "roundtrips" the
    # output of new-config to ensure it is functional

    # hacky little reuse of additional_args because both these commands have the same
    # option format and option defaults.
    env.run_wap("build", *additional_args)


def test_new_config_file_already_exists(
    env: Environment,
) -> None:
    env.prepare(project_dir_name="basic", config_file_name="basic")

    assert (env.project_dir_path / DEFAULT_CONFIG_PATH).exists()

    with pytest.raises(NewConfigException, match=r"exists"):
        env.run_wap("new-config")
