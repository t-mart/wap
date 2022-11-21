import shutil
from pathlib import Path

import click

from wap.commands.util import (
    DEFAULT_OUTPUT_PATH,
    config_path_option,
    output_path_option,
)
from wap.config import Config
from wap.console import print, warn
from wap.core import get_build_path
from wap.curseforge import RELEASE_TYPES, Changelog, CurseForgeAPI
from wap.exception import ConfigError, CurseForgeAPIError, PathMissingError

DEFAULT_RELEASE_TYPE = "alpha"
WAP_CURSEFORGE_TOKEN_ENVVAR_NAME = "WAP_CURSEFORGE_TOKEN"


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
    metavar="TOKEN",
    envvar=WAP_CURSEFORGE_TOKEN_ENVVAR_NAME,
    required=True,
    help=(
        "The value of your CurseForge API token. May also be specified in the "
        f"environment variable {WAP_CURSEFORGE_TOKEN_ENVVAR_NAME}."
    ),
)
def publish(
    config_path: Path,
    output_path: Path | None,
    release_type: str | None,
    curseforge_token: str,
) -> None:
    """
    Upload packages to Curseforge.
    """
    config = Config.from_path(config_path)
    if output_path is None:
        output_path = config_path.parent / DEFAULT_OUTPUT_PATH

    if config.publish is None or config.publish.curseforge is None:
        raise ConfigError(
            'A "publish.curseforge" config section should be present to publish. '
            "Please add one and try again."
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
        raise PathMissingError(
            f'Build path {build_path} should be a directory. Have you run "wap build" '
            "yet?"
        )

    print(f"Zipping [path]{build_path}[path]")
    zip_path = Path(
        shutil.make_archive(
            base_name=str(build_path), format="zip", root_dir=build_path
        )
    )

    cf_api = CurseForgeAPI(api_token=curseforge_token)

    print("Getting CurseForge WoW version ids...")
    version_map = cf_api.get_version_map()

    version_ids = []
    for flavor_name, version in config.wow_versions.items():
        try:
            version_ids.append(version_map[version])
        except KeyError as key_error:
            raise CurseForgeAPIError(
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

    print("Uploading to CurseForge...")
    with zip_path.open("rb") as zip_file:
        file_id = cf_api.upload(
            project_id=cf_config.project_id,
            file=zip_file,
            display_name=build_path.name,  # Addon-1.2.3
            file_name=zip_path.name,  # Addon-1.2.3.zip
            changelog=changelog,
            game_version_ids=version_ids,
            release_type=release_type,
        )
    if cf_config.slug is not None:
        url = cf_api.uploaded_file_url(file_id=file_id, slug=cf_config.slug)
        print(f"Upload available at [url]{url}[url]")
    else:
        print(f"Uploaded file {file_id}")
        print(
            '[hint]Hint: Provide a "slug" in your curseforge config to get an entire '
            "link in output next time."
        )
