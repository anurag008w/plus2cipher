"""
ui/components/cards.py

Card, InputCard, OutputCard, StatCard, HistoryCard, FavoriteCard.

These are the workhorse surfaces of the Home/History/Favorites screens.
Every card redraws itself on theme change (dark/light, accent, radius,
density) via ThemedBehavior.
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.metrics import dp

from .behaviors import ThemedBehavior
from .buttons import IconButton, SecondaryButton, PrimaryButton, ActiveIconButton
from .icons import icon_char, ICON_FONT


class Card(ThemedBehavior, BoxLayout):
    """Base rounded, bordered surface. `elevated=True` uses the lighter card tone."""

    elevated = BooleanProperty(False)
    focused_look = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
            self._border_color = Color(0, 0, 0, 0)
            self._border = Line(width=1)
        self.bind(pos=self._sync, size=self._sync)
        self.bind(focused_look=lambda *a: self.apply_theme())

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        r = self.theme.radius("card") if self.theme else 14
        self._bg.radius = [r]
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, r)

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("card_elevated" if self.elevated else "card")
        if self.focused_look:
            self._border_color.rgba = self.theme.accent("main")
            self._border.width = 1.6
        else:
            self._border_color.rgba = self.theme.color("border")
            self._border.width = 1
        self._sync()
        pad = self.theme.spacing("md")
        self.padding = (pad, pad)
        self.spacing = self.theme.spacing("sm")


class EyebrowRow(ThemedBehavior, BoxLayout):
    """The 'INPUT  58 / 5000' title row shown atop input/output cards."""

    title = StringProperty("")
    counter_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(32)
        self._title_label = Label(
            text=self.title, bold=True, halign="left", valign="middle", font_size=12
        )
        self._title_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self._counter_label = Label(
            text=self.counter_text, halign="right", valign="middle", font_size=12,
            size_hint_x=None, width=dp(90),
        )
        self._counter_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self.add_widget(self._title_label)
        self.add_widget(self._counter_label)
        self.bind(title=lambda *a: setattr(self._title_label, "text", self.title))
        self.bind(counter_text=lambda *a: setattr(self._counter_label, "text", self.counter_text))

    def apply_theme(self):
        if not self.theme:
            return
        self._title_label.color = self.theme.color("text_secondary")
        self._counter_label.color = self.theme.color("text_caption")


class ActionRow(ThemedBehavior, BoxLayout):
    """A horizontal row of secondary buttons under a card's text area."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(8)

    def apply_theme(self):
        if self.theme:
            self.spacing = self.theme.spacing("sm")


class InputCard(Card):
    """Left card on desktop / top card on mobile: where the user types text."""

    def __init__(self, char_limit=5000, on_text_change=None, on_paste=None, on_clear=None,
                 on_transform=None, **kwargs):
        self._char_limit = char_limit
        self._on_text_change = on_text_change
        super().__init__(**kwargs)
        self.eyebrow = EyebrowRow(title="INPUT", counter_text=f"0 / {char_limit}")
        self.add_widget(self.eyebrow)

        self.text_input = TextInput(
            hint_text="Type or paste your text here...",
            multiline=True,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            font_size=15,
            padding=(dp(4), dp(8)),
        )
        self.text_input.bind(text=self._on_text_changed)
        self.text_input.bind(focus=self._on_focus_changed)
        self.add_widget(self.text_input)

        actions = ActionRow()
        self.paste_btn = SecondaryButton(text="Paste", icon="paste")
        self.clear_btn = SecondaryButton(text="Clear", icon="clear")
        if on_paste:
            self.paste_btn.bind(on_release=lambda *a: on_paste())
        if on_clear:
            self.clear_btn.bind(on_release=lambda *a: on_clear())
        actions.add_widget(self.paste_btn)
        actions.add_widget(self.clear_btn)

        # Only shown when Live Transformation is OFF (spec section 20).
        self.transform_btn = PrimaryButton(text="Transform", icon="swap")
        self.transform_btn.size_hint_x = None
        self.transform_btn.width = 0
        self.transform_btn.opacity = 0
        self.transform_btn.disabled = True
        if on_transform:
            self.transform_btn.bind(on_release=lambda *a: on_transform())
        actions.add_widget(self.transform_btn)

        self.add_widget(actions)

    def set_live_mode(self, is_live: bool):
        self.transform_btn.disabled = is_live
        self.transform_btn.opacity = 0 if is_live else 1
        self.transform_btn.width = 0 if is_live else dp(120)

    def set_char_limit(self, limit: int):
        self._char_limit = limit
        self._update_counter()

    def _on_text_changed(self, _widget, text):
        if len(text) > self._char_limit:
            self.text_input.text = text[: self._char_limit]
            return  # bound again via this same handler with the truncated text
        self._update_counter()
        if self._on_text_change:
            self._on_text_change(text)

    def _update_counter(self):
        length = len(self.text_input.text)
        over = length >= self._char_limit
        self.eyebrow.counter_text = f"{length} / {self._char_limit}"
        if self.theme:
            self.eyebrow._counter_label.color = (
                self.theme.color("warning") if over else self.theme.color("text_caption")
            )

    def _on_focus_changed(self, _widget, focused):
        self.focused_look = focused

    def apply_theme(self):
        super().apply_theme()
        if self.theme:
            self.text_input.hint_text_color = self.theme.color("text_caption")
            self.text_input.foreground_color = self.theme.color("text_primary")
            self.text_input.cursor_color = self.theme.accent("main")
            self.text_input.selection_color = self.theme.accent("soft")
            self._update_counter()


