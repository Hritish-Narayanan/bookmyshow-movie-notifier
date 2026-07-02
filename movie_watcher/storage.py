"""Persist and restore theatre state."""

from __future__ import annotations

import json
from pathlib import Path



def load_theatres(path: Path) -> list[object]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("theatres", []) if isinstance(data, dict) else []


def save_theatres(path: Path, theatres: list[object]) -> None:
    path.write_text(
        json.dumps({"theatres": theatres}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def backup_file(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def restore_file(path: Path, content: str | None) -> None:
    if content is None:
        if path.exists():
            path.unlink()
        return
    path.write_text(content, encoding="utf-8")
