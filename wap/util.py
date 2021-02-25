import shutil
import sys
from pathlib import Path


def delete_path(path: Path) -> None:
    """
    Deletes either a file or directory. The path existance must be checked before
    calling this function.
    """
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:  # pragma: no cover
        # don't measure code coverage here because it's a really esoteric case:
        # it could be a pipe, link, socket or some other non-file thing.
        raise ValueError(
            f"Cannot delete path {path} because it is not a file or directory"
        )


def default_wow_addons_path_for_system() -> str:
    # this function is for documentation purposes only! we will not start assuming
    # where a user's addons path.
    platform = sys.platform

    # don't measure code coverage here because the testing system will only
    if platform == "win32":  # pragma: no cover
        return R"C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"
    elif platform == "darwin":  # pragma: no cover
        return "/Applications/World of Warcraft/_retail_/Interface/AddOns"
    else:  # pragma: no cover
        return "</path/to/WoW/Interface/AddOns>"
