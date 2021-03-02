from pathlib import Path

import click

from wap import log
from wap.commands.common import DEFAULT_CONFIG_PATH, PATH_TYPE
from wap.exception import QuickstartException
from wap.guided_config import DEFAULT_CHANGELOG_PATH, guide
from wap.util import default_wow_addons_path_for_system
from wap.wowversion import WoWVersion

LATEST_RETAIL_VERSION = WoWVersion.from_dot_version("9.0.2")


def write_changelog(path: Path, name: str) -> None:
    with path.open("w") as changelog_file:
        changelog_file.write(f"# {name} Changelog\n\n")
        changelog_file.write(
            "This file is used by *wap* when you upload to Curseforge. It should "
            "contain a record of changes over time to your project.\n\n"
        )
        changelog_file.write("## Example Version 0.0.1\n\n")
        changelog_file.write("- Added feature X\n")
        changelog_file.write("- Fixed bug Y\n")


def write_readme(path: Path, name: str) -> None:
    with path.open("w") as readme_file:
        readme_file.write(f"# {name}\n\n")
        readme_file.write(
            "(This file is not required to run *wap*. It is here as a suggestion to "
            "document your project.)\n\n"
        )
        readme_file.write(
            'This file is written in Markdown, "a lightweight and easy-to-use syntax '
            'for styling all forms of writing".\n\n'
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
        lua_file.write('print(title .. " version " .. version .. " has loaded.")\n')


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
    PROJECT_DIR_PATH must not exist.

    This command is interactive, and will ask you some questions about your project.

    If you later decide you want to change something about how you answered these
    question, edit your config file.

    For example, running:

        wap quickstart MyAddon

    will create a directory structure like the following:

      \b
      MyAddon
      ├── MyAddon
      │   └── Init.lua
      ├── CHANGELOG.md
      ├── README.md
      └── .wap.yml
    """
    # the docstring above contains the \b escape. This prevents paragraph wrapping
    # https://click.palletsprojects.com/en/7.x/documentation/#preventing-rewrapping
    # i'm not sure why i had to adjust the indentation level to get it to line up
    # properly though

    if project_dir_path.exists():
        raise QuickstartException(
            f"{project_dir_path} exists. Choose a path that does not exist for your "
            "new project."
        )

    config = guide(project_dir_name=project_dir_path.resolve().name)
    project_name = config.name

    log.info(
        '\nCreating project directory at "'
        + click.style(f"{project_dir_path}", fg="green")
        + '"'
    )
    project_dir_path.mkdir(parents=True)
    config_path = project_dir_path / DEFAULT_CONFIG_PATH
    log.info(
        'Writing config file at "' + click.style(f"{config_path}", fg="green") + '"'
    )
    config.to_path(config_path)

    log.info(
        "Creating changelog file at '"
        + click.style(f"{DEFAULT_CHANGELOG_PATH}", fg="green")
        + '"'
    )
    write_changelog(project_dir_path / DEFAULT_CHANGELOG_PATH, project_name)

    readme_path = project_dir_path / "README.md"
    log.info('Creating readme at "' + click.style(f"{readme_path}", fg="green"))
    write_readme(readme_path, project_name)

    # guided config puts 1 starter lua file in the toc config's files.
    dir_config = config.addon_configs[0]
    starter_lua_file = dir_config.toc_config.files[0]
    lua_file = project_dir_path / dir_config.path / starter_lua_file
    log.info(
        "Creating starter lua file at '" + click.style(f"{lua_file}", fg="green") + '"'
    )
    lua_file.parent.mkdir()
    write_lua_file(lua_file, project_name)

    log.info(
        click.style(
            "\nProject created! You can now begin developing your project.\n",
            fg="green",
            bold=True,
        )
    )
    log.info(
        "After you `"
        + click.style(f'cd "{project_dir_path}"', fg="magenta")
        + "`, you can get started running some wap commands immediately, such as:"
    )
    log.info("  - " + click.style("wap package", fg="blue"))
    log.info(
        "  - "
        + click.style(
            (
                "wap dev-install --wow-addons-path "
                f'"{default_wow_addons_path_for_system()}"'
            ),
            fg="blue",
        )
    )
    if config.curseforge_config:
        log.info(
            "  - "
            + click.style(
                'wap upload --version "dev" --curseforge-token "<your-token>"',
                fg="blue",
            )
        )

    log.info("\nHave fun!")
