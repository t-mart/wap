from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Generator, Iterable

import arrow
import attr
import click

from wap import log
from wap.config import Config


@attr.s(kw_only=True, frozen=True, auto_attribs=True, order=False)
class FileState:
    path: Path
    mtime: float

    @classmethod
    def from_path(cls, path: Path) -> FileState:
        return cls(path=path, mtime=path.stat().st_mtime)


def _get_project_state(config_path: Path) -> set[FileState]:
    config = Config.from_path(path=config_path)

    file_states = set()

    file_states.add(FileState.from_path(config_path))

    for addon_config in config.addon_configs:
        addon_path = config_path.parent / addon_config.path
        if addon_path.exists():
            file_states.update(_get_dir_stats(addon_path))
        # if it does not exist, it will be caught be wap package

    return file_states


def _get_dir_stats(path: Path) -> Iterable[FileState]:
    for entry in os.scandir(path):
        if entry.is_dir():
            yield from _get_dir_stats(Path(entry.path))
        else:
            yield FileState.from_path(Path(entry.path))


async def _poll_for_change(
    config_path: Path,
    last_state: set[FileState],
) -> set[FileState]:
    while True:
        new_state = _get_project_state(config_path)
        if new_state != last_state:
            return new_state

        await asyncio.sleep(0.1)


def watch_project(config_path: Path) -> Generator[set[FileState], None, None]:
    is_first_iter = True
    last_state: set[FileState] = set()

    log.info(
        "Starting filesystem watcher. Press "
        + click.style("Ctrl-C", fg="red")
        + " at any time to stop.\n"
    )

    while True:
        new_state = asyncio.run(
            _poll_for_change(config_path=config_path, last_state=last_state)
        )

        if new_state != last_state:
            time_str = arrow.now().isoformat()
            if is_first_iter:
                log.info(f"{time_str} - Running initial package and install...\n")
                is_first_iter = False
            else:
                log.info(
                    f"{time_str} - Changes detected. Repackaging and installing...\n"
                )

            diff = new_state - last_state
            last_state = new_state
            yield diff
