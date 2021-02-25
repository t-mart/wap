import json
from pathlib import Path

import click

from wap import addon, log
from wap.commands.common import (
    DEFAULT_RELEASE_TYPE,
    WAP_CURSEFORGE_TOKEN_ENVVAR_NAME,
    addon_version_option,
    config_path_option,
    json_option,
)
from wap.config import Config
from wap.curseforge import CurseForgeAPI
from wap.exception import UploadException


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
def upload(
    config_path: Path,
    addon_version: str,
    release_type: str,
    curseforge_token: str,
    show_json: bool,
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
            config_path=config_path,
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
