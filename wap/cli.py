from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from wap import __version__, log, package
from wap.addonspath import WoWAddonsPath
from wap.config import PackageConfig
from wap.curseforge import CurseForgeAPI
from wap.exception import DevInstallException, ReleaseException
from wap.result import Result, ResultMap


class PathType(click.ParamType):
    name = "PATH"

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Path:
        return Path(value).resolve()


class WowAddonsPathType(click.ParamType):
    name = "WOW_ADDONS_DIR"

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> WoWAddonsPath:
        return WoWAddonsPath(path=Path(value).resolve())


PATH_TYPE = PathType()
WOW_ADDONS_PATH_TYPE = WowAddonsPathType()


@click.group()
@click.option(
    "-c",
    "--config-path",
    type=PATH_TYPE,
    default="./.wap.yml",
    envvar="WAP_CONFIG_PATH",
    show_default=True,
    help=(
        "The path of the configuration file. May also be specified in the environment "
        "variable WAP_CONFIG_PATH."
    ),
)
@click.version_option(
    version=__version__,
    message="%(prog)s, version %(version)s",
)
@click.pass_context
def base(ctx: click.Context, config_path: Path) -> None:
    """Build and upload your WoW addons."""
    log.info("wap, version %(version)s" % {"version": __version__})
    ctx.obj = config_path


@base.command()
@click.option(
    "-v",
    "--version",
    "addon_version",
    default="dev",
    show_default=True,
    help="The developer-defined version of your addon package.",
)
@click.option(
    "-o",
    "--output-path",
    type=PATH_TYPE,
    default="./dist",
    show_default=True,
    help="The output directory in which to create the build.",
)
@click.pass_obj
def build(
    config_path: Path,
    output_path: Path,
    addon_version: str,
) -> None:
    """
    Builds packages, creating a directory with your packaged addon and a zip archive.
    """
    config = PackageConfig.from_path(path=config_path)
    result_map = ResultMap()

    for wow_version in config.wow_version_configs:
        build_path = package.build(
            config_path=config_path,
            package_name=config.name,
            dir_configs=config.dir_configs,
            output_path=output_path,
            addon_version=addon_version,
            wow_version_config=wow_version,
        )

        zip_path = package.zip(
            build_path=build_path,
            package_name=config.name,
            output_path=output_path,
            addon_version=addon_version,
            wow_version_config=wow_version,
        )

        result_map.add_by_wow_version_config(
            wow_version_config=wow_version,
            result=Result(build_path=build_path, zip_path=zip_path),
        )

    result_map.write()


@base.command()
@click.option(
    "-v",
    "--version",
    "addon_version",
    required=True,
    help="The developer-defined version of your addon package.",
)
@click.option(
    "-o",
    "--output-path",
    type=PATH_TYPE,
    default="./dist",
    show_default=True,
    help="The output directory in which to create the build.",
)
@click.option(
    "-r",
    "--release-type",
    type=click.Choice(list(CurseForgeAPI.RELEASE_TYPES)),
    default="alpha",
    show_default=True,
    help="The type of release to make.",
)
@click.option(
    "--curseforge-token",
    envvar="WAP_CURSEFORGE_TOKEN",
    required=True,
    help=(
        "The value of your CurseForge API token. May also be specified in the "
        "environment variable WAP_CURSEFORGE_TOKEN."
    ),
)
@click.pass_obj
def release(
    config_path: Path,
    output_path: Path,
    addon_version: str,
    release_type: str,
    curseforge_token: str,
) -> None:
    """
    Releases packages to CurseForge.
    """
    config = PackageConfig.from_path(path=config_path)
    result_map = ResultMap()

    if not config.curseforge_config:
        raise ReleaseException(
            'A "curseforge" section must be provided in config to do releases'
        )

    if (
        # if we're not generating any tocs (which will differentiate the addon dirs)
        all(dir_config.toc_config is None for dir_config in config.dir_configs)
        # and if we have multiple versions to deploy
        and len(config.wow_version_configs) > 1
    ):
        log.warn(
            "TOC file generation is off and because classic and retail versions are "
            "being uploaded, there will be no different between the uploaded files. "
            "CurseForge will reject one of them after processing."
        )

    curseforge_api = CurseForgeAPI(api_token=curseforge_token)

    for wow_version_config in config.wow_version_configs:
        build_path = package.build(
            config_path=config_path,
            package_name=config.name,
            dir_configs=config.dir_configs,
            output_path=output_path,
            addon_version=addon_version,
            wow_version_config=wow_version_config,
        )

        zip_path = package.zip(
            build_path=build_path,
            package_name=config.name,
            output_path=output_path,
            addon_version=addon_version,
            wow_version_config=wow_version_config,
        )

        file_id = package.release(
            package_name=config.name,
            package_zip_path=zip_path,
            addon_version=addon_version,
            release_type=release_type,
            wow_version=wow_version_config,
            changelog_path=config_path.parent / config.curseforge_config.changelog_path,
            project_id=config.curseforge_config.project_id,
            curseforge_api=curseforge_api,
            addon_name=config.curseforge_config.addon_name,
        )

        result_map.add_by_wow_version_config(
            wow_version_config=wow_version_config,
            result=Result(
                build_path=build_path, zip_path=zip_path, curseforge_file_id=file_id
            ),
        )

    result_map.write()


@base.command()
@click.option(
    "-v",
    "--version",
    "addon_version",
    default="dev",
    show_default=True,
    help="The developer-defined version of your addon package.",
)
@click.option(
    "-o",
    "--output-path",
    type=PATH_TYPE,
    default="./dist",
    show_default=True,
    help="The output directory in which to create the build.",
)
@click.option(
    "-w",
    "--wow-addons-path",
    envvar="WAP_WOW_ADDONS_PATH",
    required=True,
    type=WOW_ADDONS_PATH_TYPE,
    help=(
        'Your WoW addons path, such as "/path/to/WoW/Interface/Addons". May also be '
        "specified in the environment variable WAP_WOW_ADDONS_PATH."
    ),
)
@click.pass_obj
def dev_install(
    config_path: Path,
    addon_version: str,
    output_path: Path,
    wow_addons_path: WoWAddonsPath,
) -> None:
    """
    Installs a package to your local WoW installation's AddOns directory.
    """

    config = PackageConfig.from_path(path=config_path)

    wow_version_config = config.wow_version_by_type(wow_addons_path.type_)

    if not wow_version_config:
        raise DevInstallException(
            f"No build for your WoW installation is configured. {wow_addons_path.path} "
            f"is for {wow_addons_path.type_} and you do not have a build for "
            f"{wow_addons_path.type_} in your configuration."
        )

    build_path = package.build(
        config_path=config_path,
        package_name=config.name,
        dir_configs=config.dir_configs,
        output_path=output_path,
        addon_version=addon_version,
        wow_version_config=wow_version_config,
    )

    dev_install_paths = package.dev_install(
        build_path=build_path,
        wow_addons_path=wow_addons_path,
        package_name=config.name,
    )

    result_map = ResultMap()
    result_map.add_by_wow_version_config(
        wow_version_config=wow_version_config,
        result=Result(
            build_path=build_path,
            dev_install_paths=dev_install_paths,
        ),
    )
    result_map.write()
