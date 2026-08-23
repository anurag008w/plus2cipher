"""
ui/components/segmented.py

SegmentedControl: a two-option (or more) tab-like toggle. Used for the
Encode (+2) / Decode (-2) switch on the Home screen. Active option fills
with the current accent; inactive options sit on a dark neutral surface.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from kivy.metrics import dp
from kivy.animation import Animation

from .behaviors import ThemedBehavior


class SegmentedControl(ThemedBehavior, BoxLayout):
    options = ListProperty([])       # list of (value, label) tuples
    selected = StringProperty("")

    def __init__(self, options=None, selected="", on_change=None, **kwargs):
        self.options = options or []
        self.selected = selected or (self.options[0][0] if self.options else "")
        self._on_change = on_change
        self._buttons = {}
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.spacing = dp(4)
        self.padding = (dp(4), dp(4))

        with self.canvas.before:
            self._track_color = Color(0, 0, 0, 0)
            self._track = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_track, size=self._sync_track)

        for value, label in self.options:
            btn = Button(text=label, background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), bold=True, font_size=13)
            btn.value = value
            btn.bind(on_release=lambda w: self.select(w.value))
            self._buttons[value] = btn
            self.add_widget(btn)

    def _sync_track(self, *_):
        self._track.pos = self.pos
        self._track.size = self.size
        r = self.theme.radius("control") + 4 if self.theme else 14
        self._track.radius = [r]

    def select(self, value: str):
        if value == self.selected:
            return
        self.selected = value
        self._refresh_buttons()
        if self._on_change:
            self._on_change(value)

    def _refresh_buttons(self):
        if not self.theme:
            return
        r = self.theme.radius("control")
        for value, btn in self._buttons.items():
            is_active = value == self.selected
            with btn.canvas.before:
                btn.canvas.before.clear()
                Color(*(self.theme.accent("main") if is_active else (0, 0, 0, 0)))
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[r])
            btn.color = self.theme.accent("on_accent") if is_active else self.theme.color("text_secondary")
            btn.bind(pos=self._rebind_bg(btn, is_active, r), size=self._rebind_bg(btn, is_active, r))

    def _rebind_bg(self, btn, is_active, r):
        def _update(*_):
            btn.canvas.before.clear()
            with btn.canvas.before:
                Color(*(self.theme.accent("main") if is_active else (0, 0, 0, 0)))
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[r])
        return _update

    def apply_theme(self):
        if not self.theme:
            return
        self._track_color.rgba = self.theme.color("control_inactive")
        self._sync_track()
        self._refresh_buttons()
