"""
ui/screens/history.py

Search + list of saved conversions (spec sections 24-27, 39). SQLite-backed
via HistoryStore. Clear-all requires confirmation; individual deletes do not
(a single row is a low-stakes, easily-repeated action).
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from ..components.behaviors import ThemedBehavior
from ..components.heading import ScreenHeading
from ..components.cards import HistoryCard
from ..components.buttons import SecondaryButton
from ..components.empty_state import EmptyState
from ..components.icons import icon_char, ICON_FONT


class _SearchField(ThemedBehavior, BoxLayout):
    def __init__(self, on_change=None, hint_text="Search history...", **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = (dp(12), dp(6))
        self.spacing = dp(8)
        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

        from kivy.uix.label import Label

        self._icon_label = Label(text=icon_char("search"), font_name=ICON_FONT, font_size=16,
                                  size_hint_x=None, width=dp(20))
        self.text_input = TextInput(
            hint_text=hint_text, multiline=False,
            background_color=(0, 0, 0, 0), font_size=13,
        )
        if on_change:
            self.text_input.bind(text=lambda w, t: on_change(t))
        self.add_widget(self._icon_label)
        self.add_widget(self.text_input)

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.theme.radius("control") if self.theme else 10]

    def apply_theme(self):
        if not self.theme:
            return
        self._bg_color.rgba = self.theme.color("card")
        self._icon_label.color = self.theme.color("text_caption")
        self.text_input.hint_text_color = self.theme.color("text_caption")
        self.text_input.foreground_color = self.theme.color("text_primary")
        self.text_input.cursor_color = self.theme.accent("main")
        self._sync()


class HistoryScreen(ThemedBehavior, Screen):
    def __init__(self, settings, history_store, snackbar, clipboard_fn, on_reuse=None, **kwargs):
        self.settings = settings
        self.history_store = history_store
        self.snackbar = snackbar
        self.clipboard_fn = clipboard_fn
        self.on_reuse = on_reuse
        super().__init__(**kwargs)
        self.name = "history"

        outer = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))

        self.clear_all_btn = SecondaryButton(text="Clear all", icon="delete")
        self.clear_all_btn.size_hint_x = None
        self.clear_all_btn.width = dp(120)
        self.clear_all_btn.bind(on_release=lambda *a: self._confirm_clear_all())
        self.heading = ScreenHeading(title="History", subtitle="Everything you've converted, saved locally",
                                      right_widget=self.clear_all_btn)
        outer.add_widget(self.heading)

        self.search = _SearchField(on_change=self._on_search)
        outer.add_widget(self.search)

        self._scroll = ScrollView(do_scroll_x=False)
        self._list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self._list.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        self._scroll.add_widget(self._list)
        outer.add_widget(self._scroll)

        self.add_widget(outer)
        self._query = ""

    def on_pre_enter(self, *args):
        self.refresh()

    def _on_search(self, query: str):
        self._query = query
        self.refresh()

    def refresh(self):
        self._list.clear_widgets()
        records = self.history_store.list_history(query=self._query, limit=50)
        if not records:
            if self._query:
                empty = EmptyState("empty_search", "No matching history", "Try a different search term.")
            else:
                empty = EmptyState("empty_history", "No conversions yet", "Type or paste text on Home to begin.")
            self._list.add_widget(empty)
            return
        for record in records:
            card = HistoryCard(
                record,
                on_copy_original=self._copy_original,
                on_copy_output=self._copy_output,
                on_reuse=self._reuse,
                on_toggle_favorite=self._toggle_favorite,
                on_delete=self._delete,
            )
            self._list.add_widget(card)

    def _copy_original(self, record):
        if self.clipboard_fn.copy(record.input_text):
            self.snackbar.show("Copied")

    def _copy_output(self, record):
        if self.clipboard_fn.copy(record.output_text):
            self.snackbar.show("Copied")

    def _reuse(self, record):
        if self.on_reuse:
            self.on_reuse(record)
        self.snackbar.show("Loaded into Home")

    def _toggle_favorite(self, record):
        new_state = not record.is_favorite
        self.history_store.set_favorite(record.id, new_state)
        self.snackbar.show("Added to favorites" if new_state else "Removed from favorites")
        self.refresh()

    def _delete(self, record):
        self.history_store.delete(record.id)
        self.snackbar.show("Deleted")
        self.refresh()

    def _confirm_clear_all(self):
        from ..components.dialogs import ConfirmDialog

        ConfirmDialog(
            title="Clear all history?",
            message="This permanently deletes every saved conversion, including favorites. This can't be undone.",
            confirm_text="Clear all",
            on_confirm=self._do_clear_all,
        ).open()

    def _do_clear_all(self):
        self.history_store.clear_all()
        self.snackbar.show("History cleared")
        self.refresh()

    def apply_theme(self):
        pass
