from __future__ import annotations

from pathlib import Path

import click

from wap import log
from wap.commands.common import (
    config_path_option,
    version_option,
    wow_addons_path_option,
)
from wap.commands.dev_install import dev_install
from wap.commands.package import package
from wap.exception import WAPException
from wap.watcher import watch_project


def do_package_and_dev_install(
    ctx: click.Context,
    config_path: Path,
    version: str,
    wow_addons_path: Path,
) -> None:
    try:
        ctx.invoke(
            package,
            config_path=config_path,
            version=version,
        )
        ctx.invoke(
            dev_install,
            config_path=config_path,
            version=version,
            wow_addons_path=wow_addons_path,
        )
        log.info("")  # separate runs from one another
    except WAPException as we:
        log.error(we.message + "\n")
    except click.ClickException as ce:
        log.error(ce.message + "\n")


@click.command()
@config_path_option()
@version_option(help="The version you want to assign your package.")
@wow_addons_path_option()
@click.pass_context
def watch(
    ctx: click.Context,
    config_path: Path,
    version: str,
    wow_addons_path: Path,
) -> None:
    """
    Monitor for any changes in your project and automatically package and install
    to your WoW AddOns directory. You can exit with Ctrl-c.

    This command is a composite of the package and dev-install commands, along with
    a filesystem event watcher on your config file and addon paths. When an event
    is emitted from your filesytem, your addon will be packaged and dev-installed.

    This speeds up the developer feedback-loop, so you don't have to type
    any further wap commands while you develop on your addons.
    """

    for _ in watch_project(config_path=config_path):
        do_package_and_dev_install(
            ctx=ctx,
            config_path=config_path,
            version=version,
            wow_addons_path=wow_addons_path,
        )
