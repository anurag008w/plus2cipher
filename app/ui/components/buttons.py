"""
ui/components/buttons.py

PrimaryButton   - filled with the current accent color. Main calls to action.
SecondaryButton - card-colored with a border. Secondary actions.
IconButton      - icon-only, circular-ish rounded square, optional tooltip.

All three support: normal / hover (desktop) / pressed / focused / disabled,
and redraw live on theme or accent change (spec sections 7, 46, 63).
"""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.animation import Animation

from .behaviors import ThemedBehavior
from .tooltip import TooltipBehavior
from .icons import icon_char, ICON_FONT


class _BaseButton(ThemedBehavior, TooltipBehavior, FocusBehavior, ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon = StringProperty("")  # semantic icon name, see components/icons.py
    disabled_look = BooleanProperty(False)
    corner_radius = NumericProperty(10)

    def __init__(self, **kwargs):
        self._bg_color = [0, 0, 0, 0]
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = 8
        self.padding = (16, 10)
        with self.canvas.before:
            self._color_instr = Color(0, 0, 0, 0)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.corner_radius])
            self._focus_color = Color(1, 1, 1, 0)
            self._focus_ring = Line(width=1.6)
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)
        self.bind(state=lambda *a: self._refresh_colors())
        self.bind(hovered=lambda *a: self._refresh_colors())
        self.bind(focus=lambda *a: self._refresh_colors())
        self.bind(disabled=lambda *a: self._refresh_colors())
        self._build_content()

    def _build_content(self):
        if self.icon:
            self._icon_label = Label(
                text=icon_char(self.icon),
                font_name=ICON_FONT,
                font_size=18,
                size_hint=(None, 1),
                width=22,
            )
            self.add_widget(self._icon_label)
        if self.text:
            self._text_label = Label(text=self.text, font_size=14, bold=True, shorten=False)
            self.add_widget(self._text_label)

    def _sync_canvas(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self.corner_radius]
        self._focus_ring.rounded_rectangle = (
            self.x + 1, self.y + 1, self.width - 2, self.height - 2, self.corner_radius
        )

    def apply_theme(self):
        self._refresh_colors()
        if hasattr(self, "_text_label"):
            self._text_label.color = self._text_color()
        if hasattr(self, "_icon_label"):
            self._icon_label.color = self._text_color()

    def _text_color(self):
        return (1, 1, 1, 1)

    def _fill_color(self):
        return (0, 0, 0, 0)

    def _refresh_colors(self):
        if not self.theme:
            return
        fill = list(self._fill_color())
        if self.disabled:
            fill[3] = fill[3] * 0.4 if len(fill) > 3 else 0.4
        elif self.state == "down":
            fill = list(self._pressed_color())
        elif self.hovered:
            fill = list(self._hover_color())
        self._color_instr.rgba = fill
        self._focus_color.rgba = self.theme.accent("main") if self.focus else (1, 1, 1, 0)
        text_color = self._text_color()
        if self.disabled:
            text_color = self.theme.color("text_disabled")
        if hasattr(self, "_text_label"):
            self._text_label.color = text_color
        if hasattr(self, "_icon_label"):
            self._icon_label.color = text_color

    def _hover_color(self):
        return self._fill_color()

    def _pressed_color(self):
        return self._fill_color()


class PrimaryButton(_BaseButton):
    """Filled with the current accent. Use for the one main action on a card/screen."""

    def _fill_color(self):
        return self.theme.accent("main") if self.theme else (0.5, 0.4, 0.9, 1)

    def _hover_color(self):
        return self.theme.accent("hover") if self.theme else (0.6, 0.5, 1, 1)

    def _pressed_color(self):
        return self.theme.accent("pressed") if self.theme else (0.4, 0.3, 0.8, 1)

    def _text_color(self):
        return self.theme.accent("on_accent") if self.theme else (1, 1, 1, 1)


class SecondaryButton(_BaseButton):
    """Card-colored with a subtle border. Use for secondary actions (Paste, Clear...)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._border_color = Color(1, 1, 1, 0.1)
            self._border = Line(width=1)
        self.bind(pos=self._sync_border, size=self._sync_border)

    def _sync_border(self, *_):
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, self.corner_radius
        )

    def apply_theme(self):
        super().apply_theme()
        if self.theme:
            self._border_color.rgba = self.theme.color("border_strong")

    def _fill_color(self):
        return self.theme.color("card_elevated") if self.theme else (0.08, 0.1, 0.16, 1)

    def _hover_color(self):
        return self.theme.color("surface_hover") if self.theme else (0.1, 0.12, 0.2, 1)

    def _pressed_color(self):
        return self.theme.color("surface_pressed") if self.theme else (0.12, 0.14, 0.22, 1)

    def _text_color(self):
        return self.theme.color("text_primary") if self.theme else (1, 1, 1, 1)


class IconButton(_BaseButton):
    """Icon-only square-ish button. Pass `icon=` and optionally `tooltip_text=`."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (40, 40))
        kwargs.setdefault("corner_radius", 10)
        super().__init__(**kwargs)
        self.padding = (0, 0)

    def _build_content(self):
        self._icon_label = Label(text=icon_char(self.icon), font_name=ICON_FONT, font_size=20)
        self.add_widget(self._icon_label)

    def _fill_color(self):
        return (0, 0, 0, 0)

    def _hover_color(self):
        return self.theme.color("surface_hover") if self.theme else (1, 1, 1, 0.06)

    def _pressed_color(self):
        return self.theme.color("surface_pressed") if self.theme else (1, 1, 1, 0.12)

    def _text_color(self):
        return self.theme.color("text_secondary") if self.theme else (0.7, 0.7, 0.75, 1)


class ActiveIconButton(IconButton):
    """An IconButton that can be toggled into an accent-highlighted 'active' state.

    Used for things like the favorite star, where the icon itself changes
    meaning (outline vs filled) as well as color.
    """

    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(active=lambda *a: self._refresh_colors())

    def _text_color(self):
        if self.active and self.theme:
            return self.theme.accent("main")
        return super()._text_color()
