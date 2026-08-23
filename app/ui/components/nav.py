"""
ui/components/nav.py

Sidebar       - desktop vertical navigation (spec section 12).
BottomNav     - mobile bottom navigation, max 4 tabs; About lives inside
                Settings on mobile (spec section 13).
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
import os

from .behaviors import ThemedBehavior, HoverBehavior
from .icons import icon_char, ICON_FONT
from ..asset_paths import icon_path
from kivy.uix.behaviors import ButtonBehavior

_ICON_PATH = icon_path("icon_64.png")


class _NavItemBase(ThemedBehavior, HoverBehavior, ButtonBehavior, BoxLayout):
    route = StringProperty("")
    label_text = StringProperty("")
    icon_active = StringProperty("")
    icon_inactive = StringProperty("")

    def __init__(self, on_select=None, **kwargs):
        self._active = False
        self._on_select = on_select
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)
        self.bind(hovered=lambda *a: self._refresh())
        self.bind(on_release=lambda *a: self._on_select(self.route) if self._on_select else None)

    def set_active(self, active: bool):
        self._active = active
        self._refresh()

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.theme.radius("control") if self.theme else 10]

    def _refresh(self):
        raise NotImplementedError

    def apply_theme(self):
        self._refresh()


class SidebarItem(_NavItemBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = (dp(14), 0)
        self.spacing = dp(12)
        self._icon_label = Label(text="", font_name=ICON_FONT, font_size=19,
                                  size_hint_x=None, width=dp(24))
        self._text_label = Label(text=self.label_text, font_size=14, halign="left", valign="middle")
        self._text_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.add_widget(self._icon_label)
        self.add_widget(self._text_label)

    def _refresh(self):
        if not self.theme:
            return
        icon_name = self.icon_active if self._active else self.icon_inactive
        self._icon_label.text = icon_char(icon_name)
        if self._active:
            self._bg_color.rgba = self.theme.accent("soft")
            color = self.theme.accent("main")
        elif self.hovered:
            self._bg_color.rgba = self.theme.color("surface_hover")
            color = self.theme.color("text_primary")
        else:
            self._bg_color.rgba = (0, 0, 0, 0)
            color = self.theme.color("text_secondary")
        self._icon_label.color = color
        self._text_label.color = color


class Sidebar(ThemedBehavior, BoxLayout):
    ROUTES = [
        ("home", "Home", "home_active", "home"),
        ("history", "History", "history", "history"),
        ("favorites", "Favorites", "favorites_active", "favorites"),
        ("settings", "Settings", "settings_active", "settings"),
        ("about", "About", "about", "about"),
    ]

    def __init__(self, on_navigate=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_x = None
        self.width = dp(220)
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
            self._border_color = Color(0, 0, 0, 0)
            self._border_line = Line(points=[])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        header = BoxLayout(size_hint_y=None, height=dp(56), padding=(dp(16), 0), spacing=dp(10))
        if os.path.exists(_ICON_PATH):
            self._logo_label = Image(source=_ICON_PATH, size_hint=(None, None), size=(dp(28), dp(28)),
                                      allow_stretch=True, keep_ratio=True)
        else:
            self._logo_label = Label(text=icon_char("logo"), font_name=ICON_FONT, font_size=22,
                                      size_hint_x=None, width=dp(28))
        self._title_label = Label(text="+2 Cipher", bold=True, font_size=16, halign="left")
        self._title_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        header.add_widget(self._logo_label)
        header.add_widget(self._title_label)
        self.add_widget(header)

        nav_container = BoxLayout(orientation="vertical", spacing=dp(2),
                                   padding=(dp(8), dp(8)), size_hint_y=None)
        nav_container.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        self._items = {}
        for route, label, icon_a, icon_i in self.ROUTES:
            item = SidebarItem(route=route, label_text=label, icon_active=icon_a,
                                icon_inactive=icon_i, on_select=on_navigate)
            self._items[route] = item
            nav_container.add_widget(item)
        self.add_widget(nav_container)
        self.add_widget(BoxLayout())  # spacer pushes nav to the top

    def set_active(self, route: str):
        for r, item in self._items.items():
            item.set_active(r == route)

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border_line.points = [
            self.right, self.y, self.right, self.top,
        ]

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background_secondary")
        self._border_color.rgba = self.theme.color("border")
        if isinstance(self._logo_label, Label):
            self._logo_label.color = self.theme.accent("main")
        self._title_label.color = self.theme.color("text_primary")
        self._sync_bg()


class BottomNavItem(_NavItemBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._icon_label = Label(text="", font_name=ICON_FONT, font_size=20,
                                  size_hint_y=None, height=dp(24))
        self._text_label = Label(text=self.label_text, font_size=10.5,
                                  size_hint_y=None, height=dp(14))
        self.add_widget(self._icon_label)
        self.add_widget(self._text_label)

    def _refresh(self):
        if not self.theme:
            return
        icon_name = self.icon_active if self._active else self.icon_inactive
        self._icon_label.text = icon_char(icon_name)
        color = self.theme.accent("main") if self._active else self.theme.color("text_caption")
        self._icon_label.color = color
        self._text_label.color = color
        self._bg_color.rgba = (0, 0, 0, 0)


class BottomNav(ThemedBehavior, BoxLayout):
    ROUTES = [
        ("home", "Home", "home_active", "home"),
        ("history", "History", "history", "history"),
        ("favorites", "Favorites", "favorites_active", "favorites"),
        ("settings", "Settings", "settings_active", "settings"),
    ]

    def __init__(self, on_navigate=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(64)
        self.padding = (dp(4), dp(6))
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
            self._border_color = Color(0, 0, 0, 0)
            self._top_border = Line(points=[])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        self._items = {}
        for route, label, icon_a, icon_i in self.ROUTES:
            item = BottomNavItem(route=route, label_text=label, icon_active=icon_a,
                                  icon_inactive=icon_i, on_select=on_navigate)
            self._items[route] = item
            self.add_widget(item)

    def set_active(self, route: str):
        # "about" is reached via Settings on mobile, so it maps onto no tab.
        for r, item in self._items.items():
            item.set_active(r == route)

    def _sync_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._top_border.points = [self.x, self.top, self.right, self.top]

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("background_secondary")
        self._border_color.rgba = self.theme.color("border")
        self._sync_bg()
