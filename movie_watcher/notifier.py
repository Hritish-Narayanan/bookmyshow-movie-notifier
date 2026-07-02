"""ntfy notification client."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from urllib.parse import urlparse
from typing import Iterable

import requests


@dataclass(frozen=True, slots=True)
class Notification:
    title: str
    body: str
    tags: str = "movie,alert"
    priority: str = "4"
    click: str = ""


def _title_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    parts = [part for part in path.split("/") if part]
    slug = ""
    if "buytickets" in parts:
        index = parts.index("buytickets")
        if index > 0:
            slug = parts[index - 1]
    elif parts:
        slug = parts[-1]
    words = [part for part in slug.replace("-", " ").split() if part]
    return " ".join(word.capitalize() for word in words) if words else "Movie Theatre Update"


def format_notification(theatres: Iterable[str], *, click_url: str, title: str | None = None) -> Notification:
    items = list(theatres)
    prefix = "New theatre added!" if len(items) == 1 else "New theatres added!"
    body = "\n".join([prefix, *[f"🏢 {item}" for item in items]])
    return Notification(
        title=title or _title_from_url(click_url),
        body=body,
        tags="movie,cinema,alert",
        priority="4",
        click=click_url,
    )


def send_notification(
    ntfy_url: str,
    notification: Notification,
    logger: logging.Logger,
    dry_run: bool = False,
) -> bool:
    if dry_run:
        logger.info("DRY RUN notification title=%s body=%s", notification.title, notification.body)
        print(notification.title)
        print(notification.body)
        return True

    headers = {
        "Title": notification.title,
        "Priority": notification.priority,
        "Tags": notification.tags,
        "Click": notification.click,
    }
    response = requests.post(ntfy_url, data=notification.body.encode("utf-8"), headers=headers, timeout=30)
    response.raise_for_status()
    logger.info("Notification sent")
    return True
