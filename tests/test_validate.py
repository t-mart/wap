from tests.cmd_util import invoke_validate
from tests.fixture.config import get_basic_config
from tests.fixture.fsenv import FSEnv


def test_valid_validation(fs_env: FSEnv) -> None:
    fs_env.write_config(get_basic_config())

    result = invoke_validate()

    assert result.success
    assert result.stdout == "valid"


def test_invalid_validation(fs_env: FSEnv) -> None:
    fs_env.write_config("this aint valid!")

    result = invoke_validate()

    # TODO: look into why this isn't considered fail. something with the way click is
    # running the command... standalone mode, perhaps.
    assert result.success
    assert result.stdout == "invalid"
