import click

from wap import __version__, log
from wap.commands.common import VERSION_STRING_TEMPLATE
from wap.commands.dev_install import dev_install
from wap.commands.new_config import new_config
from wap.commands.package import package
from wap.commands.quickstart import quickstart
from wap.commands.upload import upload
from wap.commands.validate import validate
from wap.commands.watch import watch


@click.group()
@click.version_option(
    version=__version__,
    message=VERSION_STRING_TEMPLATE,
)
def base() -> None:
    """package and upload your WoW addons."""
    # always print out version info on run (will help with issue reports)
    log.info((VERSION_STRING_TEMPLATE + "\n") % {"version": __version__})


SUBCOMMANDS = [package, dev_install, upload, quickstart, new_config, validate, watch]

for subcommand in SUBCOMMANDS:
    base.add_command(subcommand)
