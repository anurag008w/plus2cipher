"""
ui/screens/splash.py

Plays the native MP4 video splash screen.
"""

from __future__ import annotations

import os

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from ..components.behaviors import ThemedBehavior
from ..asset_paths import PROJECT_ROOT

_ANIM_PATH = os.path.join(PROJECT_ROOT, "assets", "splash_anim.zip")


class SplashScreen(ThemedBehavior, Screen):
    def __init__(self, on_finished=None, **kwargs):
        self._on_finished = on_finished
        super().__init__(**kwargs)

        self._root = FloatLayout()
        with self._root.canvas.before:
            self._bg_color = Color(0.027, 0.039, 0.074, 1)
            self._bg = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._sync_bg, size=self._sync_bg)

        self._anim = None
        if os.path.exists(_ANIM_PATH):
            self._anim = Image(source=_ANIM_PATH, anim_delay=1/24.0, allow_stretch=True, keep_ratio=False)
            self._root.add_widget(self._anim)
        
        self.add_widget(self._root)

    def _sync_bg(self, *_):
        self._bg.pos = self._root.pos
        self._bg.size = self._root.size

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background")

    def on_enter(self, *args):
        if not self._anim:
            Clock.schedule_once(self._finish, 1.0)
        else:
            Clock.schedule_once(self._finish, 5.2)  # Video duration

    def _finish(self, *_):
        if getattr(self, '_finished', False):
            return
        self._finished = True
        if getattr(self, '_anim', None):
            self._anim.anim_delay = -1  # Stop animation
        if getattr(self, '_on_finished', None):
            self._on_finished()
