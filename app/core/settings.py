"""
core/settings.py

Persists all user-configurable preferences (theme, accent, cipher shift,
behavior toggles, limits, last mode/text) to a single local JSON file.
No Kivy dependency -- fully unit-testable.

Handles a missing or corrupted preferences file by quietly falling back to
defaults rather than crashing the app (spec section 56).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict


VALID_ACCENTS = ("purple", "blue", "cyan", "green", "amber", "pink", "red")
VALID_THEMES = ("dark", "light", "system")
VALID_DENSITY = ("compact", "comfortable")
VALID_FONT_SIZE = ("small", "medium", "large")
VALID_RADIUS = ("subtle", "standard", "large")
VALID_HISTORY_LIMITS = (50, 100, 250, 500, 1000, 0)  # 0 == unlimited
VALID_CHAR_LIMITS = (1000, 2500, 5000, 10000, 25000)


def _defaults() -> Dict[str, Any]:
    return {
        # Appearance
        "theme": "dark",
        "accent": "purple",
        "density": "comfortable",
        "font_size": "medium",
        "radius": "standard",
        "animations": True,
        "reduced_motion": False,
        "high_contrast": False,
        # Behavior
        "live_transformation": True,
        "auto_save_history": True,
        "auto_focus_input": True,
        "remember_last_mode": True,
        "remember_last_text": True,
        "confirm_before_clear": True,
        "clear_input_after_copy": False,
        # Cipher
        "shift": 2,
        # Limits
        "char_limit": 5000,
        "history_limit": 500,
        # Remembered state
        "last_mode": "encode",
        "last_text": "",
    }


@dataclass
class Settings:
    _data: Dict[str, Any] = field(default_factory=_defaults)
    _path: str = ""

    # -- factory / persistence -------------------------------------------------

    @classmethod
    def load(cls, path: str) -> "Settings":
        data = _defaults()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    data.update({k: v for k, v in loaded.items() if k in data})
            except (json.JSONDecodeError, OSError, ValueError):
                # Corrupted file -- fall back to defaults, don't crash.
                pass
        settings = cls(_data=data, _path=path)
        settings._validate()
        return settings

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self._path)) or ".", exist_ok=True)
        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self._path)  # atomic on POSIX

    def reset(self) -> None:
        self._data = _defaults()
        self.save()

    # -- validation --------------------------------------------------------------

    def _validate(self) -> None:
        d = self._data
        if d["theme"] not in VALID_THEMES:
            d["theme"] = "dark"
        if d["accent"] not in VALID_ACCENTS:
            d["accent"] = "purple"
        if d["density"] not in VALID_DENSITY:
            d["density"] = "comfortable"
        if d["font_size"] not in VALID_FONT_SIZE:
            d["font_size"] = "medium"
        if d["radius"] not in VALID_RADIUS:
            d["radius"] = "standard"
        if d["char_limit"] not in VALID_CHAR_LIMITS:
            d["char_limit"] = 5000
        if d["history_limit"] not in VALID_HISTORY_LIMITS:
            d["history_limit"] = 500
        if d["last_mode"] not in ("encode", "decode"):
            d["last_mode"] = "encode"
        if not isinstance(d["shift"], int) or not (1 <= d["shift"] <= 25):
            d["shift"] = 2

    # -- generic get/set -----------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any, autosave: bool = True) -> None:
        if key not in self._data:
            raise KeyError(f"Unknown setting: {key!r}")
        self._data[key] = value
        self._validate()
        if autosave:
            self.save()

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    # -- convenience typed accessors (used throughout the UI) ------------------------

    @property
    def theme(self) -> str:
        return self._data["theme"]

    @property
    def accent(self) -> str:
        return self._data["accent"]

    @property
    def shift(self) -> int:
        return self._data["shift"]

    @property
    def char_limit(self) -> int:
        return self._data["char_limit"]

    @property
    def history_limit(self) -> int:
        return self._data["history_limit"]

    @property
    def live_transformation(self) -> bool:
        return self._data["live_transformation"]
