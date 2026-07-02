"""Verification mode for notification flow."""

from __future__ import annotations

import argparse

from .config import load_config
from .notifier import format_notification, send_notification
from .storage import backup_file, restore_file, load_theatres, save_theatres
from .utils import setup_logger
from .watcher import compare_theatres


def _build_sample_theatre(name: str, theatre_id: str) -> dict[str, object]:
    return {
        "venueName": name,
        "theatreId": theatre_id,
        "city": "Chennai",
        "format": "2D",
        "showtimes": ["10:00 AM", "1:30 PM", "7:00 PM"],
    }


def cli() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()

    config = load_config()
    logger = setup_logger(config.log_level)
    original = backup_file(config.state_file)
    try:
        current = load_theatres(config.state_file)
        structured_current = current if current and isinstance(current[0], dict) else [
            _build_sample_theatre(str(name), f"sample-{index + 1}")
            for index, name in enumerate(current)
        ]
        injected = (
            structured_current[:-1]
            if args.remove and structured_current
            else structured_current
            + [
                _build_sample_theatre("Fake Theatre Alpha", "fake-alpha"),
                _build_sample_theatre("Fake Theatre Beta", "fake-beta"),
            ]
        )
        save_theatres(config.state_file, injected)
        change = compare_theatres(injected, current)
        if not change.added and not change.removed:
            logger.info("No changes found in test mode")
        items = change.removed if args.remove else change.added
        if items:
            notification = format_notification(items, click_url=config.bookmyshow_url)
            send_notification(config.ntfy_url, notification, logger, dry_run=False)
        else:
            logger.info("Skipping notification because there are no theatre changes")
        return 0
    finally:
        restore_file(config.state_file, original)
