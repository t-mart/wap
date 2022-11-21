from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Literal, cast, get_args

import click
from attrs import frozen
from watchfiles import watch

from wap.commands.util import (
    DEFAULT_OUTPUT_PATH,
    clean_option,
    config_path_option,
    output_path_option,
    wow_addons_dir_options,
)
from wap.config import AddonConfig, Config
from wap.console import print, warn
from wap.core import get_build_path
from wap.exception import ConfigError, PathExistsError, PathTypeError
from wap.fileops import clean_dir, copy_path, delete_path, symlink
from wap.toc import Toc
from wap.wow import FLAVOR_MAP, FLAVOR_NAMES, FlavorName, Version


@frozen(kw_only=True)
class AddonBuildResult:
    path: Path

    def link(self, wow_addons_path: Path, force: bool) -> Path | None:
        """
        Links this built addon to a WoW addons directory. Returns the link path.
        """
        link_path = wow_addons_path / self.path.name

        if (
            force
            and link_path.exists()
            and (link_path.resolve() != self.path.resolve())
        ):
            delete_path(link_path)

        symlink(new_path=link_path, target_path=self.path)

        return link_path


@frozen(kw_only=True)
class Addon:
    source_path: Path
    include_paths: Sequence[Path]
    include_path_root: Path
    tocs: Sequence[Toc]

    @classmethod
    def create(
        cls,
        addon_config: AddonConfig,
        config: Config,
        config_path: Path,
    ) -> Addon:
        config_dir = config_path.parent

        source_path = (config_dir / addon_config.path).resolve()

        include_paths = (
            resolve_globs(root_path=config_dir, glob_patterns=addon_config.include)
            if addon_config.include
            else []
        )

        tocs = []
        if addon_config.toc is not None:
            wow_versions = []
            for flavor_name, flavor_version in config.wow_versions.items():
                wow_version = Version.from_dotted(flavor_version)
                toc = Toc.from_toc_config(
                    toc_config=addon_config.toc,
                    wow_version=wow_version,
                    flavor_suffix=FLAVOR_MAP[flavor_name].toc_suffix,
                    config=config,
                    source_path=source_path,
                )
                tocs.append(toc)
                wow_versions.append(wow_version)

            # create just a standard toc with no suffix because curseforge purportedly
            # requires it. just use the max wow_version from those provided.
            max_wow_version = max(wow_versions)
            tocs.append(
                Toc.from_toc_config(
                    toc_config=addon_config.toc,
                    wow_version=max_wow_version,
                    config=config,
                    source_path=source_path,
                )
            )

        return cls(
            source_path=source_path,
            tocs=tocs,
            include_paths=include_paths,
            include_path_root=config_path.parent,
        )

    def build(self, package_path: Path, clean: bool) -> AddonBuildResult:
        build_path = package_path / self.source_path.name

        try:
            build_path.mkdir(parents=True, exist_ok=True)
        except FileExistsError as file_exists_error:
            raise PathExistsError(
                f"Output directory {build_path} should not be a file"
            ) from file_exists_error

        if clean:
            clean_dir(build_path)

        if not self.source_path.is_dir():
            raise PathTypeError(f"Addon path {self.source_path} should be a directory.")

        # copy source to dest
        copy_path(self.source_path, build_path)

        # keep track of what we've built
        addon_paths = {
            path.relative_to(self.source_path) for path in self.source_path.rglob("*")
        }

        # copy includes
        for include_path in self.include_paths:
            include_path_target = build_path / include_path.name
            rel_path = Path(include_path.name)
            if rel_path in addon_paths:
                warn(f"Include path {rel_path} already exists in output directory")
            else:
                addon_paths.add(rel_path)
            copy_path(include_path, include_path_target)

        # write tocs
        toc_paths = []
        for toc in self.tocs:
            toc.validate(build_path)
            toc_path_target = build_path / toc.filename(build_path.name)
            rel_path = Path(toc_path_target.name)
            if rel_path in addon_paths:
                warn(
                    f"Generated TOC path {rel_path} already exists in output "
                    "directory"
                )
            else:
                addon_paths.add(rel_path)
            try:
                toc_path_target.write_text(toc.generate())
            except (PermissionError, IsADirectoryError) as error:
                # on windows, raises PermissionError, linux raises IsADirectoryError
                raise PathExistsError(
                    f"Generated TOC file {toc_path_target} should not exist in your "
                    "source files."
                ) from error
            toc_paths.append(toc_path_target)

        return AddonBuildResult(path=build_path)

    @property
    def watch_paths(self) -> Sequence[Path]:
        return [self.source_path, *self.include_paths]


@frozen(kw_only=True)
class Package:
    addons: Sequence[Addon]
    build_path: Path

    @classmethod
    def create(cls, config: Config, config_path: Path, output_path: Path) -> Package:
        package = cls(
            addons=[
                Addon.create(
                    addon_config=addon_config,
                    config=config,
                    config_path=config_path,
                )
                for addon_config in config.package
            ],
            build_path=get_build_path(output_path=output_path, config=config),
        )

        # dupe check
        seen_addon_paths = set()
        for addon in package.addons:
            if addon.source_path not in seen_addon_paths:
                seen_addon_paths.add(addon.source_path)
            else:
                raise ConfigError(
                    "Addon paths should be unique. Found duplicate for "
                    f"{addon.source_path}."
                )

        return package

    def build(self, clean: bool) -> Sequence[AddonBuildResult]:
        return [
            addon.build(package_path=self.build_path, clean=clean)
            for addon in self.addons
        ]

    @property
    def watch_paths(self) -> Sequence[Path]:
        return [watch_path for addon in self.addons for watch_path in addon.watch_paths]


