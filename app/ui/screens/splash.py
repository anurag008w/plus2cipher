"""
ui/screens/splash.py

Plays the native MP4 video splash screen.
"""

from __future__ import annotations

import os

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from ..components.behaviors import ThemedBehavior
from ..asset_paths import PROJECT_ROOT

_VIDEO_PATH = os.path.join(PROJECT_ROOT, "assets", "splash_video.mp4")


class SplashScreen(ThemedBehavior, Screen):
    def __init__(self, on_finished=None, **kwargs):
        self._on_finished = on_finished
        super().__init__(**kwargs)

        self._root = FloatLayout()
        with self._root.canvas.before:
            self._bg_color = Color(0.027, 0.039, 0.074, 1)
            self._bg = Rectangle(pos=self._root.pos, size=self._root.size)
        self._root.bind(pos=self._sync_bg, size=self._sync_bg)

        self._video = None
        if os.path.exists(_VIDEO_PATH):
            self._video = Video(source=_VIDEO_PATH, state='play', options={'eos': 'stop'})
            self._video.bind(eos=self._on_video_eos)
            self._root.add_widget(self._video)
        
        self.add_widget(self._root)

    def _sync_bg(self, *_):
        self._bg.pos = self._root.pos
        self._bg.size = self._root.size

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background")

    def on_enter(self, *args):
        if not self._video:
            # Fallback if video doesn't exist
            Clock.schedule_once(self._finish, 1.0)
        else:
            # Fallback timeout to ensure app starts even if video fails to play/end
            Clock.schedule_once(self._finish, 6.0)

    def _on_video_eos(self, *args):
        self._finish()

    def _finish(self, *_):
        if getattr(self, '_finished', False):
            return
        self._finished = True
        if self._video:
            self._video.state = 'stop'
        if self._on_finished:
            self._on_finished()
