import shutil
import sys
from pathlib import Path

DEFAULT_WIN32_WOW_ADDONS_PATH = (
    R"C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"
)
DEFAULT_DARWIN_WOW_ADDONS_PATH = (
    "/Applications/World of Warcraft/_retail_/Interface/AddOns"
)


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

    # don't measure code coverage here because the testing system is only one platform
    # TODO: write unit test that mocks out sys.platform?
    if platform == "win32":  # pragma: no cover
        return DEFAULT_WIN32_WOW_ADDONS_PATH
    elif platform == "darwin":  # pragma: no cover
        return DEFAULT_DARWIN_WOW_ADDONS_PATH
    else:  # pragma: no cover
        return "</path/to/WoW/Interface/AddOns>"
