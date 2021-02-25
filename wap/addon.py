import shutil
from collections.abc import Sequence
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import click

from wap import log
from wap.config import CurseforgeConfig, DirConfig
from wap.curseforge import CHANGELOG_SUFFIX_MAP, CurseForgeAPI
from wap.exception import BuildException, UploadException
from wap.toc import write_toc
from wap.util import delete_path
from wap.wowversion import WoWVersion


def get_output_path() -> Path:
    return Path("dist")


def get_build_path(
    addon_name: str, addon_version: str, wow_version: WoWVersion
) -> Path:
    return get_output_path() / f"{addon_name}-{addon_version}-{wow_version.type()}"


def get_zip_path(addon_name: str, addon_version: str, wow_version: WoWVersion) -> Path:
    bp = get_build_path(
        addon_name=addon_name,
        addon_version=addon_version,
        wow_version=wow_version,
    )
    return bp.with_name(bp.name + ".zip")


def build_addon(
    config_path: Path,
    addon_name: str,
    dir_configs: Sequence[DirConfig],
    addon_version: str,
    wow_version: WoWVersion,
) -> Path:
    build_path = get_build_path(
        addon_name=addon_name,
        addon_version=addon_version,
        wow_version=wow_version,
    )

    if build_path.exists():
        delete_path(build_path)

    build_path.mkdir(parents=True)

    for dir_config in dir_configs:
        src_dir = config_path.parent / dir_config.path

        if not src_dir.is_dir():
            raise BuildException(
                f"{src_dir} is not a directory",
            )

        dst_dir = build_path / src_dir.name

        shutil.copytree(src_dir, dst_dir)

        toc_path = dst_dir / (src_dir.name + ".toc")

        if toc_path.exists():
            log.warn(
                f"A TOC file at {toc_path.name} exists in {dir_config.path}, but will "
                "be overwritten."
            )
            delete_path(toc_path)

        write_toc(
            toc_config=dir_config.toc_config,
            path=toc_path,
            addon_version=addon_version,
            wow_version=wow_version,
        )

    log.info(
        f"Built addon "
        + click.style(f"{addon_name}", fg="blue")
        + " ("
        + click.style(f"{wow_version.type()}", fg="magenta")
        + ") at "
        + click.style(f"{build_path}", fg="green")
    )

    return build_path


def zip_addon(addon_name: str, addon_version: str, wow_version: WoWVersion) -> Path:
    build_path = get_build_path(
        addon_name=addon_name, addon_version=addon_version, wow_version=wow_version
    )
    zip_path = get_zip_path(
        addon_name=addon_name, addon_version=addon_version, wow_version=wow_version
    )

    if zip_path.exists():
        delete_path(zip_path)

    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for path in build_path.rglob("*"):
            zip_file.write(
                filename=path,
                arcname=path.relative_to(build_path),
            )

    log.info(
        f"Zipped addon "
        + click.style(f"{addon_name}", fg="blue")
        + " ("
        + click.style(f"{wow_version.type()}", fg="magenta")
        + ") at "
        + click.style(f"{zip_path}", fg="green")
    )

    return zip_path


def upload_addon(
    *,
    addon_name: str,
    config_path: Path,
    curseforge_config: CurseforgeConfig,
    wow_version: WoWVersion,
    zip_file_path: Path,
    addon_version: str,
    release_type: str,
    curseforge_api: CurseForgeAPI,
) -> str:
    cf_wow_version_id = curseforge_api.get_version_id(version=wow_version.dot_version())

    changelog_path = config_path.parent / curseforge_config.changelog_path
    if not changelog_path.is_file():
        raise UploadException(f"Changelog file {changelog_path} is not a file")

    with changelog_path.open("r") as changelog_file:
        changelog_contents = changelog_file.read()

    normalized_changelog_suffix = changelog_path.suffix.lower()
    if normalized_changelog_suffix in CHANGELOG_SUFFIX_MAP:
        changelog_type = CHANGELOG_SUFFIX_MAP[normalized_changelog_suffix]
    else:
        log.warn(
            f"Unable to determine changelog type from extension for {changelog_path}, "
            'so assuming "text"'
        )
        changelog_type = "text"

    with zip_file_path.open("rb") as package_archive_file:
        file_id = curseforge_api.upload_addon_file(
            project_id=curseforge_config.project_id,
            archive_file=package_archive_file,
            display_name=f"{addon_version}-{wow_version.type()}",
            changelog_contents=changelog_contents,
            changelog_type=changelog_type,
            wow_version_id=cf_wow_version_id,
            release_type=release_type,
            file_name=f"{addon_name}-{addon_version}-{wow_version.type()}.zip",
        )

    url = curseforge_api.uploaded_file_url(
        addon_name=curseforge_config.addon_name,
        file_id=file_id,
    )
    log.info(
        f"Uploaded "
        + click.style(f"{addon_name}", fg="blue")
        + " ("
        + click.style(f"{wow_version.type()}", fg="magenta")
        + ") at  to CurseForge at "
        + click.style(f"{url}", fg="green")
    )

    return url


def dev_install_addon(
    *,
    build_path: Path,
    wow_addons_path: Path,
    wow_version: WoWVersion,
) -> Sequence[Path]:
    installed_paths = []

    for addon_path in build_path.iterdir():
        install_addon_path = wow_addons_path / addon_path.name

        if install_addon_path.exists():
            delete_path(install_addon_path)

        shutil.copytree(addon_path, install_addon_path)

        installed_paths.append(install_addon_path)

        log.info(
            f"Installed addon directory "
            + click.style(f"{addon_path.name}", fg="blue")
            + " ("
            + click.style(f"{wow_version.type()}", fg="magenta")
            + ") to "
            + click.style(f"{install_addon_path}", fg="green")
        )

    return installed_paths
