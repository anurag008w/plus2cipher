"""
ui/components/behaviors.py

Small reusable mixins used by almost every component:

- ThemedBehavior: auto-subscribes to the app's ThemeManager.on_change event
  and calls self.apply_theme() whenever theme/accent/density/etc changes, so
  no component ever has to remember to wire this up manually.
- HoverBehavior: desktop mouse hover detection (Android has no concept of
  hover, so this simply never fires there -- touch just goes straight to
  press/release, which is the correct mobile behavior per spec section 46).
"""

from __future__ import annotations

from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.app import App


class ThemedBehavior:
    """Mixin: call self.apply_theme() now and on every future theme change."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.theme = getattr(app, "theme", None)
        if self.theme is not None:
            self.theme.bind(on_change=self._on_theme_changed)
        # Deferred so subclasses finish building their widget tree first.
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: self.apply_theme(), 0)

    def _on_theme_changed(self, *args):
        self.apply_theme()

    def apply_theme(self):
        """Override in subclasses to re-read colors/tokens from self.theme."""
        pass


class HoverBehavior:
    """Mixin adding `hovered` (bool) + `on_enter`/`on_leave` for desktop mice."""

    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self.hovered:
            self.hovered = inside
            if inside:
                self.on_enter()
            else:
                self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass
