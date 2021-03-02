# mypy: allow-subclassing-any

from __future__ import annotations

import queue
import threading
import time
from functools import partial
from pathlib import Path

import arrow
import attr
import click
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from wap import log
from wap.commands.common import (
    config_path_option,
    version_option,
    wow_addons_path_option,
)
from wap.commands.dev_install import dev_install
from wap.commands.package import package
from wap.config import Config
from wap.exception import WAPException


@attr.s(kw_only=True, order=False, frozen=True, auto_attribs=True)
class TimedEvent:
    event: FileSystemEvent
    time_triggered: arrow.Arrow


@attr.s(kw_only=True, order=False, frozen=True, auto_attribs=True)
class WapWatcher(FileSystemEventHandler):
    event_queue: queue.Queue[TimedEvent]

    def on_any_event(self, event: FileSystemEvent) -> None:
        self.event_queue.put(TimedEvent(event=event, time_triggered=arrow.now()))


def do_package_and_dev_install(
    ctx: click.Context,
    config_path: Path,
    version: str,
    wow_addons_path: Path,
) -> None:
    try:
        ctx.invoke(
            package,
            config_path=config_path,
            version=version,
        )
        ctx.invoke(
            dev_install,
            config_path=config_path,
            version=version,
            wow_addons_path=wow_addons_path,
        )
        log.info("")
    except WAPException as we:
        log.error(we.message + "\n")


def event_worker(
    queue: queue.Queue[TimedEvent],
    ctx: click.Context,
    config_path: Path,
    version: str,
    wow_addons_path: Path,
) -> None:
    log.info("Performing initial package and dev-install...\n")
    do_package_and_dev_install(
        ctx=ctx,
        config_path=config_path,
        version=version,
        wow_addons_path=wow_addons_path,
    )
    last_run_end = arrow.utcnow()

    while True:
        timed_event = queue.get()

        if timed_event.time_triggered < last_run_end.shift(seconds=+1):
            queue.task_done()
            continue

        do_package_and_dev_install(
            ctx=ctx,
            config_path=config_path,
            version=version,
            wow_addons_path=wow_addons_path,
        )
        last_run_end = arrow.utcnow()

        queue.task_done()

        time.sleep(1)


@click.command()
@config_path_option()
@version_option(help="The version you want to assign your package.")
@wow_addons_path_option()
@click.pass_context
def watch(
    ctx: click.Context,
    config_path: Path,
    version: str,
    wow_addons_path: Path,
) -> None:
    """
    Monitor for any changes in your project and automatically package and install
    to your WoW AddOns directory.

    This command is a composite of the package and dev-install commands, along with
    a filesystem event watcher on your config file and addon paths. When an event
    is emitted from your filesytem, your addon will be package and dev-install will run.

    This speeds up the developer feedback-loop, so you don't have to type
    any further wap commands while you develop on your addons.
    """
    config = Config.from_path(config_path)
    event_queue: queue.Queue[TimedEvent] = queue.LifoQueue()

    watcher = WapWatcher(event_queue=event_queue)

    observer = Observer()
    observer.setName("wap_watch_observer")

    log.info(
        "Starting filesystem watcher. Press "
        + click.style("Ctrl-C", fg="red")
        + " at any time to stop."
    )

    # watch the config file and the addon directories
    observer.schedule(watcher, config_path)
    log.info("Watching " + click.style(f"{config_path}", fg="green"))
    for addon_config in config.addon_configs:
        addon_path = config_path.parent / addon_config.path
        if addon_path.is_dir():
            observer.schedule(watcher, addon_path, recursive=True)
            log.info("Watching " + click.style(f"{addon_path}", fg="green"))

    worker_partial = partial(
        event_worker,
        queue=event_queue,
        ctx=ctx,
        config_path=config_path,
        version=version,
        wow_addons_path=wow_addons_path,
    )
    threading.Thread(
        target=worker_partial, daemon=True, name="wap_watch_event_worker"
    ).start()

    observer.start()

    try:
        while True:
            time.sleep(0.1)
    finally:
        observer.stop()
        observer.join()
