# Architecture

## Layering

```
app/core        <- pure Python, zero Kivy imports, fully unit-tested
app/services     <- thin platform wrappers (clipboard, share), safe fallbacks
app/ui           <- everything Kivy: theme, components, layouts, screens
app/main.py      <- wires core + services + ui together into one App
```

`app/core` never imports Kivy. `cipher.py`, `storage.py`, and `settings.py`
can be imported and tested in a plain Python interpreter with no display —
that's deliberate, and it's why `tests/` runs in a few milliseconds with no
Xvfb needed. Every screen and component takes its dependencies (a
`Settings`, a `HistoryStore`, a snackbar callable) as constructor
arguments rather than reaching for globals, so screens are unit-testable
in isolation too, if that's ever useful.

## Theming

`ui/theme/palettes.py` holds raw color values (dark palette, light palette,
7 accent families). `ui/theme/tokens.py` holds spacing/radius/font-size/
duration *functions* that take the current density/radius/font-size
setting and return a number. `ui/theme/manager.py`'s `ThemeManager` ties
these to the live `Settings` object and is a Kivy `EventDispatcher` with a
single `on_change` event.

Every themed widget mixes in `ThemedBehavior` (`ui/components/behaviors.py`),
which does two things in `__init__`: grabs `App.get_running_app().theme`,
and binds `theme.on_change` to the widget's own `apply_theme()` method. So
switching theme/accent/density anywhere calls `theme.dispatch('on_change')`
once, and every visible themed widget re-pulls its colors and tokens. No
widget needs to remember to re-theme itself on every possible setting
change individually.

## Responsive layout

Two independent responsive mechanisms, both driven by `Window.bind(size=...)`:

- **`ui/layouts/responsive.py` (`AppShell`)** switches the whole app chrome
  between a desktop sidebar and a mobile bottom nav at 600dp, by
  *re-parenting* the shared `Header` and `ScreenManager` instances between
  two pre-built container layouts rather than rebuilding them — so screen
  state (typed text, scroll position, etc.) is never lost when you resize
  across the breakpoint.
- **`ui/screens/home.py` (`HomeScreen`)** independently switches its own
  Input/Output card workspace between side-by-side and stacked at the same
  breakpoint, since that's a layout decision specific to Home's content,
  not the app shell.

## A note on `center_x`/`center_y` inside `pos`/`size`-bound callbacks

This bit us once during development and is worth documenting so it doesn't
happen again: `Widget.center_x`/`center_y` are `cache=True` `AliasProperty`s.
Reading them from *inside a callback that is itself bound to that same
widget's `pos` or `size`* can observe a stale cached value, because the
observer ordering between your callback and Kivy's own cache invalidation
isn't guaranteed. Concretely, `ui/screens/splash.py`'s `_OrbitBadge._sync()`
used to do:

```python
def _sync(self, *_):
    cx, cy = self.center_x, self.center_y   # <- unsafe here
```

which intermittently positioned the icon using a stale `center_y` from
*before* the widget had been placed by its parent `FloatLayout`, while
`self.pos` (a plain property, not a cached alias) was already correct. The
fix is to compute center from the raw properties instead, which sidesteps
the cache entirely:

```python
def _sync(self, *_):
    cx = self.x + self.width / 2
    cy = self.y + self.height / 2
```

Every place in this codebase that syncs canvas instructions or child
widgets from within a `pos`/`size`-bound callback on the *same* widget uses
this pattern (`ui/screens/splash.py`, `ui/components/settings_widgets.py`).
If you add a new one, do the same.

## Persistence

- **Settings** (`app/core/settings.py`): one JSON file, written atomically
  (`os.replace` after writing to a `.tmp` file), with a full defaults
  fallback if the file is missing, corrupted, or has an invalid value for
  any individual key.
- **History/Favorites** (`app/core/storage.py`): one SQLite file. A
  corrupted database file is quarantined (renamed to `*.corrupt`) and
  replaced with a fresh one rather than crashing the app on startup.

Both live under `App.user_data_dir`, which Kivy resolves to the correct
OS-appropriate location on both Linux and Android automatically.

## Testing strategy

Two tiers, both run in CI (`.github/workflows/linux.yml`):

1. **`tests/`** — `pytest` unit tests for `app/core` only. Fast, no
   display required. Covers cipher correctness (round-trips, wraparound,
   case/space/symbol preservation), storage (CRUD, search, corruption
   recovery, export/import), and settings (persistence, validation,
   corruption recovery).
2. **`tests_manual/`** — headless end-to-end smoke tests that boot the
   *actual* `Plus2CipherApp` under Xvfb, navigate through every screen, and
   fail loudly (non-zero exit, via a custom Kivy `ExceptionHandler`) if
   anything raises. This is the tier that actually catches UI-layer bugs —
   widget construction errors, layout crashes on resize, theming
   exceptions — since `tests/` deliberately never touches `app/ui` at all.
   `smoke_home.py` is the CI gate; `smoke_splash.py` is a developer
   convenience tool for reviewing splash-screen changes visually and isn't
   wired into CI.

## Icons

The bundled Material Design Icons font that ships inside the `kivymd` pip
package (`kivymd/fonts/materialdesignicons-webfont.ttf`) is used for every
UI icon (`ui/components/icons.py`), so there's a consistent icon system
with no network dependency and no emoji. The actual app icon (the "+2"
badge) lives in `assets/icons/` at several sizes, generated from a single
source image cropped to fill the frame (see `icon_master.png`) so it stays
legible even at the ~24dp sizes used inline in the sidebar and header.
`ui/asset_paths.py` is the single place that resolves paths into that
directory — every screen/component that needs the icon imports
`icon_path()` from there rather than computing its own relative path, since
an off-by-one in a hand-rolled `os.path.dirname()` chain is exactly what
caused the sidebar/header logo to silently fall back to a placeholder
glyph earlier in development.
