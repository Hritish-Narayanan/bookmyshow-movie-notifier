"""Configuration loading for BookMyShow Movie Notifier."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


@dataclass(frozen=True, slots=True)
class Config:
    bookmyshow_url: str
    check_interval_min: int
    check_interval_max: int
    headless: bool
    ntfy_url: str
    log_level: str
    state_file: Path
    log_dir: Path


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_config() -> Config:
    load_dotenv()
    state_file = PROJECT_ROOT / "theatres.json"
    log_dir = PROJECT_ROOT / "logs"
    default_url = "https://in.bookmyshow.com/movies/chennai/spider-man-brand-new-day-epiq-3d/buytickets/ET00505581/20260730"
    bookmyshow_url = os.getenv("BOOKMYSHOW_URL", default_url).strip()
    if not bookmyshow_url:
        bookmyshow_url = default_url
    check_interval_min = _get_int("CHECK_INTERVAL_MIN", 60)
    check_interval_max = _get_int("CHECK_INTERVAL_MAX", check_interval_min)
    if check_interval_max < check_interval_min:
        check_interval_max = check_interval_min
    return Config(
        bookmyshow_url=bookmyshow_url,
        check_interval_min=check_interval_min,
        check_interval_max=check_interval_max,
        headless=_get_bool("HEADLESS", False),
        ntfy_url=os.getenv("NTFY_URL", "https://ntfy.sh/movie"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        state_file=state_file,
        log_dir=log_dir,
    )
