"""
ui/components/empty_state.py

Polished, situation-specific empty states (spec section 64). Never a generic
"Nothing here" -- each screen passes its own icon + message.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from .behaviors import ThemedBehavior
from .icons import icon_char, ICON_FONT


class EmptyState(ThemedBehavior, BoxLayout):
    def __init__(self, icon: str, title: str, subtitle: str = "", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.padding = (dp(24), dp(48))

        self._icon_label = Label(text=icon_char(icon), font_name=ICON_FONT, font_size=44,
                                  size_hint_y=None, height=dp(56))
        self._title_label = Label(text=title, bold=True, font_size=15,
                                   size_hint_y=None, height=dp(24))
        self._subtitle_label = Label(text=subtitle, font_size=13,
                                      size_hint_y=None, height=dp(20) if subtitle else 0)
        self.add_widget(self._icon_label)
        self.add_widget(self._title_label)
        if subtitle:
            self.add_widget(self._subtitle_label)

    def apply_theme(self):
        if not self.theme:
            return
        self._icon_label.color = self.theme.color("text_caption")
        self._title_label.color = self.theme.color("text_secondary")
        self._subtitle_label.color = self.theme.color("text_caption")
