"""Persistence helpers for issue cards."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from utils.csvhandle import get_database_file_path


@dataclass
class CardRecord:
    card_id: str = ""
    issue: str = ""
    detail: str = ""
    action: str = ""
    lu: str = ""
    tanggal: str = ""
    shift: str = ""
    user: str = ""
    saved_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, record: dict[str, str]) -> "CardRecord":
        return cls(
            card_id=record.get("card_id", ""),
            lu=record.get("lu", ""),
            tanggal=record.get("tanggal", ""),
            shift=record.get("shift", ""),
            issue=record.get("issue", ""),
            detail=record.get("detail", ""),
            action=record.get("action", ""),
            user=record.get("user", ""),
            saved_at=(
                datetime.fromisoformat(record["saved_at"])
                if record.get("saved_at")
                else datetime.now()
            ),
        )


def build_record_rows(
    cards: Iterable[dict],
    username: str = "",
    lu: str = "",
    tanggal: str = "",
    shift: str = "",
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for card_data in cards:
        if not card_data:
            continue

        details = card_data.get("details", []) or [None]
        for detail in details:
            detail_text = (detail or {}).get("detail", "") if detail else ""
            actions = (detail or {}).get("actions", []) or [""]
            for action in actions:
                rows.append(
                    {
                        "card_id": card_data.get("id", ""),
                        "lu": lu,
                        "tanggal": tanggal,
                        "shift": shift,
                        "issue": card_data.get("issue", ""),
                        "detail": detail_text,
                        "action": action or "",
                        "user": username,
                        "saved_at": datetime.now().isoformat(timespec="seconds"),
                    }
                )
    return rows


def append_cards_to_csv(rows: list[dict[str, str]]) -> Path:
    file_path = Path(get_database_file_path())

    if file_path.exists():
        existing_df = pd.read_csv(file_path)
        combined = pd.concat([existing_df, pd.DataFrame(rows)], ignore_index=True)
    else:
        combined = pd.DataFrame(rows)

    combined.to_csv(file_path, index=False, encoding="utf-8-sig")
    return file_path
