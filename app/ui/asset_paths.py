"""
ui/asset_paths.py

Centralized asset path resolution. Every screen/component that needs the
app icon should import `icon_path()` from here rather than computing its
own chain of os.path.dirname() calls — that pattern is exactly what caused
the sidebar/header logo to silently fall back to a placeholder glyph
earlier (an off-by-one in the dirname chain pointed inside app/ instead of
the project root).
"""

from __future__ import annotations

import os

# app/ui/asset_paths.py -> up two levels -> project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICONS_DIR = os.path.join(PROJECT_ROOT, "assets", "icons")


def icon_path(filename: str) -> str:
    return os.path.join(ICONS_DIR, filename)
