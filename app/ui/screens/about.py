"""
ui/screens/about.py

Spec sections 36-37, 42, 62. Plain description of what the tool does, a
worked mapping-table example, changelog, and links. Explicitly distinguishes
this from real encryption (section 62) rather than overstating what a
simple shift cipher provides.
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.metrics import dp
import os
import webbrowser

from ..components.behaviors import ThemedBehavior
from ..components.heading import ScreenHeading
from ..components.cards import Card
from ..components.icons import icon_char, ICON_FONT
from ..asset_paths import icon_path
from ...core.cipher import preview_mapping

def _read_version() -> str:
    """Read version from buildozer.spec so it never needs to be manually updated."""
    try:
        import os
        spec_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "buildozer.spec")
        spec_path = os.path.abspath(spec_path)
        with open(spec_path) as f:
            for line in f:
                if line.startswith("version"):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "1.0.0"


def _read_changelog() -> str:
    """Read and format changelog from CHANGELOG.md automatically."""
    try:
        import os
        cl_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "CHANGELOG.md")
        cl_path = os.path.abspath(cl_path)
        with open(cl_path) as f:
            lines = f.readlines()
        sections = []
        current = []
        for line in lines:
            line = line.rstrip()
            if line.startswith("## "):
                if current:
                    sections.append("\n".join(current))
                    current = []
                current.append(line[3:])  # version heading e.g. "1.1.0"
            elif line.startswith("- ") and current:
                current.append("  • " + line[2:])
        if current:
            sections.append("\n".join(current))
        return "\n\n".join(sections)
    except Exception:
        return f"{APP_VERSION} — See CHANGELOG.md for details."


APP_VERSION = _read_version()


_ICON_PATH = icon_path("icon_96.png")


class _InfoSection(Card):
    def __init__(self, title: str, body: str, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self._title_label = Label(text=title, bold=True, font_size=15, halign="left",
                                   size_hint_y=None, height=dp(24))
        self._body_label = Label(text=body, font_size=13, halign="left", valign="top",
                                  size_hint_y=None)
        self._title_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self._body_label.bind(width=lambda w, *_: setattr(w, "text_size", (w.width, None)))
        self._body_label.bind(texture_size=lambda w, *_: setattr(w, "height", w.texture_size[1]))
        self.add_widget(self._title_label)
        self.add_widget(self._body_label)
        self.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))

    def apply_theme(self):
        super().apply_theme()
        if self.theme:
            self._title_label.color = self.theme.color("text_primary")
            self._body_label.color = self.theme.color("text_secondary")


from kivy.uix.behaviors import ButtonBehavior
class _LinkRow(ButtonBehavior, Card):
    def __init__(self, icon: str, title: str, subtitle: str, on_press=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(56)

        from kivy.uix.behaviors import ButtonBehavior
        from kivy.uix.widget import Widget

        self._icon_label = Label(text=icon_char(icon), font_name=ICON_FONT, font_size=20,
                                  size_hint_x=None, width=dp(30))
        text_box = BoxLayout(orientation="vertical")
        self._title_label = Label(text=title, font_size=14, halign="left", valign="bottom",
                                   size_hint_y=None, height=dp(20))
        self._subtitle_label = Label(text=subtitle, font_size=11.5, halign="left", valign="top",
                                      size_hint_y=None, height=dp(16))
        for w in (self._title_label, self._subtitle_label):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        text_box.add_widget(self._title_label)
        text_box.add_widget(self._subtitle_label)
        self._chevron = Label(text=icon_char("chevron_right"), font_name=ICON_FONT, font_size=16,
                               size_hint_x=None, width=dp(20))
        if on_press:
            self.bind(on_release=on_press)

        self.add_widget(self._icon_label)
        self.add_widget(text_box)
        self.add_widget(self._chevron)

    def apply_theme(self):
        super().apply_theme()
        if self.theme:
            self._icon_label.color = self.theme.accent("main")
            self._title_label.color = self.theme.color("text_primary")
            self._subtitle_label.color = self.theme.color("text_caption")
            self._chevron.color = self.theme.color("text_caption")


class AboutScreen(ThemedBehavior, Screen):
    def __init__(self, snackbar, **kwargs):
        self.snackbar = snackbar
        super().__init__(**kwargs)
        self.name = "about"

        outer = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))
        outer.size_hint_y = None
        outer.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))

        outer.add_widget(ScreenHeading(title="About", subtitle="What +2 Cipher is, and how it works"))

        hero = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(14))
        if os.path.exists(_ICON_PATH):
            hero.add_widget(Image(source=_ICON_PATH, size_hint=(None, None), size=(dp(64), dp(64)),
                                   allow_stretch=True, keep_ratio=True))
        hero_text = BoxLayout(orientation="vertical")
        self._hero_title = Label(text="+2 Cipher", bold=True, font_size=20, halign="left",
                                  size_hint_y=None, height=dp(28))
        self._hero_version = Label(text=f"Version {APP_VERSION}", font_size=12, halign="left",
                                    size_hint_y=None, height=dp(18))
        for w in (self._hero_title, self._hero_version):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        hero_text.add_widget(self._hero_title)
        hero_text.add_widget(self._hero_version)
        hero.add_widget(hero_text)
        outer.add_widget(hero)

        outer.add_widget(_InfoSection(
            "What is +2 Cipher?",
            "A lightweight text transformation tool using a +2 / -2 alphabet shift. "
            "It's a simple substitution/shift utility, not strong cryptography — don't use it "
            "anywhere real confidentiality or security matters.",
        ))

        outer.add_widget(_InfoSection(
            "How it works",
            "Encoding shifts each alphabetic character two positions forward through the "
            "alphabet, wrapping from Z back to A. Decoding shifts each alphabetic character "
            "two positions backward. Spaces, numbers, punctuation, and symbols are left exactly "
            "as they are, and case is preserved.",
        ))

        outer.add_widget(self._build_mapping_table())

        outer.add_widget(_InfoSection(
            "Changelog",
            _read_changelog(),
        ))

        outer.add_widget(_LinkRow("github", "GitHub Repository", "View or contribute to the source", on_press=lambda *a: webbrowser.open("https://github.com/anurag008w/plus2cipher")))
        outer.add_widget(_LinkRow("share", "Support / Feedback", "Report an issue or suggest an idea", on_press=lambda *a: webbrowser.open("https://github.com/anurag008w/plus2cipher/issues")))
        outer.add_widget(_LinkRow("check", "Licenses", "Open-source components used by this app", on_press=lambda *a: webbrowser.open("https://kivy.org")))

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(outer)
        self.add_widget(scroll)

    def _build_mapping_table(self):
        card = Card()
        card.size_hint_y = None
        title = Label(text="Mapping example (a -> c, ... z -> b)", bold=True, font_size=13,
                       halign="left", size_hint_y=None, height=dp(22))
        title.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        card.add_widget(title)

        grid = GridLayout(cols=13, size_hint_y=None, spacing=dp(4))
        grid.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        self._mapping_labels = []
        for original, shifted in preview_mapping(2):
            lbl = Label(text=f"{original}->{shifted}", font_size=11.5,
                        size_hint_y=None, height=dp(22))
            self._mapping_labels.append(lbl)
            grid.add_widget(lbl)
        card.add_widget(grid)
        card.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        self._mapping_card = card
        self._mapping_title = title
        return card

    def apply_theme(self):
        if not self.theme:
            return
        self._hero_title.color = self.theme.color("text_primary")
        self._hero_version.color = self.theme.color("text_caption")
        if hasattr(self, "_mapping_title"):
            self._mapping_title.color = self.theme.color("text_primary")
        for lbl in getattr(self, "_mapping_labels", []):
            lbl.color = self.theme.color("text_secondary")
