from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Literal, cast, get_args

import click
from attrs import frozen
from watchfiles import watch

from wap.commands.util import (
    clean_option,
    config_path_option,
    output_path_option,
    wow_addons_dir_options,
)
from wap.config import AddonConfig, Config
from wap.console import info, warn
from wap.core import get_build_path
from wap.exception import ConfigException, PathExistsException, PathTypeException
from wap.fileops import clean_dir, copy_path, symlink
from wap.toc import Toc
from wap.wow import FLAVOR_MAP, FLAVOR_NAMES, FlavorName, Version


@frozen(kw_only=True)
class AddonBuildResult:
    path: Path

    def link(self, wow_addons_path: Path) -> Path | None:
        """
        Links this built addon to a WoW addons directory. Returns the link path if one
        was made. Otherwise, returns None.
        """
        link_path = wow_addons_path / self.path.name
        if link_path.resolve() != self.path.resolve():
            symlink(new_path=link_path, target_path=self.path)
            return link_path

        return None


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
                wow_version = Version(flavor_version)
                toc = Toc.from_toc_config(
                    toc_config=addon_config.toc,
                    wow_version=wow_version,
                    addon_version=config.version,
                    suffix=FLAVOR_MAP[flavor_name].toc_suffix,
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
                    addon_version=config.version,
                    suffix="",
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
            raise PathExistsException(
                f"Output directory {build_path} already exists as a file"
            ) from file_exists_error

        if clean:
            clean_dir(build_path)

        if not self.source_path.is_dir():
            raise PathTypeException(
                f"Addon path {self.source_path} must be a directory"
            )

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
            except PermissionError as perm_error:
                raise PathExistsException(
                    f"Cannot write generated toc {toc_path_target} because it already "
                    "exists as a directory"
                ) from perm_error
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
        addon_paths = [addon_config.path for addon_config in config.package]
        if len(addon_paths) > len(set(addon_paths)):
            raise ConfigException("Addon paths in package must be unique")
        return cls(
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
) -> set[Path]:
    flavor_addons_path_map: dict[FlavorName, Path] = {
        "mainline": mainline_addons_path,
        "wrath": wrath_addons_path,
        "vanilla": vanilla_addons_path,
    }
    uniq_flavors = set(flavors_to_link)

    if AUTO_CHOICE in uniq_flavors:
        if len(uniq_flavors) > 1:
            raise click.BadOptionUsage(
                "link", 'If linking "auto", it must be the only link'
            )

        config_flavors = set(config.wow_versions)
        existing_installs = set(
            flavor_name
            for flavor_name in FLAVOR_NAMES
            if flavor_addons_path_map[flavor_name].exists()
        )
        return {
            flavor_addons_path_map[flavor_name]
            for flavor_name in config_flavors & existing_installs
        }

    return {
        flavor_addons_path_map[link_flavor]
        for link_flavor in cast(set[FlavorName], uniq_flavors)
    }


def resolve_globs(root_path: Path, glob_patterns: Sequence[str]) -> Sequence[Path]:
    paths = []
    for pattern in glob_patterns:
        matching_paths = list(root_path.glob(pattern))
        if len(matching_paths) == 0:
            warn(f'Include "{pattern}" matched no paths')
        paths.extend(matching_paths)
    return paths


# TODO: This help text is too bulky. I'd rather take the NPM approach, where this text
# is barebones, but the online docs are thorough. Heck, we can even write a help
# subcommand that webbroswer.open's up to the help page.


@click.command()
@config_path_option()
@output_path_option()
@clean_option()
# this is kinda a odd one:
# - <nothing> = empty tuple
# - --link = ("auto")
# - --link auto = ("auto")
# - --link mainline = ("mainline")
# - --link mainline --link tbc = ("mainline", "tbc")
# - --link mainline --link auto = ("mainline", "auto") (raises an exception)
@click.option(
    "-l",
    "--link",
    "flavors_to_link",
    type=click.Choice([AUTO_CHOICE, *FLAVOR_NAMES], case_sensitive=False),
    multiple=True,
    is_flag=False,
    flag_value=AUTO_CHOICE,
    help=(
        "Create a symlink from packaged addon folder into the WoW AddOns folder. This "
        "is handy for installing your own stuff, so you can work on it and test it "
        "iteratively without having to continually recopy it into the AddOns folder. "
        "You can specify a flavor to this option to symlink just a particular flavor"
        "(that must also be in the wowVersions section of your config). You may also "
        "specify no value, in which case links will be made for all configured flavors "
        "that exist on this system. "
        "The path of the AddOns folder is a default for your operating system, but may "
        "be overriden by specifying any of the --<flavor>-addons-path options."
    ),
    show_default=True,
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
    output_path: Path,
    clean: bool,
    flavors_to_link: Sequence[FlavorName | AutoChoiceName],
    enable_watch: bool,
    mainline_addons_path: Path,
    wrath_addons_path: Path,
    vanilla_addons_path: Path,
) -> None:
    """
    Build addons into a package

    Addons inside the package directory will have ToC files generated if configured.
    Additionally, any files in the "include" field of an addon's configuration will be
    copied into the addon directories.

    The name of the directory will be in the format of "<package-name>-<version>", such
    as "MyAddon-1.2.3".
    """
    config_path = config_path.resolve()

    def build_once() -> Package:
        config = Config.from_path(config_path)
        package = Package.create(
            config=config, config_path=config_path, output_path=output_path
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
            info(f"Built {addon.path.name} in " f"{addon.path.parent}")

            for addon_dir in addon_link_dirs:
                link_path = addon.link(wow_addons_path=addon_dir)
                if link_path:
                    info(f"Linked {link_path} to {addon.path}")

        return package

    package = build_once()

    if enable_watch:
        info("Running in watch mode. Press Ctrl-C at any time to quit.")
        project_file_paths = {*package.watch_paths, config_path}
        for paths_changed in watch_paths(config_path.parent):
            if any(
                changed_path.is_relative_to(watch_path)
                for watch_path in project_file_paths
                for changed_path in paths_changed
            ):
                info("Project file changed, rebuilding...")
                package = build_once()
                project_file_paths = {*package.watch_paths, config_path}


def watch_paths(*paths: Path) -> Iterator[Iterable[Path]]:
    for changes in watch(*paths):
        yield {Path(path) for _, path in changes}