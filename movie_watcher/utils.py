"""Utility helpers."""

from __future__ import annotations

import logging
import random
import re
from typing import Iterable


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_theatre_name(name: str) -> str:
    cleaned = _WHITESPACE_RE.sub(" ", name).strip()
    cleaned = cleaned.replace(" - ", " ")
    return cleaned.casefold()


def dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = normalize_theatre_name(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result


def format_duration(seconds: int) -> str:
    minutes, remaining_seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if remaining_seconds and not hours:
        parts.append(f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}")
    return " ".join(parts) if parts else "0 seconds"


def pick_random_interval(min_seconds: int, max_seconds: int) -> int:
    if min_seconds > max_seconds:
        raise ValueError("min_seconds must be <= max_seconds")
    return random.randint(min_seconds, max_seconds)

def setup_logger(log_level: str) -> logging.Logger:
    logger = logging.getLogger("movie_watcher")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    return logger
