"""
ui/layouts/responsive.py

AppShell is the single top-level container. It owns one Header, one
ScreenManager, one Sidebar and one BottomNav, and re-parents the Header +
ScreenManager between a desktop arrangement (sidebar left, content right)
and a mobile arrangement (header top, content middle, bottom nav bottom) as
the window crosses the breakpoints defined in ui/theme/tokens.py.

Re-parenting (rather than rebuilding) the Header/ScreenManager means screen
state is never lost when the layout class changes (spec section 4/8).
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.metrics import dp

from ..components.behaviors import ThemedBehavior
from ..components.nav import Sidebar, BottomNav
from ..components.header import Header
from ..theme.tokens import layout_class


class AppShell(ThemedBehavior, FloatLayout):
    def __init__(self, screen_manager, on_navigate, on_toggle_theme, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.header = Header(on_toggle_theme=on_toggle_theme)
        self.sidebar = Sidebar(on_navigate=on_navigate)
        self.bottom_nav = BottomNav(on_navigate=on_navigate)

        self._desktop_root = BoxLayout(orientation="horizontal")
        self._mobile_root = BoxLayout(orientation="vertical")
        self._content_column = BoxLayout(orientation="vertical")

        self._current_layout = None
        self.add_widget(self._desktop_root)  # placeholder; replaced immediately below
        self.remove_widget(self._desktop_root)

        self._active_route = "home"
        Window.bind(size=self._on_resize)
        self._on_resize(Window, Window.size)

    def set_active_route(self, route: str):
        self._active_route = route
        self.sidebar.set_active(route)
        self.bottom_nav.set_active(route)

    def _on_resize(self, window, size):
        # Convert physical pixels to density-independent pixels (dp)
        # On Android, physical width can easily exceed 1000px, but dp width is smaller.
        width_dp = size[0] / dp(1)
        cls = layout_class(width_dp)
        is_mobile = cls == "mobile"
        target = "mobile" if is_mobile else "desktop"
        if target == self._current_layout:
            return
        self._current_layout = target
        self._rebuild(target)

    def _rebuild(self, target: str):
        # Detach shared widgets from wherever they currently live.
        for widget in (self.header, self.screen_manager):
            if widget.parent:
                widget.parent.remove_widget(widget)
        for container in (self._desktop_root, self._mobile_root, self._content_column):
            container.clear_widgets()
        self.clear_widgets()

        self.header.set_compact(target == "mobile")

        if target == "desktop":
            self._content_column.add_widget(self.header)
            self._content_column.add_widget(self.screen_manager)
            self._desktop_root.add_widget(self.sidebar)
            self._desktop_root.add_widget(self._content_column)
            self.add_widget(self._desktop_root)
        else:
            self._mobile_root.add_widget(self.header)
            self._mobile_root.add_widget(self.screen_manager)
            self._mobile_root.add_widget(self.bottom_nav)
            self.add_widget(self._mobile_root)

        self.sidebar.set_active(self._active_route)
        self.bottom_nav.set_active(self._active_route)

    def apply_theme(self):
        pass
