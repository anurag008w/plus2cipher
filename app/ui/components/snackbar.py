"""
ui/components/snackbar.py

Lightweight toast/snackbar feedback (spec section 19/46): "Copied", "Pasted",
"Cleared", "Added to favorites", etc. Never blocks interaction, auto-dismisses,
and queues messages so rapid actions don't stack overlapping toasts.

Usage: mounted once at the root of the app (see main.py), then anywhere:
    App.get_running_app().snackbar_host.show("Copied to clipboard")
"""

from __future__ import annotations

from collections import deque

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

from .behaviors import ThemedBehavior
from .icons import icon_char, ICON_FONT

_DISPLAY_SECONDS = 2.0


class _SnackbarBubble(ThemedBehavior, FloatLayout):
    def __init__(self, message: str, kind: str = "info", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.opacity = 0

        icon_name = {"success": "success", "error": "error", "warning": "warning"}.get(kind, "")

        # Icon glyph and text need separate Labels (different fonts), laid
        # out manually in _layout() below.
        self._icon_label = Label(text=icon_char(icon_name) if icon_name else "",
                                  font_name=ICON_FONT, font_size=15,
                                  size_hint=(None, None), size=(dp(20), dp(20)))
        self._text_label = Label(text=message, font_size=13, size_hint=(None, None))
        self._text_label.bind(texture_size=lambda w, *_: setattr(w, "size", w.texture_size))
        self._kind = kind

        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.add_widget(self._text_label)
        if icon_name:
            self.add_widget(self._icon_label)

        self._text_label.bind(texture_size=self._layout)
        Clock.schedule_once(lambda dt: self._layout(), 0)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _layout(self, *_):
        pad_x, pad_y = dp(16), dp(10)
        icon_w = dp(24) if self._icon_label.text else 0
        text_w, text_h = self._text_label.texture_size
        total_w = pad_x * 2 + icon_w + text_w
        total_h = max(text_h, dp(20)) + pad_y * 2
        self.size = (total_w, total_h)
        if self._icon_label.text:
            self._icon_label.pos = (pad_x, (total_h - dp(20)) / 2)
        self._text_label.pos = (pad_x + icon_w, (total_h - text_h) / 2)

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.theme.radius("chip") if self.theme else 8]

    def apply_theme(self):
        if not self.theme:
            return
        base = {
            "success": self.theme.color("success"),
            "error": self.theme.color("error"),
            "warning": self.theme.color("warning"),
        }.get(self._kind, None)
        self._bg_color.rgba = self.theme.color("card_elevated")
        self._text_label.color = self.theme.color("text_primary")
        self._icon_label.color = base if base else self.theme.accent("main")
        self._sync_bg()


class SnackbarHost(FloatLayout):
    """Mount ONE of these at the very top of the widget tree (see main.py)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._queue = deque()
        self._current = None
        self.size_hint = (1, 1)

    def show(self, message: str, kind: str = "info"):
        self._queue.append((message, kind))
        if self._current is None:
            self._pop_next()

    def _pop_next(self, *_):
        if not self._queue:
            self._current = None
            return
        message, kind = self._queue.popleft()
        bubble = _SnackbarBubble(message, kind=kind)
        self._current = bubble
        self.add_widget(bubble)
        Clock.schedule_once(lambda dt: self._position(bubble), 0)
        Animation(opacity=1, duration=0.15).start(bubble)
        Clock.schedule_once(lambda dt: self._dismiss(bubble), _DISPLAY_SECONDS)

    def _position(self, bubble):
        bubble.center_x = self.center_x
        bubble.y = dp(24)

    def _dismiss(self, bubble):
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *a: self._remove(bubble))
        anim.start(bubble)

    def _remove(self, bubble):
        if bubble.parent:
            self.remove_widget(bubble)
        Clock.schedule_once(self._pop_next, 0)
