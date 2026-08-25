"""
ui/components/tooltip.py

Minimal desktop tooltip: a small floating label that appears near an
icon-only control after a short hover delay, and disappears immediately on
mouse-leave. On Android there is no mouse/hover concept, so this behavior
simply never triggers there -- the accessible label (content_desc-like
text) is what mobile screen readers rely on instead (spec section 33).
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty

from .behaviors import HoverBehavior

_HOVER_DELAY = 0.45

# On Android there is no mouse/hover — tooltips must be fully disabled
# because touch-up events never trigger on_leave, causing ghost tooltips.
try:
    from android import mActivity  # noqa: F401
    _IS_ANDROID = True
except Exception:
    _IS_ANDROID = False


class _TooltipLabel(Label):
    def __init__(self, text, **kwargs):
        super().__init__(text=text, size_hint=(None, None), **kwargs)
        self.padding = (10, 6)
        self.color = (0.93, 0.94, 0.97, 1)
        self.font_size = 12
        self.bind(texture_size=self._resize)
        with self.canvas.before:
            Color(0.05, 0.06, 0.11, 0.96)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _resize(self, *_):
        self.size = (self.texture_size[0] + 20, self.texture_size[1] + 12)

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size


class TooltipBehavior(HoverBehavior):
    """Mixin: set `tooltip_text` on the widget to enable a hover tooltip."""

    tooltip_text = StringProperty("")

    def __init__(self, **kwargs):
        self._tooltip_widget = None
        self._tooltip_event = None
        super().__init__(**kwargs)

    def on_enter(self):
        # Android has no hover — never show tooltips there
        if _IS_ANDROID or not self.tooltip_text:
            return
        self._tooltip_event = Clock.schedule_once(self._show_tooltip, _HOVER_DELAY)

    def on_leave(self):
        if self._tooltip_event:
            self._tooltip_event.cancel()
            self._tooltip_event = None
        self._hide_tooltip()

    def on_touch_up(self, touch):
        # Always hide tooltip on any touch release (safety net for mobile/desktop)
        self._hide_tooltip()
        if self._tooltip_event:
            self._tooltip_event.cancel()
            self._tooltip_event = None
        return super().on_touch_up(touch)

    def _show_tooltip(self, *_):
        if not self.get_root_window():
            return
        self._tooltip_widget = _TooltipLabel(text=self.tooltip_text)
        win_x, win_y = self.to_window(self.center_x, self.top)
        Window.add_widget(self._tooltip_widget)
        self._tooltip_widget.center_x = win_x
        self._tooltip_widget.y = win_y + 8

    def _hide_tooltip(self):
        if self._tooltip_widget is not None:
            try:
                Window.remove_widget(self._tooltip_widget)
            except Exception:
                pass
            self._tooltip_widget = None

