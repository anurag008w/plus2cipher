"""
app/main.py

+2 Cipher entry point. Wires together:
  Settings (JSON) + HistoryStore (SQLite) + ThemeManager
  -> ScreenManager (Splash, Home, History, Favorites, Settings, About)
  -> AppShell (desktop sidebar <-> mobile bottom nav, responsive)
  -> SnackbarHost (toast feedback, floats above everything)

Run directly: `python3 -m app.main` from the project root, or via run.sh.
"""

from __future__ import annotations

import os
import sys

# Allow running as `python3 app/main.py` as well as `python3 -m app.main`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy.config import Config

Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "800")
Config.set("input", "mouse", "mouse,multitouch_on_demand")  # avoid the red dot on right-click (desktop)

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, NoTransition, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock

from app.core.settings import Settings
from app.core.storage import HistoryStore
from app.ui.theme.manager import ThemeManager
from app.ui.theme import palettes
from app.ui.components.snackbar import SnackbarHost

import kivy.metrics
from kivy.uix.label import Label

original_dp = kivy.metrics.dp
original_sp = kivy.metrics.sp
_app_settings_proxy = {"density": "Comfortable", "font_size": "Medium"}

def dp_patched(val):
    if isinstance(val, str) and val.endswith('dp'):
        val = float(val[:-2])
    d = _app_settings_proxy.get("density", "Comfortable")
    scale = 0.85 if d == "Compact" else (1.2 if d == "Spacious" else 1.0)
    return original_dp(val * scale)

kivy.metrics.dp = dp_patched

original_label_init = Label.__init__
def label_patched_init(self, **kwargs):
    fs_str = _app_settings_proxy.get("font_size", "Medium")
    scale = 0.85 if fs_str == "Small" else (1.2 if fs_str == "Large" else 1.0)
    if "font_size" in kwargs:
        val = kwargs["font_size"]
        if isinstance(val, (int, float)):
            kwargs["font_size"] = original_sp(val * scale)
    original_label_init(self, **kwargs)

Label.__init__ = label_patched_init

from kivy.uix.textinput import TextInput
original_ti_init = TextInput.__init__
def ti_patched_init(self, **kwargs):
    fs_str = _app_settings_proxy.get("font_size", "Medium")
    scale = 0.85 if fs_str == "Small" else (1.2 if fs_str == "Large" else 1.0)
    val = kwargs.get("font_size", 15)  # default is 15
    if isinstance(val, (int, float)):
        kwargs["font_size"] = original_sp(val * scale)
    original_ti_init(self, **kwargs)

TextInput.__init__ = ti_patched_init

original_ti_touch_down = TextInput.on_touch_down
def ti_patched_touch_down(self, touch):
    if self.collide_point(*touch.pos):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._show_keyboard(), 0.1)
    return original_ti_touch_down(self, touch)
TextInput.on_touch_down = ti_patched_touch_down



from app.ui.layouts.responsive import AppShell
from app.ui.screens.splash import SplashScreen
from app.ui.screens.home import HomeScreen
from app.ui.screens.history import HistoryScreen
from app.ui.screens.favorites import FavoritesScreen
from app.ui.screens.settings import SettingsScreen
from app.ui.screens.about import AboutScreen
from app.services import clipboard as clipboard_service
from app.services import sharing as sharing_service

APP_DATA_DIRNAME = ".plus2cipher"


