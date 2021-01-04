import shutil
from collections import OrderedDict
from typing import Any, Callable

import pytest
import strictyaml

from tests.fixtures import (
    PackageEnv,
    capsys_err,
    package_env,
    ref_config,
    ref_config_obj,
)
from wap.config import PackageConfig, WowVersionConfig
from wap.exception import (
    ConfigFileException,
    ConfigSchemaException,
    ConfigSemanticException,
)


def config_obj_to_yaml(obj: Any) -> str:
    return strictyaml.as_document(obj).as_yaml()  # type: ignore


def test_package_config_normal(
    ref_config_obj: OrderedDict[str, Any], ref_config: PackageConfig
) -> None:
    yml = config_obj_to_yaml(ref_config_obj)

    config = PackageConfig.from_yaml(yml)

    assert config == ref_config


def test_package_config_missing_name(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["name"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_package_config_missing_wow_version_configs(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["wow-versions"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_package_config_optional_curseforge_config(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["curseforge"]
    yml = config_obj_to_yaml(ref_config_obj)

    PackageConfig.from_yaml(yml)


def test_package_config_missing_dir_configs(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["dirs"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_package_config_duplicate_version_types(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    ref_config_obj["wow-versions"].append(
        OrderedDict([("version", "8.3.6"), ("type", "retail")])
    )
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)


def test_package_config_wow_version_by_type(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    yml = config_obj_to_yaml(ref_config_obj)

    pc = PackageConfig.from_yaml(yml)

    assert pc.wow_version_by_type("retail") == WowVersionConfig(
        version="9.0.2", type_="retail"
    )
    assert pc.wow_version_by_type("classic") == WowVersionConfig(
        version="1.13.6", type_="classic"
    )
    with pytest.raises(ValueError):
        pc.wow_version_by_type("not a type")


def test_package_config_from_path(package_env: PackageEnv) -> None:
    pc = PackageConfig.from_path(package_env.config_path)


def test_package_config_from_path_does_not_exist(package_env: PackageEnv) -> None:

    with pytest.raises(ConfigFileException):
        pc = PackageConfig.from_path(
            package_env.config_path.parent / "does" / "not" / "exist.yml"
        )


def test_package_config_from_path_no_yml_extension(
    package_env: PackageEnv,
    capsys_err: Callable[[], str],
) -> None:

    new_config_path = package_env.config_path.with_suffix("")
    shutil.move(src=package_env.config_path, dst=new_config_path)

    pc = PackageConfig.from_path(new_config_path)

    assert "without YAML extension" in capsys_err()
    assert "extension" in capsys_err()


def test_curseforge_config_missing_project_id(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["curseforge"]["project-id"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_curseforge_config_missing_changelog(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["curseforge"]["changelog"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_curseforge_config_changelog_not_relative(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    ref_config_obj["curseforge"]["changelog"] = "/foo.md"
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)


def test_dir_config_missing_path(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["dirs"][0]["path"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_dir_config_path_not_relative(ref_config_obj: OrderedDict[str, Any]) -> None:
    ref_config_obj["dirs"][0]["path"] = "/Foo"
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)


def test_dir_config_optional_toc_config(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["dirs"][0]["toc"]
    yml = config_obj_to_yaml(ref_config_obj)

    PackageConfig.from_yaml(yml)


def test_wow_version_config_missing_type(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["wow-versions"][0]["type"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_wow_version_config_bad_type(ref_config_obj: OrderedDict[str, Any]) -> None:
    ref_config_obj["wow-versions"][0]["type"] = "neither classic nor retail"
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)


def test_wow_version_config_missing_version(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    del ref_config_obj["wow-versions"][0]["version"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_wow_version_config_bad_version(ref_config_obj: OrderedDict[str, Any]) -> None:
    ref_config_obj["wow-versions"][0]["version"] = "not.a.version"
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)


def test_wow_version_config_interface_version(
    ref_config_obj: OrderedDict[str, Any]
) -> None:
    yml = config_obj_to_yaml(ref_config_obj)

    pc = PackageConfig.from_yaml(yml)

    assert pc.wow_version_configs[0].interface_version() == "90002"
    assert pc.wow_version_configs[1].interface_version() == "11306"


def test_toc_config_missing_tags(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["dirs"][0]["toc"]["tags"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_toc_config_missing_files(ref_config_obj: OrderedDict[str, Any]) -> None:
    del ref_config_obj["dirs"][0]["toc"]["tags"]
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSchemaException):
        PackageConfig.from_yaml(yml)


def test_toc_config_path_not_relative(ref_config_obj: OrderedDict[str, Any]) -> None:
    ref_config_obj["dirs"][0]["toc"]["files"][0] = "/foo.lua"
    yml = config_obj_to_yaml(ref_config_obj)

    with pytest.raises(ConfigSemanticException):
        PackageConfig.from_yaml(yml)