AutoChoiceName = Literal["auto"]
AUTO_CHOICE: AutoChoiceName = get_args(AutoChoiceName)[0]


def get_addon_link_targets(
    flavors_to_link: Sequence[FlavorName | AutoChoiceName],
    config: Config,
    mainline_addons_path: Path,
    wrath_addons_path: Path,
    vanilla_addons_path: Path,
) -> dict[FlavorName, Path]:
    flavor_addons_path_map: dict[FlavorName, Path] = {
        "mainline": mainline_addons_path,
        "wrath": wrath_addons_path,
        "vanilla": vanilla_addons_path,
    }
    uniq_flavors = set(flavors_to_link)

    if AUTO_CHOICE in uniq_flavors:
        if len(uniq_flavors) > 1:
            raise click.BadOptionUsage(
                "link",
                ('If linking "--auto", it should be the only provided link option.'),
            )

        config_flavors = set(config.wow_versions)
        existing_installs = set(
            flavor_name
            for flavor_name in FLAVOR_NAMES
            if flavor_addons_path_map[flavor_name].exists()
        )
        return {
            flavor_name: flavor_addons_path_map[flavor_name]
            for flavor_name in config_flavors & existing_installs
        }

    return {
        link_flavor: flavor_addons_path_map[link_flavor]
        for link_flavor in cast(set[FlavorName], uniq_flavors)
    }


def resolve_globs(root_path: Path, glob_patterns: Sequence[str]) -> Sequence[Path]:
    paths = []
    for pattern in glob_patterns:
        matching_paths = list(root_path.glob(pattern))
        if len(matching_paths) == 0:
            warn(
                f'Include pattern "{pattern}" should match some paths, but none were '
                "found."
            )
        paths.extend(matching_paths)
    return paths


@click.command()
@config_path_option()
@output_path_option()
@clean_option()
@click.option(
    "-l",
    "--link",
    "flavors_to_link",
    type=click.Choice([AUTO_CHOICE, *FLAVOR_NAMES], case_sensitive=False),
    multiple=True,
    is_flag=False,
    flag_value=AUTO_CHOICE,
    help=(
        """
        Create a symlink from packaged addon folder into a flavor's WoW AddOns. This is
        handy for installing your own stuff, so you can work on it and test it quickly.
        If no argument is provided to this option or if "auto" is provided, then links
        will be made into each flavor that exists on this system and is supported by the
        package. This option can be provided mulitple times.
        """
    ),
    show_default=True,
)
@click.option(
    "--link-force",
    is_flag=True,
    help=(
        "If --link and the link path already exists, delete it first so that this link "
        "can be made."
    ),
)
@click.option(
    "-w",
    "--watch",
    "enable_watch",
    is_flag=True,
    help=("Repackage when source files change"),
)
@wow_addons_dir_options()
def build(
    config_path: Path,
    output_path: Path | None,
    clean: bool,
    flavors_to_link: Sequence[FlavorName | AutoChoiceName],
    link_force: bool,
    enable_watch: bool,
    mainline_addons_path: Path,
    wrath_addons_path: Path,
    vanilla_addons_path: Path,
) -> None:
    """
    Build addons into a playable, distributable package.
    """
    config_path = config_path.resolve()

    if output_path is None:
        output_path = config_path.parent / DEFAULT_OUTPUT_PATH

    # used to signal if this is the first time we're building, where we might print more
    # information that subsequent times (in watch mode).
    first_time = True

    def build_once() -> Package:
        config = Config.from_path(config_path)
        package = Package.create(
            config=config,
            config_path=config_path,
            output_path=output_path,  # type: ignore
            # mypy bug https://github.com/python/mypy/issues/2608
        )

        built_addons = package.build(clean=clean)

        addon_link_dirs = get_addon_link_targets(
            flavors_to_link,
            config,
            mainline_addons_path=mainline_addons_path,
            wrath_addons_path=wrath_addons_path,
            vanilla_addons_path=vanilla_addons_path,
        )

        for addon in built_addons:
            build_addon_msg = f"Built addon [addon]{addon.path.name}[/addon]"
            if first_time:
                build_addon_msg += f" at [path]{addon.path}[/path]"
            print(build_addon_msg)

            for flavor_name, addon_dir in addon_link_dirs.items():
                link_path = addon.link(wow_addons_path=addon_dir, force=link_force)
                if first_time:
                    print(
                        f"Linked [path]{link_path}[/path] "
                        f"([flavor]{flavor_name}[/flavor]) to "
                        f"[addon]{addon.path.name}[/addon]"
                    )

        build_package_msg = (
            f"Built package [package]{package.build_path.name}[/package]"
        )
        if first_time:
            build_package_msg += f" at [path]{package.build_path}[/path]"
        print(build_package_msg)

        return package

    package = build_once()
    first_time = False

    if enable_watch:
        print("Running in watch mode. Press [key]Ctrl-C[/key] at any time to quit.")
        project_file_paths = {*package.watch_paths, config_path}
        for paths_changed in watch_paths(config_path.parent):
            if any(
                changed_path.is_relative_to(watch_path)
                for watch_path in project_file_paths
                for changed_path in paths_changed
            ):
                print("Project file changed, rebuilding...\n")
                package = build_once()
                project_file_paths = {*package.watch_paths, config_path}


def watch_paths(*paths: Path) -> Iterator[Iterable[Path]]:
    for changes in watch(*paths):
        yield {Path(path) for _, path in changes}
