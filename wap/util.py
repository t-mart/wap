import shutil
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
        # it could be a pipe or socket or some other non-file thing.
        raise ValueError(
            f"Cannot delete path {path} because it is not a file or directory"
        )
