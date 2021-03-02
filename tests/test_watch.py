import concurrent.futures

import pytest

from tests.util import Environment


@pytest.mark.skip(
    reason="need to figure out how to test a something that does a while True loop"
)
def test_watch(
    env_realfs: Environment,  # need to use real fs to get fs events
) -> None:
    env_realfs.prepare(
        project_dir_name="basic",
        config_file_name="basic",
        wow_dir_name="retail",
    )

    expected_contents = "expected"

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            env_realfs.run_wap,
            "watch",
            "--wow-addons-path",
            str(env_realfs.wow_dir_path),
        )

        src_lua_file = env_realfs.project_dir_path / "Dir1" / "Dir1.lua"
        with src_lua_file.open("w") as file:
            file.write("un" + expected_contents)
        with src_lua_file.open("w") as file:
            file.write(expected_contents)

        future.result()

    assert env_realfs.wow_dir_path
    installed_lua_file = env_realfs.wow_dir_path / "Dir1" / "Dir1.lua"
    assert installed_lua_file.exists()
    with installed_lua_file.open("r") as file:
        assert "expected" == file.read()