class OutputCard(Card):
    """Right card on desktop / bottom card on mobile: read-only transformed text."""

    def __init__(self, char_limit=5000, on_copy=None, on_share=None, on_favorite=None, **kwargs):
        self._char_limit = char_limit
        super().__init__(**kwargs)
        self.eyebrow = EyebrowRow(title="OUTPUT", counter_text=f"0 / {char_limit}")
        self.add_widget(self.eyebrow)

        self.text_input = TextInput(
            hint_text="Your transformed text will appear here",
            multiline=True,
            readonly=True,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0, 0, 0),
            font_size=15,
            padding=(dp(4), dp(8)),
        )
        self.add_widget(self.text_input)

        actions = ActionRow()
        self.copy_btn = SecondaryButton(text="Copy", icon="copy")
        self.share_btn = SecondaryButton(text="Share", icon="share")
        self.favorite_btn = ActiveIconButton(icon="favorite_off", tooltip_text="Add to favorites")
        if on_copy:
            self.copy_btn.bind(on_release=lambda *a: on_copy())
        if on_share:
            self.share_btn.bind(on_release=lambda *a: on_share())
        if on_favorite:
            self.favorite_btn.bind(on_release=lambda *a: on_favorite())
        actions.add_widget(self.copy_btn)
        actions.add_widget(self.share_btn)
        actions.add_widget(self.favorite_btn)
        self.add_widget(actions)

    def set_text(self, text: str):
        self.text_input.text = text
        self.eyebrow.counter_text = f"{len(text)} / {self._char_limit}"

    def set_favorited(self, is_fav: bool):
        self.favorite_btn.active = is_fav
        self.favorite_btn.icon = "favorite_on" if is_fav else "favorite_off"
        self.favorite_btn._icon_label.text = icon_char(self.favorite_btn.icon)
        self.favorite_btn.tooltip_text = "Remove from favorites" if is_fav else "Add to favorites"

    def apply_theme(self):
        super().apply_theme()
        if self.theme:
            self.text_input.hint_text_color = self.theme.color("text_caption")
            self.text_input.foreground_color = self.theme.color("text_primary")


class StatCard(ThemedBehavior, BoxLayout):
    """Compact MODE / SHIFT / PRESERVE / LENGTH info card (spec section 23)."""

    label = StringProperty("")
    value = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
            self._border_color = Color(0, 0, 0, 0)
            self._border = Line(width=1)
        self.bind(pos=self._sync, size=self._sync)

        self._label_widget = Label(text=self.label, font_size=11, bold=True, halign="left", valign="middle")
        self._value_widget = Label(text=self.value, font_size=13.5, halign="left", valign="top")
        self._label_widget.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self._value_widget.bind(width=lambda w, *_: setattr(w, "text_size", (w.width, None)))
        self.add_widget(self._label_widget)
        self.add_widget(self._value_widget)
        self.bind(label=lambda *a: setattr(self._label_widget, "text", self.label))
        self.bind(value=lambda *a: setattr(self._value_widget, "text", self.value))

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        r = self.theme.radius("card") if self.theme else 12
        self._bg.radius = [r]
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, r)

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("card")
        self._border_color.rgba = self.theme.color("border")
        self._label_widget.color = self.theme.color("text_caption")
        self._value_widget.color = self.theme.color("text_primary")
        pad = self.theme.spacing("sm")
        self.padding = (pad, pad)
        self.spacing = dp(2)
        self._sync()


