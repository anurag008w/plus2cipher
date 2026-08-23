# +2 Cipher

A small, polished text-shift utility for Linux desktop and Android. It
encodes text by shifting every letter two positions forward through the
alphabet (`a → c`, `z → b`, wrapping around) and decodes by shifting back —
nothing else. Spaces, numbers, punctuation, and case are always preserved.

It's a simple substitution cipher, **not** encryption — see the About
screen in the app for the honest version of that explanation.

## Features

- Encode / Decode with a live-updating output as you type
- Local, offline history and favorites (SQLite) — no account, no network
- Dark and light themes, 7 accent colors, adjustable density/font size/corner radius
- Fully responsive: a desktop sidebar layout above ~1000dp, a mobile bottom-nav
  layout below ~600dp, and everything in between
- Keyboard shortcuts on desktop (`Ctrl/Cmd+Enter` to transform, `Ctrl/Cmd+Shift+C`
  to copy, `Ctrl/Cmd+K` to clear, `Ctrl/Cmd+S` to favorite, and more — see Settings)
- Clipboard + native share sheet integration, with a clipboard fallback on
  desktop where no share sheet exists
- Reduced-motion and high-contrast accessibility options

## Running it

### Linux desktop

```bash
./run.sh
```

First run creates a local virtual environment and installs dependencies;
every run after that just launches the app. To make it double-clickable
from your application menu instead:

```bash
./install-desktop.sh
```

### Android

A debug APK is built automatically by [`.github/workflows/android.yml`](.github/workflows/android.yml)
on every push to `main` — grab it from that workflow run's Artifacts tab.

To build it yourself:

```bash
pip install buildozer==1.5.0 cython==0.29.36
buildozer -v android debug
```

The first Android build downloads and compiles a fair amount of tooling
(the Android SDK/NDK, python-for-android) and can take 20–40 minutes.
Subsequent builds are much faster.

## Project structure

```
app/
  core/          cipher engine, SQLite storage, JSON settings — zero Kivy
                 imports, fully unit-testable on their own (see tests/)
  services/      clipboard + share, each with a safe, non-crashing fallback
  ui/
    theme/       design tokens + color palettes + the live ThemeManager
    components/  the reusable widget library (buttons, cards, nav, ...)
    layouts/     AppShell — the responsive desktop/mobile switcher
    screens/     Splash, Home, History, Favorites, Settings, About
  main.py        wires everything together
main.py           thin root-level entry point (see ARCHITECTURE.md)
tests/            pytest unit tests for app/core (no display required)
tests_manual/     headless end-to-end smoke tests that boot the real UI
                  under Xvfb (see ARCHITECTURE.md)
assets/icons/     app icon at several sizes
buildozer.spec    Android packaging config
```

More detail on how the pieces fit together is in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

That covers the cipher engine, storage layer, and settings persistence —
36 tests, no display needed. For a fuller check that actually renders every
screen (this is what caught the real layout bugs during development):

```bash
sudo apt-get install -y xvfb xclip   # once
xvfb-run -a --server-args="-screen 0 1280x800x24" python tests_manual/smoke_home.py
```

Both run automatically in CI on every push (see `.github/workflows/linux.yml`).

## License

No license file has been added yet — add one before treating this as
open source in practice.
