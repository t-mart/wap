from pathlib import Path

from wap.config import Config


def get_build_path(output_path: Path, config: Config) -> Path:
    return output_path / f"{config.name}-{config.version}"
