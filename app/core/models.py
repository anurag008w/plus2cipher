"""
core/models.py

Plain-data models. No Kivy dependency so they stay testable in isolation.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ConversionRecord:
    """A single encode/decode conversion, as stored in history/favorites."""

    id: Optional[int]
    timestamp: str          # ISO-8601 UTC string
    mode: str                # "encode" | "decode"
    input_text: str
    output_text: str
    is_favorite: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_row(row: tuple) -> "ConversionRecord":
        """Build a record from a sqlite3 row: (id, timestamp, mode, input, output, favorite)."""
        rid, ts, mode, input_text, output_text, favorite = row
        return ConversionRecord(
            id=rid,
            timestamp=ts,
            mode=mode,
            input_text=input_text,
            output_text=output_text,
            is_favorite=bool(favorite),
        )
