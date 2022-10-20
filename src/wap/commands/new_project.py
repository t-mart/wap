import textwrap
from pathlib import Path

import click

from wap.console import print
from wap.prompt import prompt_for_config


@click.command()
def new_project() -> None:
    """
    Create a new project.
    """
    config = prompt_for_config(mode="new-project")

    project_path = Path.cwd() / config.name
    project_path.mkdir()

    # create the following structure
    # - README.md
    # - Addon/
    #   - Main.lua
    # - wap.json

    config_path = project_path / "wap.json"
    config.write_to_path(config_path, indent=True)

    readme_md_text = textwrap.dedent(
        f"""\
        # {config.name}

        This addon helps you...
        """
    )
    readme_path = project_path / "README.md"
    readme_path.write_text(readme_md_text)

    main_lua_text = textwrap.dedent(
        f"""\
        -- Your code can go here.
        -- Here's something to get you started, but you can erase it if you wish.

        local title = GetAddOnMetadata("{config.name}", "Title")
        local version = GetAddOnMetadata("{config.name}", "Version")
        print(title .. " version " .. version .. " has loaded")
        """
    )
    main_lua_path = project_path / config.name / "Main.lua"
    main_lua_path.parent.mkdir()
    main_lua_path.write_text(main_lua_text)

    print(
        f"Project for package [package]{project_path.name}[/package] created at "
        f"[path]{project_path}[/path]"
    )