class Plus2CipherApp(App):
    title = "+2 Cipher"

    def build(self):
        from kivy.core.window import Window
        Window.softinput_mode = "pan"
        data_dir = self._resolve_data_dir()
        self.settings = Settings.load(os.path.join(data_dir, "settings.json"))

        global _app_settings_proxy
        _app_settings_proxy["density"] = self.settings.get("density")
        _app_settings_proxy["font_size"] = self.settings.get("font_size")

        self.history_store = HistoryStore(os.path.join(data_dir, "history.db"))
        self.theme = ThemeManager(self.settings)

        self._set_window_background()
        self.theme.bind(on_change=lambda *a: self._set_window_background())

        try:
            from app.ui.asset_paths import icon_path

            icon_file = icon_path("icon_512.png")
            if os.path.exists(icon_file):
                Window.set_icon(icon_file)
        except Exception:
            pass

        self.screen_manager = ScreenManager(
            transition=NoTransition() if self.settings.get("reduced_motion") else FadeTransition(duration=0.12)
        )

        self.splash_screen = SplashScreen(on_finished=self._on_splash_finished, name="splash")
        self.home_screen = HomeScreen(
            settings=self.settings, history_store=self.history_store, snackbar=self._snackbar_proxy(),
            share_fn=lambda text: sharing_service.share_text(text), clipboard_fn=clipboard_service,
            name="home",
        )
        self.history_screen = HistoryScreen(
            settings=self.settings, history_store=self.history_store, snackbar=self._snackbar_proxy(),
            clipboard_fn=clipboard_service, on_reuse=self._reuse_record, name="history",
        )
        self.favorites_screen = FavoritesScreen(
            settings=self.settings, history_store=self.history_store, snackbar=self._snackbar_proxy(),
            clipboard_fn=clipboard_service, on_reuse=self._reuse_record, name="favorites",
        )
        self.settings_screen = SettingsScreen(
            settings=self.settings, history_store=self.history_store, snackbar=self._snackbar_proxy(),
            on_apply_char_limit=self.home_screen.apply_char_limit,
            on_apply_live_transform=self.home_screen.set_live_transformation,
            name="settings",
        )
        self.settings_screen.theme_ref = self.theme
        self.about_screen = AboutScreen(snackbar=self._snackbar_proxy(), name="about")

        # NOTE: splash_screen is intentionally NOT added to screen_manager.
        # It's a full-screen overlay shown before the sidebar/header chrome
        # exists on screen at all -- adding it as a normal Screen here would
        # nest it inside AppShell and squeeze it into the content area next
        # to the sidebar, instead of covering the whole window.
        for screen in (
            self.home_screen, self.history_screen,
            self.favorites_screen, self.settings_screen, self.about_screen,
        ):
            self.screen_manager.add_widget(screen)
        self.screen_manager.current = "home"

        self.home_screen.set_live_transformation(self.settings.live_transformation)

        self.app_shell = AppShell(
            screen_manager=self.screen_manager,
            on_navigate=self._navigate,
            on_toggle_theme=self._toggle_theme,
        )
        self.app_shell.set_active_route("home")

        self.snackbar_host = SnackbarHost()

        root = FloatLayout()
        root.add_widget(self.app_shell)
        root.add_widget(self.snackbar_host)
        root.add_widget(self.splash_screen)  # added last -> painted on top, covers everything
        self._root = root

        Window.bind(on_key_down=self._on_key_down)
        Clock.schedule_interval(lambda dt: self.settings.save(), 8.0)  # periodic autosave of last_text etc.
        Clock.schedule_once(lambda dt: self.splash_screen.on_enter(), 0)

        return root

    # -- setup helpers -----------------------------------------------------------------

    def _resolve_data_dir(self) -> str:
        try:
            base = self.user_data_dir  # Kivy resolves the right OS-appropriate path, incl. Android
        except Exception:
            base = os.path.join(os.path.expanduser("~"), APP_DATA_DIRNAME)
        os.makedirs(base, exist_ok=True)
        return base

    def _set_window_background(self):
        try:
            Window.clearcolor = self.theme.color("background")
        except Exception:
            pass

    def _snackbar_proxy(self):
        """Screens are constructed before snackbar_host exists; proxy defers the call."""

        class _Proxy:
            def show(_self, message, kind="info"):
                if getattr(self, "snackbar_host", None):
                    self.snackbar_host.show(message, kind=kind)

        return _Proxy()

    # -- navigation ----------------------------------------------------------------------

    def _on_splash_finished(self):
        if self.splash_screen.parent:
            self._root.remove_widget(self.splash_screen)

    def _navigate(self, route: str):
        self.screen_manager.current = route
        self.app_shell.set_active_route(route)

    def _toggle_theme(self):
        self.theme.set_theme("light" if self.theme.settings.theme == "dark" else "dark")

    def _reuse_record(self, record):
        self.home_screen.input_card.text_input.text = record.output_text
        self.home_screen.segmented.select("decode" if record.mode == "encode" else "encode")
        self._navigate("home")

    # -- keyboard shortcuts (desktop) -----------------------------------------------------

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        ctrl_or_cmd = "ctrl" in modifiers or "meta" in modifiers
        if not ctrl_or_cmd or self.screen_manager.current != "home":
            return False
        home = self.home_screen
        if key in (13, 271) and not modifiers.__contains__("shift"):  # Enter / numpad Enter
            home._transform()
            return True
        if codepoint == "c" and "shift" in modifiers:
            home._on_copy()
            return True
        if codepoint == "v" and "shift" in modifiers:
            home._on_paste()
            return True
        if codepoint == "k":
            home._on_clear()
            return True
        if codepoint == "s":
            home._on_toggle_favorite()
            return True
        return False

    def on_stop(self):
        try:
            self.settings.save()
        except Exception:
            pass

    def on_pause(self):
        try:
            self.settings.save()
        except Exception:
            pass
        return True


def main():
    Plus2CipherApp().run()


if __name__ == "__main__":
    main()
