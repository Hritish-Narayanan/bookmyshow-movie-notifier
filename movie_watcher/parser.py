"""Parse theatre lists from HTML or structured data."""

from __future__ import annotations

import json
import re
from typing import Iterable

from .utils import dedupe_preserve_order


THEATRE_PATTERNS = [
    re.compile(r'"venueName"\s*:\s*"([^"]+)"'),
    re.compile(r'"name"\s*:\s*"([^"]+)"'),
    re.compile(r'data-name="([^"]+)"'),
]


def _normalize_candidate(text: str) -> str:
    return " ".join(text.split()).strip()


def extract_theatre_names_from_text(text: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for pattern in THEATRE_PATTERNS:
        matches.extend((match.start(), match.group(1)) for match in pattern.finditer(text))
    if not matches:
        matches.extend((index, candidate) for index, candidate in enumerate(_extract_from_json(text)))
    cleaned = [_normalize_candidate(candidate) for _, candidate in sorted(matches, key=lambda item: item[0])]
    cleaned = [candidate for candidate in cleaned if candidate]
    return dedupe_preserve_order(cleaned)


def _extract_from_json(text: str) -> list[str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    results: list[str] = []

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in {"venuename", "theatrename", "name"} and isinstance(item, str):
                    results.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return results


def extract_from_candidates(candidates: Iterable[str]) -> list[str]:
    cleaned = [_normalize_candidate(candidate) for candidate in candidates]
    cleaned = [candidate for candidate in cleaned if candidate]
    return dedupe_preserve_order(cleaned)


def extract_theatre_name(value: object) -> str:
    if isinstance(value, str):
        return _normalize_candidate(value)
    if isinstance(value, dict):
        for key in ("venueName", "theatreName", "name", "title"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return _normalize_candidate(candidate)
    return _normalize_candidate(str(value))


def extract_theatre_names_from_entries(entries: Iterable[object]) -> list[str]:
    return dedupe_preserve_order(
        candidate
        for candidate in (extract_theatre_name(entry) for entry in entries)
        if candidate
    )
