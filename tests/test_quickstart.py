from pathlib import Path

import pytest

from tests.util import Environment, fileset
from wap.exception import QuickstartException


@pytest.mark.parametrize(
    "project_dir_path",
    [
        "MyAddon",
        "subdir/MyAddon",
    ],
    ids=["at cwd", "subdir"],
)
def test_quickstart(
    env: Environment,
    project_dir_path: str,
) -> None:
    env.prepare(
        project_dir_name="empty",
    )

    env.run_wap("quickstart", project_dir_path)

    addon_name = Path(project_dir_path).name

    expected_quickstart_files = {
        Path(f".wap.yml"),
        Path(f"CHANGELOG.md"),
        Path(f"README.md"),
        Path(f"{addon_name}/{addon_name}.lua"),
    }

    # unfortunate naming conflict between env.project_dir_path and project_dir_path.
    # the former is the environment "project directory", but in this case, is just an
    # empty directory. the latter is where the user has quickstarted the new project.
    # the Environment class wasn't really written with this use case in mind, but offers
    # too nice a test fixture to pass up.
    full_project_dir_path = env.project_dir_path / project_dir_path
    actual_quickstart_files = fileset(full_project_dir_path)

    assert expected_quickstart_files == actual_quickstart_files

    # do a simple wap build in the new project dir. this essentially "roundtrips" the
    # output of quickstart to ensure it is functional
    env.run_wap("build", cwd=full_project_dir_path)


def test_quickstart_dir_exists(
    env: Environment,
) -> None:
    env.prepare(
        project_dir_name="empty",
    )

    project_dir_path = env.project_dir_path / "exists"
    project_dir_path.mkdir()

    with pytest.raises(QuickstartException, match=r"exists"):
        env.run_wap("quickstart", str(project_dir_path))
