"""
ui/screens/settings.py

Spec sections 29-35, 41. Grouped, functional settings -- every toggle here
actually does something (no dead controls, per section 65).
"""

from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp

from ..components.behaviors import ThemedBehavior
from ..components.heading import ScreenHeading
from ..components.segmented import SegmentedControl
from ..components.settings_widgets import SettingSection, SettingRow, ColorSelector
from ..components.switch import ThemedSwitch
from ..components.buttons import SecondaryButton


def _themed_switch(active: bool, on_change):
    return ThemedSwitch(active=active, on_change=on_change)


def _themed_spinner(text, values, on_change, width=140):
    sp = Spinner(text=text, values=values, size_hint=(None, None), size=(dp(width), dp(36)),
                  background_normal="", background_down="")
    sp.bind(text=lambda w, v: on_change(v))
    return sp


class SettingsScreen(ThemedBehavior, Screen):
    def __init__(self, settings, history_store, snackbar, on_apply_char_limit=None,
                 on_apply_live_transform=None, **kwargs):
        self.settings = settings
        self.history_store = history_store
        self.snackbar = snackbar
        self.on_apply_char_limit = on_apply_char_limit
        self.on_apply_live_transform = on_apply_live_transform
        self.theme_ref = None  # set from main.py after construction
        super().__init__(**kwargs)
        self.name = "settings"

        outer = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        outer.size_hint_y = None
        outer.bind(minimum_height=lambda w, *_: setattr(w, "height", w.minimum_height))

        self.heading = ScreenHeading(title="Settings", subtitle="Appearance, behavior, and storage")
        outer.add_widget(self.heading)

        outer.add_widget(self._build_appearance_section())
        outer.add_widget(self._build_behavior_section())
        outer.add_widget(self._build_cipher_section())
        outer.add_widget(self._build_history_section())
        outer.add_widget(self._build_accessibility_section())
        outer.add_widget(self._build_storage_section())
        outer.add_widget(self._build_shortcuts_section())
        outer.add_widget(self._build_about_link_row())

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(outer)
        self.add_widget(scroll)

    # -- section builders -----------------------------------------------------------

    def _build_appearance_section(self):
        s = self.settings
        section = SettingSection("Appearance")

        theme_ctrl = SegmentedControl(
            options=[("dark", "Dark"), ("light", "Light"), ("system", "System")],
            selected=s.theme, on_change=self._on_theme_changed,
        )
        theme_ctrl.size_hint_x = None
        theme_ctrl.width = dp(220)
        section.add_row(SettingRow("Theme", "Dark, light, or match your system", theme_ctrl))

        accent_ctrl = ColorSelector(selected=s.accent, on_select=self._on_accent_changed)
        section.add_row(SettingRow("Accent color", "Applied to buttons, tabs, and highlights", accent_ctrl))

        density_ctrl = SegmentedControl(
            options=[("comfortable", "Comfortable"), ("compact", "Compact")],
            selected=s.get("density"), on_change=lambda v: self._set_and_apply("density", v),
        )
        density_ctrl.size_hint_x = None
        density_ctrl.width = dp(200)
        section.add_row(SettingRow("UI density", "Spacing between elements", density_ctrl))

        font_ctrl = SegmentedControl(
            options=[("small", "Small"), ("medium", "Medium"), ("large", "Large")],
            selected=s.get("font_size"), on_change=lambda v: self._set_and_apply("font_size", v),
        )
        font_ctrl.size_hint_x = None
        font_ctrl.width = dp(200)
        section.add_row(SettingRow("Font size", "Text size across the app", font_ctrl))

        radius_ctrl = SegmentedControl(
            options=[("subtle", "Subtle"), ("standard", "Standard"), ("large", "Large")],
            selected=s.get("radius"), on_change=lambda v: self._set_and_apply("radius", v),
        )
        radius_ctrl.size_hint_x = None
        radius_ctrl.width = dp(200)
        section.add_row(SettingRow("Rounded corners", "Card and button corner radius", radius_ctrl))

        section.add_row(SettingRow("Animations", "Interface motion and transitions",
                                    _themed_switch(s.get("animations"), lambda v: self._set_and_apply("animations", v))))
        section.add_row(SettingRow("Reduced motion", "Minimize animation for accessibility",
                                    _themed_switch(s.get("reduced_motion"), lambda v: self._set_and_apply("reduced_motion", v))))
        return section

    def _build_behavior_section(self):
        s = self.settings
        section = SettingSection("Behavior")
        section.add_row(SettingRow("Live transformation", "Update output while you type",
                                    _themed_switch(s.live_transformation, self._on_live_transform_changed)))
        section.add_row(SettingRow("Auto-save history", "Save every conversion automatically",
                                    _themed_switch(s.get("auto_save_history"), lambda v: self._set_and_apply("auto_save_history", v))))
        section.add_row(SettingRow("Auto-focus input", "Focus the input box on Home automatically",
                                    _themed_switch(s.get("auto_focus_input"), lambda v: self._set_and_apply("auto_focus_input", v))))
        section.add_row(SettingRow("Remember last mode", "Reopen in your last encode/decode mode",
                                    _themed_switch(s.get("remember_last_mode"), lambda v: self._set_and_apply("remember_last_mode", v))))
        section.add_row(SettingRow("Remember last text", "Restore unsent input after restarting",
                                    _themed_switch(s.get("remember_last_text"), lambda v: self._set_and_apply("remember_last_text", v))))
        section.add_row(SettingRow("Confirm before clear", "Ask before clearing typed text",
                                    _themed_switch(s.get("confirm_before_clear"), lambda v: self._set_and_apply("confirm_before_clear", v))))
        section.add_row(SettingRow("Clear input after copy", "Empty the input once output is copied",
                                    _themed_switch(s.get("clear_input_after_copy"), lambda v: self._set_and_apply("clear_input_after_copy", v))))
        return section

    def _build_cipher_section(self):
        s = self.settings
        section = SettingSection("Cipher")
        label = Label(text=f"+{s.shift} / -{s.shift}", bold=True, size_hint=(None, None), size=(dp(90), dp(28)))
        section.add_row(SettingRow("Current shift", "The built-in +2 Cipher behavior", label))

        limit_values = ["1000", "2500", "5000", "10000", "25000"]
        limit_ctrl = _themed_spinner(str(s.char_limit), limit_values, self._on_char_limit_changed)
        section.add_row(SettingRow("Character limit", "Maximum length per conversion", limit_ctrl))
        return section

    def _build_history_section(self):
        s = self.settings
        section = SettingSection("History")
        limit_values = ["50", "100", "250", "500", "1000", "Unlimited"]
        current = "Unlimited" if s.history_limit == 0 else str(s.history_limit)
        limit_ctrl = _themed_spinner(current, limit_values, self._on_history_limit_changed)
        section.add_row(SettingRow("History limit", "Oldest non-favorite entries are trimmed first", limit_ctrl))

        export_btn = SecondaryButton(text="Export", icon="export")
        export_btn.size_hint_x = None
        export_btn.width = dp(110)
        export_btn.bind(on_release=lambda *a: self._export_history())
        section.add_row(SettingRow("Export history", "Save all history to a JSON file", export_btn))

        clear_btn = SecondaryButton(text="Clear all", icon="delete")
        clear_btn.size_hint_x = None
        clear_btn.width = dp(110)
        clear_btn.bind(on_release=lambda *a: self._confirm_clear_history())
        section.add_row(SettingRow("Clear all history", "Permanently delete every saved conversion", clear_btn))
        return section

    def _build_accessibility_section(self):
        s = self.settings
        section = SettingSection("Accessibility")
        section.add_row(SettingRow("High contrast", "Increase text and border contrast",
                                    _themed_switch(s.get("high_contrast"), lambda v: self._set_and_apply("high_contrast", v))))
        note = Label(text="Font scaling, focus states, and keyboard navigation\nare on throughout the app.",
                     font_size=11.5, size_hint=(None, None), size=(dp(260), dp(32)), halign="right")
        note.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        section.add_row(SettingRow("Built in", "", note))
        return section

    def _build_storage_section(self):
        section = SettingSection("Storage")
        used_kb = self.history_store.storage_bytes() / 1024
        usage_label = Label(text=f"{used_kb:.1f} KB", size_hint=(None, None), size=(dp(90), dp(24)))
        section.add_row(SettingRow("Storage used", "Local history database size", usage_label))

        reset_settings_btn = SecondaryButton(text="Reset settings", icon="clear")
        reset_settings_btn.size_hint_x = None
        reset_settings_btn.width = dp(150)
        reset_settings_btn.bind(on_release=lambda *a: self._confirm_reset_settings())
        section.add_row(SettingRow("Reset settings", "Restore all preferences to defaults", reset_settings_btn))

        reset_all_btn = SecondaryButton(text="Reset everything", icon="delete")
        reset_all_btn.size_hint_x = None
        reset_all_btn.width = dp(170)
        reset_all_btn.bind(on_release=lambda *a: self._confirm_reset_everything())
        section.add_row(SettingRow("Reset everything", "Settings, history, and favorites — all of it", reset_all_btn))
        return section

    def _build_shortcuts_section(self):
        section = SettingSection("Keyboard shortcuts (desktop)")
        shortcuts = [
            ("Ctrl/Cmd + Enter", "Transform"),
            ("Ctrl/Cmd + Shift + C", "Copy output"),
            ("Ctrl/Cmd + Shift + V", "Paste"),
            ("Ctrl/Cmd + K", "Clear"),
            ("Ctrl/Cmd + S", "Favorite / save"),
            ("Esc", "Close dialog"),
        ]
        for keys, action in shortcuts:
            key_label = Label(text=keys, size_hint=(None, None), size=(dp(180), dp(20)), halign="right")
            key_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
            section.add_row(SettingRow(action, "", key_label))
        return section

    def _build_about_link_row(self):
        section = SettingSection("More")
        about_btn = SecondaryButton(text="About +2 Cipher", icon="about" if False else "about")
        about_btn.size_hint_x = None
        about_btn.width = dp(170)
        about_btn.bind(on_release=lambda *a: self._go_to_about())
        section.add_row(SettingRow("About", "Version, licenses, and how the cipher works", about_btn))
        return section

    # -- handlers ------------------------------------------------------------------

    def _set_and_apply(self, key, value):
        self.settings.set(key, value)
        if self.theme_ref:
            self.theme_ref.dispatch("on_change")

    def _on_theme_changed(self, value):
        if self.theme_ref:
            self.theme_ref.set_theme(value)

    def _on_accent_changed(self, value):
        if self.theme_ref:
            self.theme_ref.set_accent(value)

    def _on_live_transform_changed(self, value):
        self.settings.set("live_transformation", value)
        if self.on_apply_live_transform:
            self.on_apply_live_transform(value)

    def _on_char_limit_changed(self, value):
        limit = int(value)
        self.settings.set("char_limit", limit)
        if self.on_apply_char_limit:
            self.on_apply_char_limit(limit)
        self.snackbar.show(f"Character limit set to {limit}")

    def _on_history_limit_changed(self, value):
        limit = 0 if value == "Unlimited" else int(value)
        self.settings.set("history_limit", limit)
        self.history_store.enforce_limit(limit if limit else None)
        self.snackbar.show("History limit updated")

    def _export_history(self):
        import os

        out_dir = os.path.expanduser("~/.plus2cipher")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "history_export.json")
        try:
            self.history_store.export_json(path)
            self.snackbar.show(f"Exported to {path}", kind="success")
        except Exception:
            self.snackbar.show("Export failed", kind="error")

    def _confirm_clear_history(self):
        from ..components.dialogs import ConfirmDialog

        ConfirmDialog(
            title="Clear all history?",
            message="This permanently deletes every saved conversion, including favorites.",
            confirm_text="Clear all",
            on_confirm=self._do_clear_history,
        ).open()

    def _do_clear_history(self):
        self.history_store.clear_all()
        self.snackbar.show("History cleared")

    def _confirm_reset_settings(self):
        from ..components.dialogs import ConfirmDialog

        ConfirmDialog(
            title="Reset settings?",
            message="All preferences will return to their defaults. History and favorites are kept.",
            confirm_text="Reset",
            on_confirm=self._do_reset_settings,
        ).open()

    def _do_reset_settings(self):
        self.settings.reset()
        if self.theme_ref:
            self.theme_ref.dispatch("on_change")
        self.snackbar.show("Settings reset")

    def _confirm_reset_everything(self):
        from ..components.dialogs import ConfirmDialog

        ConfirmDialog(
            title="Reset everything?",
            message="Settings, history, and favorites will all be permanently deleted. This can't be undone.",
            confirm_text="Reset everything",
            on_confirm=self._do_reset_everything,
        ).open()

    def _do_reset_everything(self):
        self.settings.reset()
        self.history_store.clear_all()
        if self.theme_ref:
            self.theme_ref.dispatch("on_change")
        self.snackbar.show("Everything reset")

    def _go_to_about(self):
        if self.manager:
            self.manager.current = "about"

    def apply_theme(self):
        pass
