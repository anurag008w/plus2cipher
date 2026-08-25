"""
ui/screens/splash.py

Splash screen matching the reference design (icon + reference animation
supplied by the user): dark starfield background, a couple of slow shooting
stars, the app icon badge with two orbiting dots and concentric rings, the
"+2 Cipher" title, "Encode (+2) · Decode (-2)" subtitle, a soft flowing
wave ribbon along the bottom, and a small pulsing "LOADING..." indicator.

Runs for ~5 seconds (matching the reference clip) before auto-navigating to
Home. In Reduced Motion mode this collapses to a fast, near-static ~0.6s
screen instead -- accessibility always wins over the showcase animation.
"""

from __future__ import annotations

import math
import os
import random

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line, Point
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from ..components.behaviors import ThemedBehavior
from ..asset_paths import icon_path

_ICON_PATH = icon_path("icon_192.png")

_SPLASH_DURATION = 5.0
_ENTRANCE_DURATION = 0.45


class _StarField(Widget):
    """A scattering of static Points plus a few slow diagonal shooting stars."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._star_points = []
        self._shooting = []
        with self.canvas:
            self._star_color = Color(0.75, 0.8, 1, 0.55)
            self._stars = Point(points=[], pointsize=1.1)
        self.bind(size=self._regenerate, pos=self._regenerate)

    def _regenerate(self, *_):
        if self.width <= 0 or self.height <= 0:
            return
        rng = random.Random(42)  # deterministic layout, redrawn identically on resize
        pts = []
        count = int((self.width * self.height) / 2600)
        for _ in range(max(30, min(count, 260))):
            x = self.x + rng.uniform(0, self.width)
            y = self.y + rng.uniform(0, self.height)
            pts.extend([x, y])
        self._stars.points = pts

        # (re)build shooting stars proportional to screen size
        self._shooting = []
        for i in range(3):
            self._shooting.append(self._make_shooting_star(i))

    def _make_shooting_star(self, seed):
        rng = random.Random(1000 + seed)
        length = dp(70)
        start_x = self.x + rng.uniform(0, self.width)
        start_y = self.y + self.height * rng.uniform(0.55, 1.0)
        speed = rng.uniform(0.16, 0.26)  # screen-widths per second
        delay = rng.uniform(0, 3.0)
        color = (0.66, 0.55, 1, 0) if seed % 2 == 0 else (0.4, 0.75, 1, 0)
        with self.canvas:
            c = Color(*color)
            ln = Line(points=[start_x, start_y, start_x - length, start_y + length], width=1.4)
        return {
            "color": c, "line": ln, "start_x": start_x, "start_y": start_y,
            "length": length, "speed": speed, "delay": delay, "t": 0.0,
        }

    def advance(self, dt):
        for star in self._shooting:
            star["t"] += dt
            t = star["t"] - star["delay"]
            period = 1.0 / max(star["speed"], 0.01)
            if t < 0:
                star["color"].a = 0
                continue
            phase = (t % period) / period
            travel = phase * (self.width + dp(140)) - dp(70)
            x = star["start_x"] - travel
            y = star["start_y"] - travel * 0.55
            star["line"].points = [x, y, x - star["length"], y + star["length"] * 0.55]
            alpha = min(phase * 6, 1.0, (1.0 - phase) * 6) if phase < 1.0 else 0
            star["color"].a = max(0.0, min(alpha, 0.85))


class _OrbitBadge(Widget):
    """The icon image plus two concentric rings and two orbiting dots."""

    def __init__(self, accent_main, accent_secondary, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(180), dp(180))
        self._angle_a = 0.0
        self._angle_b = 200.0

        with self.canvas.before:
            self._ring_color_outer = Color(*accent_main, 0.28)
            self._ring_outer = Line(width=1.1)
            self._ring_color_inner = Color(*accent_secondary, 0.22)
            self._ring_inner = Line(width=1.1)
            self._dot_a_color = Color(*accent_main, 0.9)
            self._dot_a = Ellipse(size=(dp(9), dp(9)))
            self._dot_b_color = Color(*accent_secondary, 0.9)
            self._dot_b = Ellipse(size=(dp(7), dp(7)))

        if os.path.exists(_ICON_PATH):
            self._icon = Image(source=_ICON_PATH, size=(dp(120), dp(120)), size_hint=(None, None),
                                allow_stretch=True, keep_ratio=True)
            self.add_widget(self._icon)

        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        # NOTE: center_x/center_y are cache=True AliasProperties on Widget.
        # Reading them from inside a callback that is itself bound to this
        # same widget's `pos`/`size` can observe a stale cached value before
        # Kivy's own internal cache invalidation has run. Computing from the
        # raw x/y/width/height avoids that ordering hazard entirely.
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        r_outer = self.width / 2 - dp(6)
        r_inner = self.width / 2 - dp(28)
        self._ring_outer.circle = (cx, cy, r_outer)
        self._ring_inner.circle = (cx, cy, r_inner)
        if hasattr(self, "_icon"):
            self._icon.center = (cx, cy)
        self._update_dots()

    def _update_dots(self):
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        r_outer = self.width / 2 - dp(6)
        r_inner = self.width / 2 - dp(28)
        ax = cx + r_outer * math.cos(math.radians(self._angle_a))
        ay = cy + r_outer * math.sin(math.radians(self._angle_a))
        bx = cx + r_inner * math.cos(math.radians(self._angle_b))
        by = cy + r_inner * math.sin(math.radians(self._angle_b))
        self._dot_a.pos = (ax - dp(4.5), ay - dp(4.5))
        self._dot_b.pos = (bx - dp(3.5), by - dp(3.5))

    def advance(self, dt):
        self._angle_a = (self._angle_a + dt * 46) % 360
        self._angle_b = (self._angle_b - dt * 34) % 360
        self._update_dots()


class _WaveRibbon(Widget):
    """A soft flowing purple-to-cyan line along the bottom of the splash."""

    def __init__(self, color_a, color_b, **kwargs):
        super().__init__(**kwargs)
        self._phase = 0.0
        segments = 24
        with self.canvas:
            self._color_a = Color(*color_a, 0.55)
            self._line_a = Line(width=1.6)
            self._color_b = Color(*color_b, 0.45)
            self._line_b = Line(width=1.6)
        self._segments = segments
        self.bind(size=self._redraw, pos=self._redraw)

    def _wave_points(self, offset_phase, amplitude, y_bias):
        if self.width <= 0:
            return []
        pts = []
        for i in range(self._segments + 1):
            t = i / self._segments
            x = self.x + t * self.width
            y = (self.y + self.height * y_bias
                 + amplitude * math.sin(t * math.pi * 2.2 + self._phase + offset_phase))
            pts.extend([x, y])
        return pts

    def _redraw(self, *_):
        self._line_a.points = self._wave_points(0.0, dp(14), 0.55)
        self._line_b.points = self._wave_points(1.6, dp(10), 0.4)

    def advance(self, dt):
        self._phase += dt * 1.1
        self._redraw()


class _LoadingDots(Widget):
    def __init__(self, accent_main, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(56), dp(10))
        self._t = 0.0
        self._colors = []
        self._dots = []
        with self.canvas:
            for i in range(3):
                c = Color(*accent_main, 0.35)
                d = Ellipse(size=(dp(7), dp(7)))
                self._colors.append(c)
                self._dots.append(d)
        self.bind(pos=self._layout, size=self._layout)

    def _layout(self, *_):
        spacing = self.width / 3
        for i, d in enumerate(self._dots):
            d.pos = (self.x + spacing * i + spacing / 2 - dp(3.5), self.y)

    def advance(self, dt):
        self._t += dt
        for i, c in enumerate(self._colors):
            phase = (self._t * 1.6 - i * 0.28) % 1.0
            c.a = 0.3 + 0.6 * (0.5 + 0.5 * math.sin(phase * math.pi * 2))


class _DotDivider(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color = Color(1, 1, 1, 0.5)
            self._dot = Ellipse(size=(dp(5), dp(5)))
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        self._dot.pos = (cx - dp(2.5), cy - dp(2.5))

    def set_color(self, rgba):
        self._color.rgba = rgba


class SplashScreen(ThemedBehavior, Screen):
    def __init__(self, on_finished=None, **kwargs):
        self._on_finished = on_finished
        self._clock_event = None
        super().__init__(**kwargs)

        root = FloatLayout()
        with root.canvas.before:
            self._bg_color = Color(0.027, 0.039, 0.074, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._sync_bg, size=self._sync_bg)
        self._root = root

        self._starfield = _StarField(size_hint=(1, 1))
        root.add_widget(self._starfield)

        self._badge = _OrbitBadge((0.55, 0.36, 0.96), (0.13, 0.83, 0.93),
                                   pos_hint={"center_x": 0.5, "center_y": 0.62})
        root.add_widget(self._badge)

        self._title_label = Label(text="+2 Cipher", bold=True, font_size=28,
                                   size_hint=(None, None), size=(dp(240), dp(36)),
                                   pos_hint={"center_x": 0.5, "center_y": 0.42})
        root.add_widget(self._title_label)

        self._divider = _DotDivider(
            size_hint=(None, None), size=(dp(20), dp(14)),
            pos_hint={"center_x": 0.5, "center_y": 0.375})
        root.add_widget(self._divider)

        self._subtitle_label = Label(text="Encode (+2)  \u00b7  Decode (-2)", font_size=13,
                                      size_hint=(None, None), size=(dp(280), dp(20)),
                                      pos_hint={"center_x": 0.5, "center_y": 0.345})
        root.add_widget(self._subtitle_label)

        self._wave = _WaveRibbon((0.55, 0.36, 0.96), (0.13, 0.83, 0.93),
                                  size_hint=(1, None), height=dp(90),
                                  pos_hint={"center_x": 0.5, "y": 0.0})
        root.add_widget(self._wave)

        self._dots = _LoadingDots((0.55, 0.36, 0.96),
                                   pos_hint={"center_x": 0.5, "center_y": 0.1})
        root.add_widget(self._dots)

        self._loading_label = Label(text="LOADING...", font_size=10.5,
                                     size_hint=(None, None), size=(dp(120), dp(16)),
                                     pos_hint={"center_x": 0.5, "center_y": 0.065})
        root.add_widget(self._loading_label)

        self._fade_group = [
            self._badge, self._title_label, self._divider, self._subtitle_label,
            self._dots, self._loading_label,
        ]
        for w in self._fade_group:
            w.opacity = 0

        self.add_widget(root)

    def _sync_bg(self, *_):
        self._bg.pos = self._root.pos
        self._bg.size = self._root.size

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background")
        self._title_label.color = self.theme.color("text_primary")
        self._divider.set_color(self.theme.accent("main"))
        self._subtitle_label.color = self.theme.color("text_secondary")
        self._loading_label.color = self.theme.color("text_caption")

    def on_enter(self, *args):
        reduced = self.theme.settings.get("reduced_motion", False) if self.theme else False

        if reduced:
            for w in self._fade_group:
                w.opacity = 1
            Clock.schedule_once(self._finish, 0.6)
            return

        entrance = Animation(opacity=1, duration=_ENTRANCE_DURATION, t="out_cubic")
        for w in self._fade_group:
            entrance.start(w)

        self._clock_event = Clock.schedule_interval(self._advance, 1 / 30)
        Clock.schedule_once(self._finish, _SPLASH_DURATION)

    def _advance(self, dt):
        self._starfield.advance(dt)
        self._badge.advance(dt)
        self._wave.advance(dt)
        self._dots.advance(dt)

    def _finish(self, *_):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        if self._on_finished:
            self._on_finished()
