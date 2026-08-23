"""
ui/components/dialogs.py

ConfirmDialog: a modal used ONLY for destructive/irreversible actions
(clear all history, reset settings, reset everything -- spec sections 26,
32, 34). Normal actions use the Snackbar instead of a dialog (section 19).
"""

from __future__ import annotations

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from .behaviors import ThemedBehavior
from .buttons import PrimaryButton, SecondaryButton


class ConfirmDialog(ThemedBehavior, ModalView):
    def __init__(self, title: str, message: str, confirm_text: str = "Confirm",
                 on_confirm=None, destructive: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(360), dp(200))
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        self.auto_dismiss = True
        self._destructive = destructive

        with self.canvas.before:
            self._scrim_color = Color(0, 0, 0, 0)

        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        with content.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=content.pos, size=content.size)
        content.bind(pos=self._sync_bg, size=self._sync_bg)

        self._title_label = Label(text=title, bold=True, font_size=16,
                                   size_hint_y=None, height=dp(24), halign="left")
        self._title_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self._message_label = Label(text=message, font_size=13, halign="left", valign="top")
        self._message_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))

        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = SecondaryButton(text="Cancel")
        confirm_btn = PrimaryButton(text=confirm_text)
        cancel_btn.bind(on_release=lambda *a: self.dismiss())

        def _confirm(*_):
            self.dismiss()
            if on_confirm:
                on_confirm()

        confirm_btn.bind(on_release=_confirm)
        actions.add_widget(cancel_btn)
        actions.add_widget(confirm_btn)
        self._confirm_btn = confirm_btn

        content.add_widget(self._title_label)
        content.add_widget(self._message_label)
        content.add_widget(actions)
        self.add_widget(content)
        self._content = content

        from kivy.core.window import Window

        self._window = Window
        Window.bind(on_keyboard=self._on_keyboard)
        self.bind(on_dismiss=lambda *a: self._window.unbind(on_keyboard=self._on_keyboard))

    def _on_keyboard(self, window, key, *args):
        if key == 27 and self._parent_window:  # Esc closes the dialog
            self.dismiss()
            return True
        return False

    def _sync_bg(self, *_):
        self._bg.pos = self._content.pos
        self._bg.size = self._content.size
        self._bg.radius = [self.theme.radius("sheet") if self.theme else 18]

    def apply_theme(self):
        if not self.theme:
            return
        self._scrim_color.rgba = self.theme.color("scrim")
        self._bg_color.rgba = self.theme.color("card_elevated")
        self._title_label.color = self.theme.color("text_primary")
        self._message_label.color = self.theme.color("text_secondary")
        if self._destructive:
            self._confirm_btn._fill_color = lambda: self.theme.color("error")
        self._sync_bg()
