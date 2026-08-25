"""
ui/theme/manager.py

The single runtime source of truth for "what does the app look like right
now". Wraps Settings + palettes + tokens, and is a Kivy EventDispatcher so
any widget can react live when the user changes theme, accent, density,
font size, or corner radius -- without losing screen state (spec section 8).

Usage pattern used throughout ui/components and ui/screens:

    theme = App.get_running_app().theme
    theme.bind(on_change=lambda *a: self._apply_theme())

    def _apply_theme(self):
        self.bg_color = theme.color('card')
        self.accent_color = theme.accent('main')
"""

from __future__ import annotations

from kivy.event import EventDispatcher

from . import palettes, tokens


class ThemeManager(EventDispatcher):
    """Not a Kivy Widget -- a plain EventDispatcher usable anywhere."""

    __events__ = ("on_change",)

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

    # -- palette lookups ---------------------------------------------------------

    def _palette(self) -> dict:
        return palettes.LIGHT if self.settings.theme == "light" else palettes.DARK

    def color(self, name: str) -> tuple:
        return self._palette().get(name, palettes.DARK[name])

    def accent(self, variant: str = "main") -> tuple:
        family = palettes.ACCENTS.get(self.settings.accent, palettes.ACCENTS["purple"])
        return family.get(variant, family["main"])

    # -- token lookups (already respect current settings) -------------------------

    def spacing(self, name: str) -> float:
        return tokens.spacing(name, self.settings.get("density", "comfortable"))

    def radius(self, name: str) -> float:
        return tokens.radius(name, self.settings.get("radius", "standard"))

    def font_size(self, role: str) -> float:
        return tokens.font_size(role, self.settings.get("font_size", "medium"))

    def duration(self, name: str) -> float:
        return tokens.duration(name, self.settings.get("reduced_motion", False))

    @property
    def is_light(self) -> bool:
        return self.settings.theme == "light"

    # -- mutators: change + persist + broadcast -----------------------------------

    def set_theme(self, theme_name: str) -> None:
        self.settings.set("theme", theme_name)
        self.dispatch("on_change")

    def set_accent(self, accent_name: str) -> None:
        self.settings.set("accent", accent_name)
        self.dispatch("on_change")

    def set_density(self, density: str) -> None:
        self.settings.set("density", density)
        self.dispatch("on_change")

    def set_font_size(self, size_name: str) -> None:
        self.settings.set("font_size", size_name)
        self.dispatch("on_change")

    def set_radius(self, radius_name: str) -> None:
        self.settings.set("radius", radius_name)
        self.dispatch("on_change")

    def set_reduced_motion(self, enabled: bool) -> None:
        self.settings.set("reduced_motion", enabled)
        self.dispatch("on_change")

    def set_high_contrast(self, enabled: bool) -> None:
        self.settings.set("high_contrast", enabled)
        self.dispatch("on_change")

    def on_change(self, *args):
        """Default no-op required by Kivy's EventDispatcher for custom events."""
        pass

    @property
    def scale_font(self) -> float:
        return tokens._FONT_SCALE.get(self.settings.get("font_size", "medium"), 1.0)

    @property
    def scale_spacing(self) -> float:
        return 0.75 if self.settings.get("density", "comfortable") == "compact" else 1.0

    @property
    def scale_radius(self) -> float:
        r = self.settings.get("radius", "standard")
        if r == "subtle": return 0.6
        if r == "large": return 1.4
        return 1.0
