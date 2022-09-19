import shutil
from pathlib import Path

from wap.exception import (
    PathExistsException,
    PathMissingException,
    PathTypeException,
    PlatformException,
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
        raise PathTypeException(
            f"Cannot delete path {path} because it is not a file or directory"
        )


def clean_dir(path: Path) -> None:
    """
    Deletes all files and subdirectories in a given directory, but does not delete the
    directory itself.
    """
    for subpath in path.iterdir():
        delete_path(subpath)


def copy_path(src: Path, dst: Path) -> None:
    """
    If src is a file: If dst does not exist, copy src to dst. If dst is a file,
    overwrite its contents with those of src. If dst is a directory, raise a
    PathExistsException.

    If src is a directory: If dst does not exist, create a new directory dst and copy
    src's tree to it. If dst is a directory, copy src's tree to it (without cleaning).
    If dst is a file, raise a PathExistsException.

    | src type | dest type |    outcome    |
    |:--------:|:---------:|:-------------:|
    |     F    |     F     |   overwrite   |
    |     F    |     D     |  exists error |
    |     F    | not exist |    new file   |
    |     D    |     F     |   perm error  |
    |     D    |     D     | copy contents |
    |     D    | not exist |    new dir    |

    And finally, if src and dst are not directories or files, raise a PathTypeException.
    """
    if src.is_file():
        if dst.is_dir():
            raise PathExistsException(
                f"Cannot copy file {src} to {dst} because it is a directory"
            )
        shutil.copy(src, dst)
    elif src.is_dir():
        if dst.is_file():
            raise PathExistsException(
                f"Cannot copy directory {src} to {dst} because it is a file"
            )
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:  # pragma: no cover
        raise PathTypeException(
            f"Cannot copy path {src} because it is not a file or directory"
        )


def symlink(
    *, new_path: Path, target_path: Path, target_is_directory: bool | None = None
) -> None:
    """
    Make new_path a symbolic (soft) link that targets target_path.

    On Windows, *target_is_directory* must be set to True if target is a directory. If
    the argument is None (the default), it will take the value of
    `target_path.is_dir()`.

    Additionally on Windows, if a certain type of OSError is raised that indicates
    insufficient privileges, this function instead raises a new OSError (`from` the
    original) with a more helpful message about disabling the privilege requirement'
    for newer versions of Windows 10.
    """
    if target_is_directory is None:
        target_is_directory = target_path.is_dir()

    # FileExistsError and FileNotFoundError are subclasses of OSError, all three of
    # which we catch, so the ordering is important.
    # additionally, target_is_directory is only important in specific Windows cases, but
    # is ignored otherwise, so we provide it anyway.
    try:
        new_path.symlink_to(
            target_path.resolve(), target_is_directory=target_is_directory
        )
    except FileExistsError as file_exists_error:
        if target_path.resolve() == new_path.resolve():
            return
        raise PathExistsException(
            f"Intended symlink {new_path} already exists."
        ) from file_exists_error
    except FileNotFoundError as file_not_found_error:
        raise PathMissingException(
            f"Unable to create link {new_path}. Does its parent directory exist?"
        ) from file_not_found_error
    except OSError as os_error:
        if getattr(os_error, "winerror", None) == 1314:
            raise PlatformException(
                f"Could not create symbolic link from {new_path} to {target_path} "
                "which requires requires elevation as administrator on Windows. "
                "However, Windows 10 (build 14972 or newer) with Developer Mode "
                "enabled no longer requires elevation."
            ) from os_error
        raise os_error
