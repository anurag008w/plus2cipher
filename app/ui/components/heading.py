"""
ui/components/heading.py

ScreenHeading: the big page title + subtitle row shown at the top of each
screen's content (Home's "Encode / Decode" title, History's "History", ...).
Optionally carries a right-aligned action widget (Home's swap button).
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from .behaviors import ThemedBehavior


class ScreenHeading(ThemedBehavior, BoxLayout):
    def __init__(self, title: str, subtitle: str = "", right_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(52)

        text_box = BoxLayout(orientation="vertical")
        self._title_label = Label(text=title, bold=True, font_size=22, halign="left",
                                   valign="bottom", size_hint_y=None, height=dp(30))
        self._subtitle_label = Label(text=subtitle, font_size=12.5, halign="left",
                                      valign="top", size_hint_y=None, height=dp(18) if subtitle else 0)
        for w in (self._title_label, self._subtitle_label):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        text_box.add_widget(self._title_label)
        if subtitle:
            text_box.add_widget(self._subtitle_label)
        self.add_widget(text_box)

        if right_widget is not None:
            right_wrap = BoxLayout(size_hint_x=None, width=right_widget.width or dp(80))
            right_wrap.add_widget(BoxLayout())
            right_wrap.add_widget(right_widget)
            self.add_widget(right_wrap)

    def apply_theme(self):
        if not self.theme:
            return
        self._title_label.color = self.theme.color("text_primary")
        self._subtitle_label.color = self.theme.color("text_secondary")
