"""BookMyShow watcher and comparison logic."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .config import Config
from .notifier import format_notification, send_notification
from .parser import extract_theatre_names_from_text, extract_theatre_names_from_entries
from .storage import load_theatres, save_theatres
from .utils import format_duration, normalize_theatre_name, pick_random_interval


@dataclass(slots=True)
class TheatreChange:
    current: list[str]
    previous: list[str]
    added: list[str]
    removed: list[str]


def compare_theatres(current: list[str], previous: list[str]) -> TheatreChange:
    current_names = extract_theatre_names_from_entries(current)
    previous_names = extract_theatre_names_from_entries(previous)
    current_keys = {normalize_theatre_name(name): name for name in current_names}
    previous_keys = {normalize_theatre_name(name): name for name in previous_names}
    added = [name for key, name in current_keys.items() if key not in previous_keys]
    removed = [name for key, name in previous_keys.items() if key not in current_keys]
    return TheatreChange(current=current_names, previous=previous_names, added=added, removed=removed)


def _wait_random_delay() -> None:
    import time

    time.sleep(2)


def fetch_theatres(config: Config, logger: logging.Logger) -> list[str]:
    logger.info("Opening BookMyShow")
    if not config.bookmyshow_url:
        raise RuntimeError("BOOKMYSHOW_URL is not configured")
    logger.info("Navigating to %s", config.bookmyshow_url)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=config.headless)
        page = browser.new_page()
        try:
            _wait_random_delay()
            logger.info("Waiting for theatres")
            page.goto(config.bookmyshow_url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_load_state("networkidle", timeout=120000)
            title = page.title()
            if "attention required" in title.casefold():
                raise RuntimeError("BookMyShow blocked by Cloudflare")
            html = page.content()
            theatres = extract_theatre_names_from_text(html)
            if not theatres:
                theatres = extract_theatre_names_from_text(page.locator("body").inner_text())
            if not theatres:
                theatres = _fetch_from_performance_entries(page)
            logger.info("%d theatres found", len(theatres))
            if not theatres:
                raise RuntimeError("No theatres extracted from page content")
            return theatres
        finally:
            browser.close()


def _fetch_from_performance_entries(page) -> list[str]:
    entries = page.evaluate(
        """() => performance.getEntriesByType('resource').map(entry => entry.name)"""
    )
    extracted: list[str] = []
    for entry in entries or []:
        if "api" in entry.lower() or "movie" in entry.lower():
            extracted.extend(extract_theatre_names_from_text(str(entry)))
    return extracted


def check_once(
    config: Config,
    logger: logging.Logger,
    dry_run: bool = False,
    fetcher: Callable[[Config, logging.Logger], list[str]] = fetch_theatres,
) -> TheatreChange:
    previous = load_theatres(config.state_file)
    current = fetcher(config, logger)
    change = compare_theatres(current, previous)
    if change.added:
        logger.info("%d new theatres detected", len(change.added))
        notification = format_notification(change.added, click_url=config.bookmyshow_url)
        send_notification(config.ntfy_url, notification, logger, dry_run=dry_run)
    else:
        logger.info("No changes detected")
    save_theatres(config.state_file, current)
    return change


def run(config: Config, logger: logging.Logger, dry_run: bool = False) -> int:
    logger.info("Application started")
    while True:
        try:
            change = check_once(config, logger, dry_run=dry_run)
            delay = pick_random_interval(config.check_interval_min, config.check_interval_max)
            logger.info("Next check in %s.", format_duration(delay))
            import time

            time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Shutting down")
            return 0
        except PlaywrightTimeoutError as exc:
            logger.exception("Playwright timeout: %s", exc)
        except Exception:
            logger.exception("Unexpected exception")
            import time

            time.sleep(10)
