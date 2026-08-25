"""
ui/screens/favorites.py

Spec sections 28, 40. A filtered view of history where is_favorite = True.
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from ..components.behaviors import ThemedBehavior
from ..components.heading import ScreenHeading
from ..components.cards import FavoriteCard
from ..components.empty_state import EmptyState
from .history import _SearchField


class FavoritesScreen(ThemedBehavior, Screen):
    def __init__(self, settings, history_store, snackbar, clipboard_fn, on_reuse=None, **kwargs):
        self.settings = settings
        self.history_store = history_store
        self.snackbar = snackbar
        self.clipboard_fn = clipboard_fn
        self.on_reuse = on_reuse
        super().__init__(**kwargs)
        self.name = "favorites"

        outer = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        self.heading = ScreenHeading(title="Favorites", subtitle="Conversions you've starred for later")
        outer.add_widget(self.heading)

        self.search = _SearchField(on_change=self._on_search, hint_text="Search favorites...")
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
        records = self.history_store.list_favorites(query=self._query, limit=50)
        if not records:
            if self._query:
                empty = EmptyState("empty_search", "No matching favorites", "Try a different search term.")
            else:
                empty = EmptyState("empty_favorites", "No favorites yet",
                                    "Tap the star on any conversion to save it here.")
            self._list.add_widget(empty)
            return
        for record in records:
            card = FavoriteCard(
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
        self.history_store.set_favorite(record.id, False)
        self.snackbar.show("Removed from favorites")
        self.refresh()

    def _delete(self, record):
        self.history_store.delete(record.id)
        self.snackbar.show("Deleted")
        self.refresh()

    def apply_theme(self):
        pass
