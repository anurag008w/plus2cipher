"""
ui/components/switch.py

ThemedSwitch: a small on/off toggle whose ON track color is the current
accent (spec section 7 explicitly lists "selected switches" among the
controls that must follow the accent color) and animates its thumb.
"""

from __future__ import annotations

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.properties import BooleanProperty
from kivy.animation import Animation
from kivy.metrics import dp

from .behaviors import ThemedBehavior


class ThemedSwitch(ButtonBehavior, ThemedBehavior, Widget):
    active = BooleanProperty(False)

    def __init__(self, active: bool = False, on_change=None, **kwargs):
        self._on_change = on_change
        super().__init__(**kwargs)
        self.active = active
        self.size_hint = (None, None)
        self.size = (dp(46), dp(26))

        with self.canvas.before:
            self._track_color = Color(0, 0, 0, 0)
            self._track = RoundedRectangle(pos=self.pos, size=self.size)
            self._thumb_color = Color(1, 1, 1, 1)
            self._thumb = Ellipse(size=(dp(20), dp(20)))

        self.bind(pos=self._sync, size=self._sync)
        self.bind(on_release=lambda *a: self.toggle())
        self.bind(active=lambda *a: self._refresh(animate=True))

    def toggle(self):
        self.active = not self.active
        if self._on_change:
            self._on_change(self.active)

    def _sync(self, *_):
        self._track.pos = self.pos
        self._track.size = self.size
        self._track.radius = [self.height / 2]
        self._thumb.size = (self.height - dp(6), self.height - dp(6))
        self._position_thumb(animate=False)

    def _position_thumb(self, animate: bool):
        target_x = (self.right - self.height + dp(3)) if self.active else (self.x + dp(3))
        target_y = self.y + dp(3)
        if animate:
            Animation(pos=(target_x, target_y), duration=0.12, t="out_quad").start(
                _ThumbProxy(self._thumb)
            )
        else:
            self._thumb.pos = (target_x, target_y)

    def _refresh(self, animate: bool = False):
        if not self.theme:
            return
        self._track_color.rgba = self.theme.accent("main") if self.active else self.theme.color("control_inactive")
        self._position_thumb(animate=animate)

    def apply_theme(self):
        self._refresh(animate=False)


from kivy.event import EventDispatcher
class _ThumbProxy(EventDispatcher):
    """Lets kivy.animation.Animation tween an Ellipse's `pos` like a widget's."""

    def __init__(self, ellipse):
        self._ellipse = ellipse

    @property
    def pos(self):
        return self._ellipse.pos

    @pos.setter
    def pos(self, value):
        self._ellipse.pos = value
