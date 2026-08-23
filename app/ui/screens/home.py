"""
ui/screens/home.py

The primary screen (spec sections 14-23, 38). Encode (+2) / Decode (-2)
segmented control, Input/Output cards, a center swap/transform control, and
a compact Mode/Shift/Preserve/Length info row. Responsive: side-by-side
cards above the mobile breakpoint, stacked below it.
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock

from ..components.behaviors import ThemedBehavior
from ..components.heading import ScreenHeading
from ..components.segmented import SegmentedControl
from ..components.cards import InputCard, OutputCard, StatCard
from ..components.buttons import IconButton
from ..theme.tokens import BREAKPOINT_MOBILE_MAX
from ...core import cipher

_MODE_LABELS = {"encode": "Encode (+2)", "decode": "Decode (-2)"}


class HomeScreen(ThemedBehavior, Screen):
    def __init__(self, settings, history_store, snackbar, share_fn, clipboard_fn, **kwargs):
        self.settings = settings
        self.history_store = history_store
        self.snackbar = snackbar
        self.share_fn = share_fn
        self.clipboard_fn = clipboard_fn
        self._current_favorite_record_id = None
        super().__init__(**kwargs)
        self.name = "home"

        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(20), spacing=dp(16))
        root.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        self._root = root

        self._top_swap_btn = IconButton(icon="swap", tooltip_text="Swap input & output")
        self._top_swap_btn.bind(on_release=lambda *a: self._swap())
        self.heading = ScreenHeading(
            title="Encode / Decode",
            subtitle="Transform text with +2 or -2 cipher",
            right_widget=self._top_swap_btn,
        )
        root.add_widget(self.heading)

        self.segmented = SegmentedControl(
            options=[("encode", "Encode (+2)"), ("decode", "Decode (-2)")],
            selected=settings.get("last_mode", "encode"),
            on_change=self._on_mode_changed,
        )
        root.add_widget(self.segmented)

        self._workspace = BoxLayout(size_hint_y=None, spacing=dp(16))
        self._workspace.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))
        root.add_widget(self._workspace)

        self.input_card = InputCard(
            char_limit=settings.char_limit,
            on_text_change=self._on_input_changed,
            on_paste=self._on_paste,
            on_clear=self._on_clear,
            on_transform=self._transform,
        )
        self.output_card = OutputCard(
            char_limit=settings.char_limit,
            on_copy=self._on_copy,
            on_share=self._on_share,
            on_favorite=self._on_toggle_favorite,
        )
        self.input_card.size_hint_y = None
        self.output_card.size_hint_y = None
        self.input_card.height = dp(260)
        self.output_card.height = dp(260)

        self._center_swap_btn = IconButton(icon="swap", tooltip_text="Swap input & output",
                                            size=(dp(44), dp(44)))
        self._center_swap_btn.bind(on_release=lambda *a: self._swap())
        self._center_wrap = BoxLayout(size_hint=(None, None), size=(dp(56), dp(260)))
        self._center_wrap.add_widget(BoxLayout())
        self._center_wrap.add_widget(self._center_swap_btn)
        self._center_wrap.add_widget(BoxLayout())

        # A second, independent button instance for the stacked (mobile)
        # layout -- deliberately NOT the same widget as _center_swap_btn,
        # since a widget can only have one parent at a time and swapping a
        # shared instance between containers on every resize is fragile.
        self._center_swap_btn_mobile = IconButton(icon="swap", tooltip_text="Swap input & output",
                                                    size=(dp(44), dp(44)))
        self._center_swap_btn_mobile.bind(on_release=lambda *a: self._swap())
        self._center_row_mobile = BoxLayout(size_hint_y=None, height=dp(44))
        self._center_row_mobile.add_widget(BoxLayout())
        self._center_row_mobile.add_widget(self._center_swap_btn_mobile)
        self._center_row_mobile.add_widget(BoxLayout())

        stats_row = BoxLayout(size_hint_y=None, height=dp(76), spacing=dp(12))
        self.mode_stat = StatCard(label="MODE", value=_MODE_LABELS[self.segmented.selected])
        self.shift_stat = StatCard(label="SHIFT", value=f"+{settings.shift} / -{settings.shift}")
        self.preserve_stat = StatCard(label="PRESERVE", value="Letters, spaces, numbers, symbols")
        self.length_stat = StatCard(label="LENGTH", value="0 characters")
        for s in (self.mode_stat, self.shift_stat, self.preserve_stat, self.length_stat):
            stats_row.add_widget(s)
        root.add_widget(stats_row)

        scroll.add_widget(root)
        self.add_widget(scroll)

        self._layout_is_stacked = None
        Window.bind(size=self._on_window_resize)
        Clock.schedule_once(lambda dt: self._on_window_resize(Window, Window.size), 0)

        if settings.get("remember_last_text", True):
            self.input_card.text_input.text = settings.get("last_text", "")

    # -- responsive workspace layout ------------------------------------------------

    def _on_window_resize(self, window, size):
        stacked = size[0] < BREAKPOINT_MOBILE_MAX + 100  # a little headroom over the raw mobile cutoff
        if stacked == self._layout_is_stacked:
            return
        self._layout_is_stacked = stacked
        self._workspace.clear_widgets()
        self._workspace.orientation = "vertical" if stacked else "horizontal"
        if stacked:
            self.input_card.size_hint_x = 1
            self.output_card.size_hint_x = 1
            self._workspace.add_widget(self.input_card)
            self._workspace.add_widget(self._center_row_mobile)
            self._workspace.add_widget(self.output_card)
            self._workspace.size_hint_y = None
        else:
            self.input_card.size_hint_x = 0.5
            self.output_card.size_hint_x = 0.5
            self._workspace.add_widget(self.input_card)
            self._workspace.add_widget(self._center_wrap)
            self._workspace.add_widget(self.output_card)

    # -- transformation logic ------------------------------------------------------

    def _on_mode_changed(self, mode: str):
        self.settings.set("last_mode", mode)
        self.mode_stat.value = _MODE_LABELS[mode]
        self._transform()  # mode switch always updates output instantly (spec 18)

    def _on_input_changed(self, text: str):
        self.length_stat.value = f"{len(text)} character{'s' if len(text) != 1 else ''}"
        if self.settings.get("remember_last_text", True):
            self.settings.set("last_text", text, autosave=False)
        if self.settings.live_transformation:
            self._transform()
        self._current_favorite_record_id = None
        self.output_card.set_favorited(False)

    def _transform(self, *_):
        text = self.input_card.text_input.text
        mode = self.segmented.selected
        result = cipher.apply_mode(text, mode, self.settings.shift)
        self.output_card.set_text(result)
        if text and self.settings.get("auto_save_history", True):
            record = self.history_store.add(mode, text, result)
            self.history_store.enforce_limit(self.settings.history_limit)
            self._current_favorite_record_id = record.id
            self.output_card.set_favorited(False)

    def set_live_transformation(self, is_live: bool):
        self.input_card.set_live_mode(is_live)

    def apply_char_limit(self, limit: int):
        self.input_card.set_char_limit(limit)
        self.output_card._char_limit = limit

    # -- actions ---------------------------------------------------------------------

    def _on_paste(self):
        pasted = self.clipboard_fn.paste()
        if pasted:
            self.input_card.text_input.text = pasted
            self.snackbar.show("Pasted")
        else:
            self.snackbar.show("Clipboard is empty")

    def _on_clear(self):
        if self.settings.get("confirm_before_clear", True) and self.input_card.text_input.text:
            from ..components.dialogs import ConfirmDialog

            ConfirmDialog(
                title="Clear input?",
                message="This will clear the text you've typed. This can't be undone.",
                confirm_text="Clear",
                on_confirm=self._do_clear,
            ).open()
        else:
            self._do_clear()

    def _do_clear(self):
        self.input_card.text_input.text = ""
        self.output_card.set_text("")
        self.snackbar.show("Cleared")

    def _on_copy(self):
        text = self.output_card.text_input.text
        if not text:
            self.snackbar.show("Nothing to copy yet")
            return
        if self.clipboard_fn.copy(text):
            self.snackbar.show("Copied")
            if self.settings.get("clear_input_after_copy", False):
                self._do_clear()
        else:
            self.snackbar.show("Couldn't access the clipboard")

    def _on_share(self):
        text = self.output_card.text_input.text
        result = self.share_fn(text)
        self.snackbar.show(result.message, kind="success" if result.ok else "error")

    def _on_toggle_favorite(self):
        if self._current_favorite_record_id is None:
            self.snackbar.show("Type something to save a favorite")
            return
        new_state = not self.output_card.favorite_btn.active
        self.history_store.set_favorite(self._current_favorite_record_id, new_state)
        self.output_card.set_favorited(new_state)
        self.snackbar.show("Added to favorites" if new_state else "Removed from favorites")

    def _swap(self):
        new_input = self.output_card.text_input.text
        if not new_input:
            self.snackbar.show("Nothing to swap yet")
            return
        new_mode = "decode" if self.segmented.selected == "encode" else "encode"
        self.segmented.select(new_mode)  # triggers _on_mode_changed -> _transform
        self.input_card.text_input.text = new_input

    def apply_theme(self):
        pass
