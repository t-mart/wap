from pathlib import Path

FIXTURE_ROOT = Path(__file__).parent
CONFIGS_ROOT = FIXTURE_ROOT / "configs"
PROJECT_DIRS_ROOT = FIXTURE_ROOT / "project_dirs"
# WOW_DIRS_ROOT = FIXTURE_ROOT / "wow_dirs"

WOW_DIRS = {
    "classic": Path("/World of Warcraft/_classic_/Interface/AddOns"),
    "retail": Path("/World of Warcraft/_retail_/Interface/AddOns"),
    "bad_addons_part": Path("/World of Warcraft/_retail_/Interface/AddOffs"),
    "bad_interface_part": Path("/World of Warcraft/_retail_/Interfaces/AddOns"),
    "bad_type_part": Path("/World of Warcraft/_neither_/Interface/AddOns"),
    "bad_wow_part": Path("/Planet of Warcraft/_retail_/Interface/AddOns"),
    "too_short": Path("/World of Warcraft/"),
}


def config_file_path(name: str) -> Path:
    path = CONFIGS_ROOT / (name + ".yml")
    if not path.is_file():
        raise ValueError(f"Config path {path} is not a file")
    return path


def project_dir_path(name: str) -> Path:
    path = PROJECT_DIRS_ROOT / name
    if not path.is_dir():
        raise ValueError(f"Project path {path} is not a directory")
    return path


def wow_dir_path(name: str) -> Path:
    try:
        return WOW_DIRS[name]
    except KeyError:
        raise ValueError(f"WoW path {name} does not exist")
