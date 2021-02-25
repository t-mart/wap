import json
from pathlib import Path
from typing import Optional

import click

from wap import addon, log
from wap.changelog import CHANGELOG_TYPES, Changelog
from wap.commands.common import (
    DEFAULT_RELEASE_TYPE,
    WAP_CURSEFORGE_TOKEN_ENVVAR_NAME,
    addon_version_option,
    config_path_option,
    json_option,
)
from wap.config import Config
from wap.curseforge import CurseForgeAPI
from wap.exception import ChangelogException, UploadException


@click.command()
@config_path_option()
@json_option()
@addon_version_option(required=True)
@click.option(
    "-r",
    "--release-type",
    type=click.Choice(list(CurseForgeAPI.RELEASE_TYPES)),
    default=DEFAULT_RELEASE_TYPE,
    show_default=True,
    help="The type of release to make.",
)
@click.option(
    "--curseforge-token",
    envvar=WAP_CURSEFORGE_TOKEN_ENVVAR_NAME,
    required=True,
    help=(
        "The value of your CurseForge API token. May also be specified in the "
        "environment variable WAP_CURSEFORGE_TOKEN."
    ),
)
@click.option(
    "--changelog-contents",
    help=(
        "The contents of your changelog that will be displayed with your upload on "
        "CurseForge. If you have also provided a changelog-file in your config, "
        "this option will take precedence. --changelog-type must also be provided if "
        "using this option."
    ),
)
@click.option(
    "--changelog-type",
    type=click.Choice(list(CHANGELOG_TYPES), case_sensitive=False),
    help=(
        "The format of your changelog contents. --changelog-contents must also be "
        "provided if using this option."
    ),
)
def upload(
    config_path: Path,
    addon_version: str,
    release_type: str,
    curseforge_token: str,
    show_json: bool,
    changelog_contents: Optional[str],
    changelog_type: Optional[str],
) -> int:
    """
    Uploads packages to CurseForge.
    """
    config = Config.from_path(config_path)

    curseforge_config = config.curseforge_config
    if curseforge_config is None:
        raise UploadException(
            'A "curseforge" configuration section must be provided in config to upload'
        )

    if (changelog_contents is None) ^ (changelog_type is None):
        raise ChangelogException(
            "--changelog-contents and --changelog-type must be used together or "
            "not at all."
        )
    else:

        if changelog_contents is not None:
            changelog = Changelog(
                contents=changelog_contents,
                type=changelog_type,  # type: ignore
            )
        elif curseforge_config.changelog_path is not None:
            changelog_path = config_path.parent / curseforge_config.changelog_path
            if not changelog_path.is_file():
                raise UploadException(
                    f'Curseforge config has changelog path "{changelog_path}", but it '
                    "is not a file. This path must point to a file, must be relative "
                    f'to the parent of the config file ("{config_path.resolve()}") '
                    "and, if it is in a subdirectory, must only use forward slashes "
                    '("/"). Or, you may use the --changelog-contents and '
                    "--changelog-type options "
                )
            changelog = Changelog.from_path(changelog_path)

    output_map = {}

    curseforge_api = CurseForgeAPI(api_token=curseforge_token)

    for wow_version in config.wow_versions:
        zip_path = addon.get_zip_path(
            addon_name=config.name,
            wow_version=wow_version,
            addon_version=addon_version,
        )

        if not zip_path.is_file():
            log.error(
                "Expected zip file not found. Have you run `"
                + click.style(f'wap build --addon-version "{addon_version}"', fg="blue")
                + "` yet?"
            )
            raise UploadException(f'Zip file "{zip_path}" not found.')

        upload_url = addon.upload_addon(
            addon_name=config.name,
            curseforge_config=curseforge_config,
            changelog=changelog,
            wow_version=wow_version,
            zip_file_path=zip_path,
            addon_version=addon_version,
            release_type=release_type,
            curseforge_api=curseforge_api,
        )

        output_map[wow_version.type()] = {
            "curseforge_upload_url": upload_url,
        }

    if show_json:
        click.echo(json.dumps(output_map, indent=2))

    return 0
