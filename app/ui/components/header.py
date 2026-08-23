"""
ui/components/header.py

Header adapts between:
- Desktop: logo + "+2 Cipher" + small subtitle ("Encode (+2) · Decode (-2)"),
  theme toggle on the right (spec section 11).
- Mobile: compact logo/back + current page title, theme toggle on the right.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Line
from kivy.properties import StringProperty
from kivy.metrics import dp
import os

from .behaviors import ThemedBehavior
from .buttons import IconButton
from .icons import icon_char, ICON_FONT
from ..asset_paths import icon_path

_ICON_PATH = icon_path("icon_64.png")


class Header(ThemedBehavior, BoxLayout):
    def __init__(self, on_toggle_theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = (dp(16), dp(8))
        self.spacing = dp(10)
        self._compact = False

        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._border_color = Color(0, 0, 0, 0)
            self._border_line = Line(points=[])
        self.bind(pos=self._sync_border, size=self._sync_border)

        if os.path.exists(_ICON_PATH):
            self._logo_label = Image(source=_ICON_PATH, size_hint=(None, 1), width=dp(26),
                                      allow_stretch=True, keep_ratio=True)
        else:
            self._logo_label = Label(text=icon_char("logo"), font_name=ICON_FONT, font_size=20,
                                      size_hint=(None, 1), width=dp(26))
        title_box = BoxLayout(orientation="vertical")
        self._title_label = Label(text="+2 Cipher", bold=True, font_size=16, halign="left",
                                   valign="bottom", size_hint_y=None, height=dp(22))
        self._subtitle_label = Label(text="Encode (+2) · Decode (-2)", font_size=11,
                                      halign="left", valign="top", size_hint_y=None, height=dp(16))
        for w in (self._title_label, self._subtitle_label):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        title_box.add_widget(self._title_label)
        title_box.add_widget(self._subtitle_label)

        spacer = BoxLayout()

        self._theme_toggle = IconButton(icon="theme_dark", tooltip_text="Toggle theme")
        if on_toggle_theme:
            self._theme_toggle.bind(on_release=lambda *a: on_toggle_theme())

        self.add_widget(self._logo_label)
        self.add_widget(title_box)
        self._title_box = title_box
        self.add_widget(spacer)
        self.add_widget(self._theme_toggle)

    def set_context(self, title: str, subtitle: str = ""):
        self._title_label.text = title
        self._subtitle_label.text = subtitle
        self._subtitle_label.height = dp(16) if subtitle else 0

    def set_compact(self, compact: bool):
        self._compact = compact
        self.height = dp(52) if compact else dp(60)
        self._logo_label.opacity = 0 if compact else 1
        self._logo_label.width = 0 if compact else dp(26)

    def _sync_border(self, *_):
        self._border_line.points = [self.x, self.y, self.right, self.y]

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background")
        self._border_color.rgba = self.theme.color("border")
        if isinstance(self._logo_label, Label):
            self._logo_label.color = self.theme.accent("main")
        self._title_label.color = self.theme.color("text_primary")
        self._subtitle_label.color = self.theme.color("text_caption")
        self._theme_toggle.icon = "theme_light" if self.theme.is_light else "theme_dark"
        self._theme_toggle._icon_label.text = icon_char(self._theme_toggle.icon)
