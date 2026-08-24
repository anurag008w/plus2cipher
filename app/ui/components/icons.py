"""
ui/components/icons.py

A consistent, non-emoji icon system (spec section 47), built on the Material
Design Icons font. The font file and its glyph-name -> unicode codepoint
table are vendored into assets/fonts/ (see assets/fonts/LICENSE.md) rather
than imported from the kivymd package at runtime, because python-for-android
has no build recipe for kivymd -- it falls back to an unconstrained `pip
install kivymd` during the Android build, which pulls in dependency
conflicts from newer kivymd releases and fails. Vendoring the two small
files we actually use removes that dependency (and its risk) entirely
without losing anything, since this app never uses any KivyMD widgets.

Usage:
    from app.ui.components.icons import icon_char, ICON_FONT
    Label(text=icon_char('content-copy'), font_name=ICON_FONT)
"""

from __future__ import annotations

import json

from ..asset_paths import ICONS_DIR
import os

_FONTS_DIR = os.path.join(os.path.dirname(ICONS_DIR), "fonts")
ICON_FONT = os.path.join(_FONTS_DIR, "materialdesignicons-webfont.ttf")

try:
    with open(os.path.join(_FONTS_DIR, "md_icons.json"), "r", encoding="utf-8") as _f:
        md_icons = json.load(_f)
except Exception:  # pragma: no cover - defensive fallback if the asset is missing
    md_icons = {}

# Semantic name -> Material Design Icons glyph name, so the rest of the app
# never has to know raw MDI names and we can swap the underlying icon set
# in one place later if needed.
ICON_MAP = {
    "home": "home-variant-outline",
    "home_active": "home-variant",
    "history": "history",
    "favorites": "star-outline",
    "favorites_active": "star",
    "settings": "cog-outline",
    "settings_active": "cog",
    "about": "information-outline",
    "copy": "content-copy",
    "paste": "content-paste",
    "clear": "close-circle-outline",
    "swap": "swap-horizontal",
    "share": "share-variant-outline",
    "favorite_off": "star-outline",
    "favorite_on": "star",
    "reuse": "restore",
    "delete": "trash-can-outline",
    "search": "magnify",
    "close": "close",
    "check": "check-circle-outline",
    "chevron_right": "chevron-right",
    "theme_dark": "moon-waning-crescent",
    "theme_light": "white-balance-sunny",
    "theme_system": "theme-light-dark",
    "menu": "menu",
    "back": "arrow-left",
    "warning": "alert-circle-outline",
    "error": "close-octagon-outline",
    "success": "check-circle-outline",
    "empty_history": "clock-outline",
    "empty_favorites": "star-off-outline",
    "empty_search": "file-search-outline",
    "keyboard": "keyboard-outline",
    "storage": "database-outline",
    "export": "tray-arrow-up",
    "import": "tray-arrow-down",
    "github": "github",
    "accessibility": "human-handsup",
    "logo": "alpha-c-box-outline",
}


def icon_char(name: str) -> str:
    """Look up a semantic icon name (see ICON_MAP) and return its glyph."""
    mdi_name = ICON_MAP.get(name, name)
    return md_icons.get(mdi_name, "?")
