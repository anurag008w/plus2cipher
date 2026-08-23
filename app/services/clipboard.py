"""
services/clipboard.py

Cross-platform clipboard access (spec section 54). Kivy's Clipboard core
provider already abstracts Linux (xclip/xsel/gtk) vs Android (system
clipboard service), so this module just adds a safe try/except boundary
plus a consistent success/failure return value for the UI layer.
"""

from __future__ import annotations


def copy(text: str) -> bool:
    try:
        from kivy.core.clipboard import Clipboard

        Clipboard.copy(text or "")
        return True
    except Exception:
        return False


def paste() -> str:
    try:
        from kivy.core.clipboard import Clipboard

        return Clipboard.paste() or ""
    except Exception:
        return ""
