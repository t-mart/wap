from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable

import attr
import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from wap.addonspath import WoWAddonsPath
from wap.config import (
    CurseforgeConfig,
    DirConfig,
    PackageConfig,
    TocConfig,
    WowVersionConfig,
)

# The following fixtures are COUPLED and represent the same data:
#   - ref_config_obj
#     Provides an unschema-ed way to add/delete objects from a config
#   - ref_config
#     A built WAP configuration object
#   - ref_config_yml
#     Text of a yaml
# A convenience because these objects are so complex. While you can derive these
# objects from each other, it's essential for testing that their different
# representations are separated so that we can be sure that WAP can convert them
# between them properly


@pytest.fixture
def ref_config_obj() -> OrderedDict[str, Any]:
    """
    Turn this into a yaml string with `strictyaml.as_document(obj).as_yaml()`
    """
    return OrderedDict(
        [
            ("name", "MoneyPrinter"),
            (
                "wow-versions",
                [
                    OrderedDict([("version", "9.0.2"), ("type", "retail")]),
                    OrderedDict([("version", "1.13.6"), ("type", "classic")]),
                ],
            ),
            (
                "curseforge",
                OrderedDict(
                    [
                        ("project-id", "441390"),
                        ("changelog", "CHANGELOG.md"),
                        ("addon-name", "moneyprinter"),
                    ]
                ),
            ),
            (
                "dirs",
                [
                    OrderedDict(
                        [
                            ("path", "MoneyPrinter"),
                            (
                                "toc",
                                OrderedDict(
                                    [
                                        (
                                            "tags",
                                            OrderedDict(
                                                [
                                                    ("Title", "MoneyPrinter"),
                                                    ("Notes", "Prints your money"),
                                                    ("DefaultState", "Enabled"),
                                                    ("LoadOnDemand", "0"),
                                                    ("Author", "Tim Martin"),
                                                ]
                                            ),
                                        ),
                                        ("files", ["Core.lua"]),
                                    ]
                                ),
                            ),
                        ]
                    ),
                    OrderedDict(
                        [
                            ("path", "LibMoneyPrinter"),
                            (
                                "toc",
                                OrderedDict(
                                    [
                                        (
                                            "tags",
                                            OrderedDict(
                                                [
                                                    ("Title", "LibMoneyPrinter"),
                                                    (
                                                        "Notes",
                                                        "Library for MoneyPrinter",
                                                    ),
                                                    ("DefaultState", "Enabled"),
                                                    ("LoadOnDemand", "0"),
                                                ]
                                            ),
                                        ),
                                        ("files", ["API.lua"]),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ],
            ),
        ]
    )


@pytest.fixture
def ref_config_yml() -> str:
    return """name: MoneyPrinter
wow-versions:
  - version: 9.0.2
    type: retail
  - version: 1.13.6
    type: classic
curseforge:
  project-id: 441390
  changelog: CHANGELOG.md
  addon-name: moneyprinter
dirs:
  - path: MoneyPrinter
    toc:
      tags:
        Title: MoneyPrinter
        Notes: Prints your money
        DefaultState: Enabled
        LoadOnDemand: 0
        Author: Tim Martin
      files:
        - Core.lua
  - path: LibMoneyPrinter
    toc:
      tags:
        Title: LibMoneyPrinter
        Notes: Library for MoneyPrinter
        DefaultState: Enabled
        LoadOnDemand: 0
      files:
        - API.lua
"""


@pytest.fixture
def ref_config(fs: FakeFilesystem) -> PackageConfig:
    return PackageConfig(
        name="MoneyPrinter",
        wow_version_configs=[
            WowVersionConfig(version="9.0.2", type_="retail"),
            WowVersionConfig(version="1.13.6", type_="classic"),
        ],
        curseforge_config=CurseforgeConfig(
            project_id="441390",
            changelog_path=Path("CHANGELOG.md"),
            addon_name="moneyprinter",
        ),
        dir_configs=[
            DirConfig(
                path=Path("MoneyPrinter"),
                toc_config=TocConfig(
                    tags={
                        "Title": "MoneyPrinter",
                        "Notes": "Prints your money",
                        "DefaultState": "Enabled",
                        "LoadOnDemand": "0",
                        "Author": "Tim Martin",
                    },
                    files=[
                        Path("Core.lua"),
                    ],
                ),
            ),
            DirConfig(
                path=Path("LibMoneyPrinter"),
                toc_config=TocConfig(
                    tags={
                        "Title": "LibMoneyPrinter",
                        "Notes": "Library for MoneyPrinter",
                        "DefaultState": "Enabled",
                        "LoadOnDemand": "0",
                    },
                    files=[
                        Path("API.lua"),
                    ],
                ),
            ),
        ],
    )


@pytest.fixture
def ref_config_real_path() -> PackageConfig:
    # yeesh. this needs to be different than ref_config() because including
    # the fs fixture (a FakeFilesystem from pyfakefs) will cause different Path objects
    # to be created. These Path objects fail isinstance(the_path, Path) checks
    return PackageConfig(
        name="MoneyPrinter",
        wow_version_configs=[
            WowVersionConfig(version="9.0.2", type_="retail"),
            WowVersionConfig(version="1.13.6", type_="classic"),
        ],
        curseforge_config=CurseforgeConfig(
            project_id="441390",
            changelog_path=Path("CHANGELOG.md"),
            addon_name="moneyprinter",
        ),
        dir_configs=[
            DirConfig(
                path=Path("MoneyPrinter"),
                toc_config=TocConfig(
                    tags={
                        "Title": "MoneyPrinter",
                        "Notes": "Prints your money",
                        "DefaultState": "Enabled",
                        "LoadOnDemand": "0",
                        "Author": "Tim Martin",
                    },
                    files=[
                        Path("Core.lua"),
                    ],
                ),
            ),
            DirConfig(
                path=Path("LibMoneyPrinter"),
                toc_config=TocConfig(
                    tags={
                        "Title": "LibMoneyPrinter",
                        "Notes": "Library for MoneyPrinter",
                        "DefaultState": "Enabled",
                        "LoadOnDemand": "0",
                    },
                    files=[
                        Path("API.lua"),
                    ],
                ),
            ),
        ],
    )


@attr.s(kw_only=True, frozen=True, auto_attribs=True, order=True)
class PackageEnv:
    fs: FakeFilesystem
    addon_root_path: Path
    config: PackageConfig
    config_path: Path
    output_path: Path


_ADDON_FIXTURE_PATH = Path(__file__).parent / "test_addon"


@pytest.fixture
def package_env(fs: FakeFilesystem) -> FakeFilesystem:
    addon_root_path = Path("/MoneyPrinter")
    config_path = addon_root_path / ".wap.yml"
    fs.add_real_directory(_ADDON_FIXTURE_PATH, target_path=addon_root_path)
    config = PackageConfig.from_path(config_path)
    output_path = Path("/dist")
    return PackageEnv(
        fs=fs,
        addon_root_path=addon_root_path,
        config=config,
        config_path=config_path,
        output_path=output_path,
    )


@pytest.fixture
def retail_wow_addons_path(fs: FakeFilesystem) -> WoWAddonsPath:
    path = Path("/") / "World of Warcraft" / "_retail_" / "Interface" / "AddOns"
    fs.create_dir(path)
    return WoWAddonsPath(path=path)


@pytest.fixture
def classic_wow_addons_path(fs: FakeFilesystem) -> WoWAddonsPath:
    path = Path("/") / "World of Warcraft" / "_classic_" / "Interface" / "AddOns"
    fs.create_dir(path)
    return WoWAddonsPath(path=path)


@pytest.fixture
def wow_addons_path_parameterized(  # type: ignore
    request,
    classic_wow_addons_path: WoWAddonsPath,
    retail_wow_addons_path: WoWAddonsPath,
) -> WoWAddonsPath:
    # per the type of the `request` argument, it's _pytest.fixtures.SubRequest. note
    # that that's in the private pytest API, so we can't access it safely. Open PR to
    # fix this at https://github.com/pytest-dev/pytest/pull/6717
    if request.param == "retail":
        return retail_wow_addons_path
    return classic_wow_addons_path


@pytest.fixture
def capsys_err(capsys: pytest.CaptureFixture[str]) -> Callable[[], str]:
    """
    Convenience method for getting capsys's error output. Call this fixture to get the
    output. Repeated calls return the same output.
    """
    read = None

    def wrapped() -> str:
        nonlocal read
        if read is None:
            read = capsys.readouterr().err
        return read

    return wrapped
