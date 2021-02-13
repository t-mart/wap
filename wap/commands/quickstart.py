from pathlib import Path
from wap.exception import NewProjectException

import click

from wap.commands.common import (
    DEFAULT_CONFIG_PATH,
    PATH_TYPE,
)
from wap.config import Config, CurseforgeConfig, DirConfig, TocConfig
from wap.wowversion import WoWVersion
from wap.log import info

LATEST_RETAIL_VERSION = WoWVersion.from_dot_version("9.0.2")


def default_config(name: str) -> Config:
    return Config(
        name=name,
        wow_versions=[LATEST_RETAIL_VERSION],
        curseforge_config=CurseforgeConfig(
            project_id="00000",
            changelog_path=Path("CHANGELOG.md"),
            addon_name="fill-this-in",
        ),
        dir_configs=[
            DirConfig(
                path=Path(name),
                toc_config=TocConfig(
                    tags={
                        "Title": name,
                        "Author": "Your name",
                    },
                    files=[Path(name).with_suffix(".lua")],
                ),
            )
        ],
    )


def write_changelog(path: Path, name: str) -> None:
    with path.open("w") as changelog_file:
        changelog_file.write(f"# {name} Changelog\n\n")
        changelog_file.write("Added feature X\n")
        changelog_file.write("Fixed bug Y\n")


def write_readme(path: Path, name: str) -> None:
    with path.open("w") as readme_file:
        readme_file.write(f"# {name}\n\n")
        readme_file.write(
            'This README file is written in Markdown, "a lightweight and easy-to-use '
            'syntax for styling all forms of writing".\n\n'
        )
        readme_file.write(
            "You can learn more about Markdown at "
            "<https://guides.github.com/features/mastering-markdown/>.\n\n"
        )
        readme_file.write(
            "Otherwise, go ahead and describe your project, such as...\n\n"
        )
        readme_file.write("## Features\n\n")
        readme_file.write("- Gives you free gold!\n")
        readme_file.write("- Boosts your DPS!\n")
        readme_file.write(
            "- Did someone say Thunderfury, Blessed Blade of the Windseeker?\n"
        )


def write_lua_file(path: Path, name: str) -> None:
    with path.open("w") as lua_file:
        lua_file.write("-- Your code can go here.\n")
        lua_file.write("-- Here's something to get you started,\n")
        lua_file.write("-- but you can erase it if you wish.\n\n")
        lua_file.write(f'local title = GetAddOnMetadata("{name}", "Title")\n')
        lua_file.write(f'local version = GetAddOnMetadata("{name}", "Version")\n')
        lua_file.write(f'print(title .. " version " .. version .. " initialized")\n')


@click.command()
@click.argument(
    "project_dir_path",
    type=PATH_TYPE,
)
def quickstart(
    project_dir_path: Path,
) -> None:
    """
    Creates a new addon project directory at PROJECT_DIR_PATH with a default structure.
    """
    if project_dir_path.exists():
        raise NewProjectException(
            f"{project_dir_path} exists. Choose a path that does not exist for your "
            "new project."
        )

    info(f"Creating project directory at {project_dir_path}")
    project_dir_path.mkdir()

    project_name = project_dir_path.name

    config = default_config(project_name)
    config_path = project_dir_path / DEFAULT_CONFIG_PATH
    info(f"Creating config file at {config_path}")
    config.to_path(config_path)

    changelog_path = project_dir_path / "CHANGELOG.md"
    info(f"Creating changelog file at {changelog_path}")
    write_changelog(changelog_path, project_name)

    readme_path = project_dir_path / "README.md"
    info(f"Creating readme at {readme_path}")
    write_readme(readme_path, project_name)

    lua_file = project_dir_path / project_name / (project_name + ".lua")
    info(f"Creating starter lua file at {lua_file}")
    lua_file.parent.mkdir()
    write_lua_file(lua_file, project_name)

    info(f"Project created! You can now begin developing your project.")
    info(
        f"After you `cd {project_dir_path}`, you can get started running some wap "
        "commands immediately, such as:"
    )
    info("  - wap build")
    info(
        R'  - wap dev-install --wow-addons-path'
        R'"C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"')
    info("Have fun!")
