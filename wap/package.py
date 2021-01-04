from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Sequence
from zipfile import ZIP_DEFLATED, ZipFile

from wap import log
from wap.addonspath import WoWAddonsPath
from wap.config import DirConfig, WowVersionConfig
from wap.curseforge import CurseForgeAPI
from wap.exception import BuildException, DevInstallException
from wap.toc import write_toc

CHANGELOG_SUFFIX_MAP = {
    ".md": "markdown",
    ".html": "html",
    ".txt": "text",
}


def build(
    *,
    config_path: Path,
    package_name: str,
    dir_configs: Sequence[DirConfig],
    output_path: Path,
    addon_version: str,
    wow_version_config: WowVersionConfig,
) -> Path:
    build_path = (
        output_path / f"{package_name}-{addon_version}-{wow_version_config.type_}"
    )

    if build_path.exists():
        shutil.rmtree(build_path)

    build_path.mkdir(parents=True)

    for dir_config in dir_configs:
        src_dir = config_path.parent / dir_config.path

        # this catches 1) the directory not existing and 2) the source_dir is not
        # actually a dir, which is not allowed: WoW addons must be directories that go
        # into the Interface/Addons dir
        if not src_dir.is_dir():
            raise BuildException(
                f"{src_dir} is not a directory",
            )

        dst_dir = build_path / src_dir.name

        shutil.copytree(src_dir, dst_dir)

        toc_path = dst_dir / (src_dir.name + ".toc")
        if dir_config.toc_config:
            toc_config = dir_config.toc_config
            write_toc(
                toc_path=toc_path,
                addon_version=addon_version,
                interface_version=wow_version_config.interface_version(),
                tags=toc_config.tags,
                files=[dst_dir / file for file in toc_config.files],
            )
        elif not toc_path.exists():
            log.warn(f"{dir_config.path} does not have expected TOC file at {toc_path}")

    log.info(f"Built package {package_name} at {build_path}")

    return build_path


def zip(
    *,
    build_path: Path,
    package_name: str,
    output_path: Path,
    addon_version: str,
    wow_version_config: WowVersionConfig,
) -> Path:
    zip_path = (
        output_path / f"{package_name}-{addon_version}-{wow_version_config.type_}.zip"
    )

    if zip_path.exists():
        zip_path.unlink()

    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for path in build_path.rglob("*"):
            zip_file.write(
                filename=path,
                arcname=path.relative_to(build_path),
            )

    log.info(f"Zipped package {package_name} at {zip_path}")

    return zip_path


def release(
    *,
    wow_version: WowVersionConfig,
    package_name: str,
    package_zip_path: Path,
    addon_version: str,
    release_type: str,
    project_id: str,
    changelog_path: Path,
    curseforge_api: CurseForgeAPI,
    addon_name: Optional[str] = None,
) -> int:
    cf_wow_version_id = curseforge_api.get_version_id(version=wow_version.version)

    if not changelog_path.is_file():
        raise BuildException(f"Changelog file {changelog_path} for is not a file")

    with changelog_path.open("r") as changelog_file:
        changelog_contents = changelog_file.read()

    normalized_changelog_suffix = changelog_path.suffix.lower()
    if normalized_changelog_suffix in CHANGELOG_SUFFIX_MAP:
        changelog_type = CHANGELOG_SUFFIX_MAP[normalized_changelog_suffix]
    else:
        log.warn(
            f"Unable to determine changelog type from extension for {changelog_path}, "
            "so assuming text"
        )
        changelog_type = "text"

    with package_zip_path.open("rb") as package_archive_file:
        file_id = curseforge_api.upload_addon_file(
            project_id=project_id,
            archive_file=package_archive_file,
            display_name=f"{addon_version}-{wow_version.type_}",
            changelog_contents=changelog_contents,
            changelog_type=changelog_type,
            wow_version_id=cf_wow_version_id,
            release_type=release_type,
            file_name=f"{package_name}-{addon_version}-{wow_version.type_}.zip",
        )

    release_log_str = f"Released {package_name} to CurseForge "
    if addon_name is not None:
        url = curseforge_api.UPLOADED_FILE_URL_TEMPLATE.format(
            addon_name=addon_name,
            file_id=file_id,
        )
        release_log_str += f"at {url}"
    else:
        release_log_str += f"with file_id {file_id}"
    log.info(release_log_str)

    return file_id


def dev_install(
    *,
    build_path: Path,
    package_name: str,
    wow_addons_path: WoWAddonsPath,
) -> list[Path]:
    installed_paths = []

    for addon_path in build_path.iterdir():
        if not addon_path.is_dir():
            raise DevInstallException(
                f"Built addon at {addon_path} contains not-directory files"
            )

        install_addon_path = wow_addons_path.path / addon_path.name

        if install_addon_path.exists():
            shutil.rmtree(install_addon_path)

        shutil.copytree(addon_path, install_addon_path)

        installed_paths.append(install_addon_path)

    log.info(f"Installed {package_name} to {wow_addons_path.path}")
    return installed_paths