class _RecordCardBase(Card):
    """Shared layout for HistoryCard/FavoriteCard: original + transformed + meta row."""

    def __init__(self, record, on_copy_original=None, on_copy_output=None,
                 on_reuse=None, on_toggle_favorite=None, on_delete=None, **kwargs):
        self.record = record
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.spacing = dp(6)

        top = BoxLayout(size_hint_y=None, height=dp(18))
        self._timestamp_label = Label(text=self._friendly_time(record.timestamp), font_size=11, halign="left")
        self._mode_label = Label(text=record.mode.upper(), font_size=11, bold=True,
                                  size_hint_x=None, width=dp(70), halign="right")
        for w in (self._timestamp_label, self._mode_label):
            w.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
        top.add_widget(self._timestamp_label)
        top.add_widget(self._mode_label)
        self.add_widget(top)

        self._original_label = Label(
            text=record.input_text, font_size=14, halign="left", valign="top",
            size_hint_y=None,
        )
        self._transformed_label = Label(
            text=record.output_text, font_size=13, halign="left", valign="top",
            size_hint_y=None,
        )
        for w in (self._original_label, self._transformed_label):
            w.bind(width=lambda widget, *_: setattr(widget, "text_size", (widget.width, None)))
            w.bind(texture_size=lambda widget, *_: setattr(widget, "height", widget.texture_size[1]))
        self.add_widget(self._original_label)
        self.add_widget(self._transformed_label)

        actions = ActionRow()
        self.copy_original_btn = IconButton(icon="copy", tooltip_text="Copy original")
        self.copy_output_btn = IconButton(icon="copy", tooltip_text="Copy transformed")
        self.reuse_btn = IconButton(icon="reuse", tooltip_text="Reuse")
        self.favorite_btn = ActiveIconButton(
            icon="favorite_on" if record.is_favorite else "favorite_off",
            tooltip_text="Remove from favorites" if record.is_favorite else "Add to favorites",
            active=record.is_favorite,
        )
        self.delete_btn = IconButton(icon="delete", tooltip_text="Delete")
        if on_copy_original:
            self.copy_original_btn.bind(on_release=lambda *a: on_copy_original(record))
        if on_copy_output:
            self.copy_output_btn.bind(on_release=lambda *a: on_copy_output(record))
        if on_reuse:
            self.reuse_btn.bind(on_release=lambda *a: on_reuse(record))
        if on_toggle_favorite:
            self.favorite_btn.bind(on_release=lambda *a: on_toggle_favorite(record))
        if on_delete:
            self.delete_btn.bind(on_release=lambda *a: on_delete(record))
        for b in (self.copy_original_btn, self.copy_output_btn, self.reuse_btn):
            actions.add_widget(b)
        spacer = BoxLayout()
        actions.add_widget(spacer)
        actions.add_widget(self.favorite_btn)
        actions.add_widget(self.delete_btn)
        self.add_widget(actions)

        self.bind(minimum_height=lambda *a: setattr(self, "height", self.minimum_height))

    @staticmethod
    def _friendly_time(iso_ts: str) -> str:
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(iso_ts)
            return dt.strftime("%d %b, %H:%M")
        except Exception:
            return iso_ts

    def apply_theme(self):
        super().apply_theme()
        if not self.theme:
            return
        self._timestamp_label.color = self.theme.color("text_caption")
        self._mode_label.color = self.theme.accent("main")
        self._original_label.color = self.theme.color("text_primary")
        self._transformed_label.color = self.theme.color("text_secondary")


class HistoryCard(_RecordCardBase):
    pass


class FavoriteCard(_RecordCardBase):
    pass
