"""
tests_manual/smoke_home.py

A headless, end-to-end smoke test: boots the *actual* app (not a mock),
skips the splash, visits every screen, types a sample conversion, and
screenshots each step. Unlike the unit tests in tests/ (which only cover
framework-independent core/ logic), this is what actually catches UI-layer
bugs -- widget construction errors, layout crashes, theming issues.

Requires a display. Run under Xvfb:
    xvfb-run -a --server-args="-screen 0 1280x800x24" python tests_manual/smoke_home.py

Exits non-zero if any exception occurs anywhere in the app during the run,
so this is safe to use as a CI gate (see .github/workflows/linux.yml).
"""

import os
import sys
import tempfile
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.clock import Clock  # noqa: E402
from kivy.base import ExceptionManager, ExceptionHandler  # noqa: E402
from app.main import Plus2CipherApp  # noqa: E402

SHOT_DIR = os.environ.get(
    "PLUS2CIPHER_SMOKE_SCREENSHOTS",
    os.path.join(tempfile.gettempdir(), "plus2cipher-smoke-screenshots"),
)
os.makedirs(SHOT_DIR, exist_ok=True)

_failure = {"exc": None}


class _FailFastHandler(ExceptionHandler):
    """Turns any exception raised inside Kivy's event loop into a hard,
    process-exiting failure instead of a silently-logged-and-continue.
    """

    def handle_exception(self, exception):
        _failure["exc"] = exception
        traceback.print_exception(type(exception), exception, exception.__traceback__)
        return ExceptionManager.RAISE


ExceptionManager.add_handler(_FailFastHandler())


class TestApp(Plus2CipherApp):
    def build(self):
        root = super().build()
        # Skip the ~5s splash animation for this smoke test -- jump to Home.
        Clock.schedule_once(lambda dt: self._on_splash_finished(), 0.3)
        Clock.schedule_once(lambda dt: self._shoot("home"), 1.0)
        Clock.schedule_once(lambda dt: self._type_and_shoot(), 1.6)
        Clock.schedule_once(lambda dt: self._go("history"), 2.6)
        Clock.schedule_once(lambda dt: self._go("favorites"), 3.2)
        Clock.schedule_once(lambda dt: self._go("settings"), 3.8)
        Clock.schedule_once(lambda dt: self._go("about"), 4.4)
        Clock.schedule_once(lambda dt: self.stop(), 5.2)
        return root

    def _shoot(self, name):
        from kivy.core.window import Window
        import shutil
        target = os.path.join(SHOT_DIR, f"{name}.png")
        filename = Window.screenshot(name=target)
        if filename and os.path.exists(filename) and filename != target:
            shutil.move(filename, target)

    def _type_and_shoot(self):
        self.home_screen.input_card.text_input.text = "Hello, World! 123"
        Clock.schedule_once(lambda dt: self._shoot("home_typed"), 0.3)

    def _go(self, route):
        self._navigate(route)
        Clock.schedule_once(lambda dt: self._shoot(route), 0.3)


if __name__ == "__main__":
    TestApp().run()
    if _failure["exc"] is not None:
        print(f"\nSMOKE TEST FAILED: {_failure['exc']!r}", file=sys.stderr)
        sys.exit(1)
    print(f"\nSmoke test passed. Screenshots written to: {SHOT_DIR}")
