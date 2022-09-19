from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from zipfile import ZIP_DEFLATED, ZipFile

from wap.config import Config


def zip_addon(package_path: Path) -> BinaryIO:
    # TODO: just use https://docs.python.org/3/library/shutil.html#shutil.make_archive
    # instead of all this
    stream = BytesIO()

    with ZipFile(stream, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for path in package_path.rglob("*"):
            zip_file.write(
                filename=path,
                arcname=path.relative_to(package_path),
            )

    return stream


def get_build_path(output_path: Path, config: Config) -> Path:
    return output_path / f"{config.name}-{config.version}"
