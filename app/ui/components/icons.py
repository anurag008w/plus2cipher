"""
ui/components/icons.py

A consistent, non-emoji icon system (spec section 47), built on the Material
Design Icons font that ships inside the kivymd package (fonts/materialdesign
icons-webfont.ttf) plus its glyph name -> unicode codepoint table. No network
access is required -- the font file is bundled with the pip dependency.

Usage:
    from app.ui.components.icons import icon_char, ICON_FONT
    Label(text=icon_char('content-copy'), font_name=ICON_FONT)
"""

from __future__ import annotations

import os

try:
    import kivymd

    ICON_FONT = os.path.join(os.path.dirname(kivymd.__file__), "fonts", "materialdesignicons-webfont.ttf")
    from kivymd.icon_definitions import md_icons
except Exception:  # pragma: no cover - defensive fallback if kivymd is absent
    ICON_FONT = None
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
