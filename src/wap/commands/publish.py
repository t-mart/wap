import shutil
from pathlib import Path

import click

from wap.commands.util import config_path_option, output_path_option
from wap.config import Config
from wap.console import info, warn
from wap.core import get_build_path
from wap.curseforge import RELEASE_TYPES, Changelog, CurseForgeAPI
from wap.exception import ConfigException, CurseForgeAPIException, PathMissingException

DEFAULT_RELEASE_TYPE = "alpha"
WAP_CURSEFORGE_TOKEN_ENVVAR_NAME = "WAP_CF_TOKEN"


@click.command()
@config_path_option()
@output_path_option()
@click.option(
    "-r",
    "--release-type",
    type=click.Choice(list(RELEASE_TYPES)),
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
    "--dry-run",
    is_flag=True,
    type=bool,
    help=("Don't upload anything, but instead just report what would have been done."),
)
def publish(
    config_path: Path,
    output_path: Path,
    release_type: str | None,
    curseforge_token: str,
    dry_run: bool,
) -> None:
    """
    Upload packages to Curseforge.
    """
    config = Config.from_path(config_path)

    if config.publish is None or config.publish.curseforge is None:
        raise ConfigException(
            'A "publish.curseforge" config section must be present to publish'
        )

    cf_config = config.publish.curseforge

    if cf_config.changelog_file is not None:
        changelog_path = config_path.parent / cf_config.changelog_file
        changelog = Changelog.from_path(
            path=changelog_path, type_=cf_config.changelog_type
        )
    elif cf_config.changelog_text is not None:
        changelog = Changelog.from_text(
            text=cf_config.changelog_text, type_=cf_config.changelog_type
        )
    else:
        changelog = Changelog.from_text(text="")
        warn("No changelog text or file provided, so using empty string")

    build_path = get_build_path(output_path, config)
    if not build_path.is_dir():
        raise PathMissingException(
            f'Build path {build_path} is not a directory. Have you run "wap build" yet?'
        )

    info(f"Zipping {build_path}")
    zip_path = Path(
        shutil.make_archive(
            base_name=str(build_path), format="zip", root_dir=build_path
        )
    )

    cf_api = CurseForgeAPI(api_token=curseforge_token)

    info("Getting CurseForge WoW version ids...")
    version_map = cf_api.get_version_map()

    version_ids = []
    for flavor_name, version in config.wow_versions.items():
        try:
            version_ids.append(version_map[version])
        except KeyError as key_error:
            raise CurseForgeAPIException(
                f"Curseforge does not know about version {version} for flavor "
                f"{flavor_name}. Does it actually exist?"
            ) from key_error

    if release_type is None:
        if cf_config.release_type:
            release_type = cf_config.release_type
        else:
            release_type = DEFAULT_RELEASE_TYPE
            warn(
                "No release type specified on command line or in config. Defaulting to "
                f"{DEFAULT_RELEASE_TYPE}"
            )

    if not dry_run:
        info(f"Uploading {zip_path} to CurseForge with version ids {version_ids}")
        with zip_path.open("rb") as zip_file:
            file_id = cf_api.upload(
                project_id=cf_config.project_id,
                archive_file=zip_file,
                display_name=build_path.name,  # Addon-1.2.3
                file_name=zip_path.name,  # Addon-1.2.3.zip
                changelog=changelog,
                game_version_ids=version_ids,
                release_type=release_type,
            )
        if cf_config.slug is not None:
            url = cf_api.uploaded_file_url(file_id=file_id, slug=cf_config.slug)
            info(f"Upload available at {url}")
        else:
            info(f"Uploaded file {file_id}")
            info(
                'Hint: Provide a "slug" in your curseforge config to get an entire '
                "link in output next time."
            )
    else:
        info("Not uploading for dry run")
