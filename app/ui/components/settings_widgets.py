"""
ui/components/settings_widgets.py

SettingSection - a titled group of rows (Appearance, Behavior, Cipher, ...).
SettingRow     - label (+ optional description) with a control aligned right.
ColorSelector  - the 7-swatch accent color picker.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.metrics import dp

from .behaviors import ThemedBehavior
from .icons import icon_char


class SettingSection(ThemedBehavior, BoxLayout):
    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing = dp(2)
        self.padding = (0, dp(4))

        self._title_label = Label(text=title.upper(), bold=True, font_size=12,
                                   halign="left", size_hint_y=1)
        self._title_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.add_widget(self._title_label)

        self._rows_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(1))
        self._rows_container.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        with self._rows_container.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self._rows_container.pos, size=self._rows_container.size)
        self._rows_container.bind(pos=self._sync_bg, size=self._sync_bg)
        self.add_widget(self._rows_container)

        self.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))

    def add_row(self, row):
        self._rows_container.add_widget(row)

    def _sync_bg(self, *_):
        self._bg.pos = self._rows_container.pos
        self._bg.size = self._rows_container.size
        self._bg.radius = [self.theme.radius("card") if self.theme else 14]

    def apply_theme(self):
        if not self.theme:
            return
        self._title_label.color = self.theme.color("text_caption")
        self._bg_color.rgba = self.theme.color("card")
        self._sync_bg()


class SettingRow(ThemedBehavior, BoxLayout):
    def __init__(self, label: str, description: str = "", control=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(72) if description else dp(56)
        self.padding = (dp(16), dp(8))
        self.spacing = dp(12)

        with self.canvas.before:
            self._border_color = Color(0, 0, 0, 0)
            self._border_line = Line(points=[])
        self.bind(pos=self._sync_border, size=self._sync_border)

        text_box = BoxLayout(orientation="vertical")
        self._label_widget = Label(text=label, font_size=14, halign="left", valign="middle",
                                    size_hint_y=1)
        self._desc_widget = Label(text=description, font_size=11.5, halign="left", valign="top",
                                   size_hint_y=0.8 if description else 0)
        for w in (self._label_widget, self._desc_widget):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        text_box.add_widget(self._label_widget)
        if description:
            text_box.add_widget(self._desc_widget)
        self.add_widget(text_box)

        if control is not None:
            control.size_hint_x = None
            self.add_widget(control)
        self._control = control

    def _sync_border(self, *_):
        self._border_line.points = [self.x, self.y, self.right, self.y]

    def apply_theme(self):
        if not self.theme:
            return
        self._border_color.rgba = self.theme.color("border")
        self._label_widget.color = self.theme.color("text_primary")
        self._desc_widget.color = self.theme.color("text_caption")


class _Swatch(ButtonBehavior, ThemedBehavior, Widget):
    def __init__(self, accent_name: str, on_select=None, **kwargs):
        self.accent_name = accent_name
        self._on_select = on_select
        self._selected = False
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(30), dp(30))
        with self.canvas.before:
            self._fill_color = Color(1, 1, 1, 1)
            self._fill = Ellipse(pos=self.pos, size=self.size)
            self._ring_color = Color(0, 0, 0, 0)
            self._ring = Line(width=1.8)
        self.bind(pos=self._sync, size=self._sync)
        self.bind(on_release=lambda *a: self._on_select(self.accent_name) if self._on_select else None)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.apply_theme()

    def _sync(self, *_):
        self._fill.pos = self.pos
        self._fill.size = self.size
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        self._ring.circle = (cx, cy, self.width / 2 + 3)

    def apply_theme(self):
        if not self.theme:
            return
        from ..theme import palettes

        family = palettes.ACCENTS.get(self.accent_name, palettes.ACCENTS["purple"])
        self._fill_color.rgba = family["main"]
        self._ring_color.rgba = self.theme.color("text_primary") if self._selected else (0, 0, 0, 0)
        self._sync()


class ColorSelector(ThemedBehavior, BoxLayout):
    def __init__(self, selected: str, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(36)
        self._selected = selected
        self._on_user_select = on_select
        self._swatches = {}
        from ..theme.palettes import ACCENTS

        for name in ACCENTS.keys():
            sw = _Swatch(name, on_select=self._handle_select)
            sw.set_selected(name == selected)
            self._swatches[name] = sw
            self.add_widget(sw)
        self.bind(minimum_width=lambda w, *_: setattr(w, "width", w.minimum_width))
        self.size_hint_x = None
        self.width = self.minimum_width

    def _handle_select(self, name: str):
        for n, sw in self._swatches.items():
            sw.set_selected(n == name)
        if self._on_user_select:
            self._on_user_select(name)

    def apply_theme(self):
        pass
