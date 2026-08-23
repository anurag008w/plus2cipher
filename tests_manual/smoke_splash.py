"""
tests_manual/smoke_splash.py

Screenshots the actual splash animation at a few points in time, for
visually reviewing changes to ui/screens/splash.py. Not part of the CI
gate (smoke_home.py is) -- this one is a developer convenience tool.

IMPORTANT: app.main must be imported FIRST, before touching kivy.core.window
or any kivy.uix module. app.main sets the desktop window size via
kivy.config.Config at import time; if Kivy's Window singleton gets created
by an earlier import, that Config change arrives too late and the window
silently stays at Kivy's 800x600 default instead.

Run under Xvfb:
    xvfb-run -a --server-args="-screen 0 1280x800x24" python tests_manual/smoke_splash.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("KIVY_NO_ARGS", "1")

from app.main import Plus2CipherApp  # noqa: E402  (must be the first kivy-touching import)
from kivy.clock import Clock  # noqa: E402
from kivy.core.window import Window  # noqa: E402

SHOT_DIR = os.environ.get(
    "PLUS2CIPHER_SMOKE_SCREENSHOTS",
    os.path.join(tempfile.gettempdir(), "plus2cipher-smoke-screenshots"),
)
os.makedirs(SHOT_DIR, exist_ok=True)


class TestApp(Plus2CipherApp):
    def build(self):
        root = super().build()
        for label, t in (("splash_1s", 1.0), ("splash_3s", 3.0), ("splash_end", 4.9), ("post_splash_home", 5.4)):
            Clock.schedule_once(lambda dt, name=label: self._shoot(name), t)
        Clock.schedule_once(lambda dt: self.stop(), 5.8)
        return root

    def _shoot(self, name):
        Window.screenshot(name=os.path.join(SHOT_DIR, f"{name}.png"))


if __name__ == "__main__":
    TestApp().run()
    print(f"Screenshots written to: {SHOT_DIR}")
