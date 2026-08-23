"""
ui/theme/tokens.py

Centralized design tokens. Nothing in the UI layer should hardcode a
spacing/radius/font-size number -- pull it from here so the whole app stays
visually consistent and so density/font-size/radius settings apply globally.

All numeric values are in dp (density-independent pixels), Kivy's own unit,
so they scale sensibly across desktop and Android.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Responsive breakpoints (dp) -- section 4 of the spec.
# ---------------------------------------------------------------------------

BREAKPOINT_MOBILE_MAX = 600
BREAKPOINT_TABLET_MAX = 1000  # >= 1000 is "desktop"


def layout_class(width_dp: float) -> str:
    if width_dp >= BREAKPOINT_TABLET_MAX:
        return "desktop"
    if width_dp >= BREAKPOINT_MOBILE_MAX:
        return "tablet"
    return "mobile"


# ---------------------------------------------------------------------------
# Spacing scale, adjusted by the "density" setting.
# ---------------------------------------------------------------------------

_SPACING_COMFORTABLE = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32, "xxl": 48}
_SPACING_COMPACT = {"xs": 3, "sm": 6, "md": 12, "lg": 18, "xl": 24, "xxl": 36}


def spacing(name: str, density: str = "comfortable") -> float:
    table = _SPACING_COMPACT if density == "compact" else _SPACING_COMFORTABLE
    return table.get(name, table["md"])


# ---------------------------------------------------------------------------
# Corner radius, adjusted by the "radius" setting.
# ---------------------------------------------------------------------------

_RADII = {
    "subtle": {"card": 8, "control": 6, "chip": 6, "sheet": 12},
    "standard": {"card": 14, "control": 10, "chip": 8, "sheet": 20},
    "large": {"card": 20, "control": 14, "chip": 12, "sheet": 28},
}


def radius(name: str, style: str = "standard") -> float:
    table = _RADII.get(style, _RADII["standard"])
    return table.get(name, table["card"])


# ---------------------------------------------------------------------------
# Typography scale, adjusted by the "font_size" setting.
# ---------------------------------------------------------------------------

_FONT_SCALE = {"small": 0.9, "medium": 1.0, "large": 1.15}

_FONT_BASE = {
    "page_title": 24,
    "section_title": 17,
    "card_title": 13,      # e.g. "INPUT" / "OUTPUT" eyebrow labels
    "body": 15,
    "secondary": 13,
    "caption": 11,
}


def font_size(role: str, size_setting: str = "medium") -> float:
    scale = _FONT_SCALE.get(size_setting, 1.0)
    base = _FONT_BASE.get(role, _FONT_BASE["body"])
    return round(base * scale, 1)


# ---------------------------------------------------------------------------
# Elevation -- Kivy has no native shadows, so "elevation" here is expressed
# as a border/opacity recipe consumed by components/cards.py rather than a
# literal shadow. Kept restrained per spec (no glow-heavy look).
# ---------------------------------------------------------------------------

ELEVATION = {
    "flat": {"border_alpha": 0.08, "shadow_alpha": 0.0},
    "card": {"border_alpha": 0.10, "shadow_alpha": 0.18},
    "raised": {"border_alpha": 0.16, "shadow_alpha": 0.28},
}

BORDER_WIDTH = 1.0
BORDER_WIDTH_FOCUS = 1.6

ICON_SIZE_SM = 18
ICON_SIZE_MD = 22
ICON_SIZE_LG = 28


# ---------------------------------------------------------------------------
# Animation durations (seconds). Reduced-motion mode collapses everything to
# near-zero rather than removing animations code-paths entirely.
# ---------------------------------------------------------------------------

_DURATIONS = {
    "press": 0.08,
    "hover": 0.12,
    "tab_switch": 0.16,
    "screen_transition": 0.22,
    "theme_switch": 0.18,
    "splash": 0.9,
    "toast": 0.20,
}


def duration(name: str, reduced_motion: bool = False) -> float:
    if reduced_motion:
        return 0.01
    return _DURATIONS.get(name, 0.15)
