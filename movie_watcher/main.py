"""CLI entry point."""

from __future__ import annotations

import argparse

from .config import load_config
from .notifier import format_notification, send_notification
from .utils import setup_logger
from .watcher import check_once, run


def cli() -> int:
    parser = argparse.ArgumentParser(prog="bookmyshow-movie-notifier")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-notify", action="store_true")
    args = parser.parse_args()

    config = load_config()
    config.log_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(config.log_level)

    if args.force_notify:
        try:
            notification = format_notification(
                ["Test Theatre"],
                click_url=config.bookmyshow_url,
            )
            send_notification(config.ntfy_url, notification, logger, dry_run=False)
            return 0
        except Exception:
            logger.exception("Force notification failed")
            return 1

    if args.dry_run:
        try:
            check_once(config, logger, dry_run=True)
        except Exception:
            logger.exception("Dry run failed")
        return 0

    return run(config, logger, dry_run=False)
