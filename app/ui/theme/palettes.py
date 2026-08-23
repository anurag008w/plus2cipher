"""
ui/theme/palettes.py

Raw color values. Kept separate from tokens.py / manager.py so the palette
can be tuned without touching any layout logic. All colors are (r, g, b, a)
tuples in 0-1 float space, the format Kivy expects for canvas instructions
and widget color properties.
"""

from __future__ import annotations


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b, alpha)


# ---------------------------------------------------------------------------
# Accent color families. Each accent has:
#   main    -> primary buttons, active states, focus rings
#   hover   -> hovered state (slightly lighter)
#   pressed -> pressed state (slightly darker)
#   soft    -> low-opacity background wash for selected chips/segmented tabs
#   on_accent -> text/icon color to place on top of `main`
# ---------------------------------------------------------------------------

ACCENTS = {
    "purple": {
        "main": hex_to_rgba("#8B5CF6"),
        "hover": hex_to_rgba("#9D75F8"),
        "pressed": hex_to_rgba("#7A46E0"),
        "soft": hex_to_rgba("#8B5CF6", 0.16),
        "on_accent": hex_to_rgba("#FFFFFF"),
    },
    "blue": {
        "main": hex_to_rgba("#5B8DEF"),
        "hover": hex_to_rgba("#71A0F5"),
        "pressed": hex_to_rgba("#4676D6"),
        "soft": hex_to_rgba("#5B8DEF", 0.16),
        "on_accent": hex_to_rgba("#FFFFFF"),
    },
    "cyan": {
        "main": hex_to_rgba("#22D3EE"),
        "hover": hex_to_rgba("#4FDDF2"),
        "pressed": hex_to_rgba("#16B8D1"),
        "soft": hex_to_rgba("#22D3EE", 0.16),
        "on_accent": hex_to_rgba("#04222A"),
    },
    "green": {
        "main": hex_to_rgba("#34D399"),
        "hover": hex_to_rgba("#54DCAB"),
        "pressed": hex_to_rgba("#22B884"),
        "soft": hex_to_rgba("#34D399", 0.16),
        "on_accent": hex_to_rgba("#04241A"),
    },
    "amber": {
        "main": hex_to_rgba("#F5B342"),
        "hover": hex_to_rgba("#F7C264"),
        "pressed": hex_to_rgba("#DE9C27"),
        "soft": hex_to_rgba("#F5B342", 0.16),
        "on_accent": hex_to_rgba("#241703"),
    },
    "pink": {
        "main": hex_to_rgba("#EC6FBB"),
        "hover": hex_to_rgba("#F088C7"),
        "pressed": hex_to_rgba("#D953A5"),
        "soft": hex_to_rgba("#EC6FBB", 0.16),
        "on_accent": hex_to_rgba("#25051B"),
    },
    "red": {
        "main": hex_to_rgba("#F0625F"),
        "hover": hex_to_rgba("#F37F7C"),
        "pressed": hex_to_rgba("#D84744"),
        "soft": hex_to_rgba("#F0625F", 0.16),
        "on_accent": hex_to_rgba("#FFFFFF"),
    },
}


# ---------------------------------------------------------------------------
# Dark palette (default). Deep near-black navy, restrained.
# ---------------------------------------------------------------------------

DARK = {
    "background": hex_to_rgba("#070A13"),
    "background_secondary": hex_to_rgba("#0D1220"),
    "card": hex_to_rgba("#111827"),
    "card_elevated": hex_to_rgba("#151B2B"),
    "border": hex_to_rgba("#8FA8FF", 0.10),
    "border_strong": hex_to_rgba("#8FA8FF", 0.20),
    "text_primary": hex_to_rgba("#EDEFF7"),
    "text_secondary": hex_to_rgba("#9AA3B8"),
    "text_caption": hex_to_rgba("#6B7488"),
    "text_disabled": hex_to_rgba("#4A5266"),
    "surface_hover": hex_to_rgba("#8FA8FF", 0.06),
    "surface_pressed": hex_to_rgba("#8FA8FF", 0.12),
    "control_inactive": hex_to_rgba("#161D2E"),
    "success": hex_to_rgba("#34D399"),
    "warning": hex_to_rgba("#F5B342"),
    "error": hex_to_rgba("#F0625F"),
    "scrim": hex_to_rgba("#020308", 0.72),
}


# ---------------------------------------------------------------------------
# Light palette. Independently designed (not an inversion) but with the
# same component hierarchy: background < card < elevated card.
# ---------------------------------------------------------------------------

LIGHT = {
    "background": hex_to_rgba("#F4F5FA"),
    "background_secondary": hex_to_rgba("#EAECF4"),
    "card": hex_to_rgba("#FFFFFF"),
    "card_elevated": hex_to_rgba("#FFFFFF"),
    "border": hex_to_rgba("#1A2340", 0.09),
    "border_strong": hex_to_rgba("#1A2340", 0.16),
    "text_primary": hex_to_rgba("#151A2B"),
    "text_secondary": hex_to_rgba("#565E75"),
    "text_caption": hex_to_rgba("#7A8199"),
    "text_disabled": hex_to_rgba("#B0B5C4"),
    "surface_hover": hex_to_rgba("#1A2340", 0.04),
    "surface_pressed": hex_to_rgba("#1A2340", 0.08),
    "control_inactive": hex_to_rgba("#E7E9F2"),
    "success": hex_to_rgba("#0F9D6E"),
    "warning": hex_to_rgba("#B4780C"),
    "error": hex_to_rgba("#D33E3B"),
    "scrim": hex_to_rgba("#151A2B", 0.45),
}
