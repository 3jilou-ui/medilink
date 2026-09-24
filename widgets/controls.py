"""Contrôles thématisés (boutons, chips, champs) dessinés au Canvas."""
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from utils.constants import (BORDER, CYAN, DANGER, PRIMARY, SUCCESS,
                             SURFACE_LIGHT, SURFACE, TEXT, TEXT_DIM, darken)


class MediButton(Button):
    bg_color = ListProperty(PRIMARY)
    radius = NumericProperty(dp(14))

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", TEXT)
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[self.radius])
        self.bind(pos=self._sync, size=self._sync, bg_color=self._sync,
                  radius=self._sync, state=self._sync)
        self._sync()

    def _sync(self, *args):
        rgba = darken(self.bg_color, 0.82) if self.state == "down" \
            else list(self.bg_color)
        self._color.rgba = rgba
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]


class DangerButton(MediButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = DANGER


class SuccessButton(MediButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = SUCCESS


class GhostButton(MediButton):
    border_color = ListProperty(CYAN)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = (0, 0, 0, 0)
        self.color = CYAN
        with self.canvas.before:
            self._fill = Color(0, 0, 0, 0)
            self._fill_rect = RoundedRectangle(pos=self.pos, size=self.size,
                                               radius=[self.radius])
            self._border = Color(*self.border_color)
            self._line = Line(rounded_rectangle=[self.x, self.y,
                                                 self.width, self.height,
                                                 self.radius], width=1.2)
        self.bind(pos=self._sync2, size=self._sync2, state=self._sync2,
                  border_color=self._sync2, radius=self._sync2)
        self._sync2()

    def _sync2(self, *args):
        self._fill.rgba = SURFACE_LIGHT if self.state == "down" \
            else (0, 0, 0, 0)
        self._fill_rect.pos = self.pos
        self._fill_rect.size = self.size
        self._fill_rect.radius = [self.radius]
        self._border.rgba = self.border_color
        self._line.rounded_rectangle = [self.x, self.y, self.width,
                                        self.height, self.radius]


class SmallButton(MediButton):
    def __init__(self, **kwargs):
        kwargs.setdefault("height", dp(38))
        kwargs.setdefault("font_size", sp(12))
        super().__init__(**kwargs)
        self.radius = dp(10)


class ChipButton(ToggleButton):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("font_size", sp(11))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", TEXT)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(32))
        kwargs.setdefault("size_hint_x", None)
        super().__init__(**kwargs)
        with self.canvas.before:
            self._fill_c = Color(*SURFACE_LIGHT)
            self._fill_r = RoundedRectangle(pos=self.pos, size=self.size,
                                            radius=[dp(10)])
            self._border_c = Color(*BORDER)
            self._border_l = Line(rounded_rectangle=[self.x, self.y,
                                                     self.width, self.height,
                                                     dp(10)], width=1.0)
        self.bind(pos=self._sync, size=self._sync, state=self._sync,
                  texture_size=self._grow)
        self._grow()
        self._sync()

    def _grow(self, *args):
        self.width = self.texture_size[0] + dp(22)

    def _sync(self, *args):
        down = self.state == "down"
        self._fill_c.rgba = PRIMARY if down else SURFACE_LIGHT
        self._fill_r.pos = self.pos
        self._fill_r.size = self.size
        self._border_c.rgba = PRIMARY if down else BORDER
        self._border_l.rounded_rectangle = [self.x, self.y, self.width,
                                            self.height, dp(10)]


class MediTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("foreground_color", TEXT)
        kwargs.setdefault("hint_text_color", TEXT_DIM)
        kwargs.setdefault("cursor_color", CYAN)
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("font_size", sp(14))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("padding", [dp(14), dp(14)])
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*SURFACE_LIGHT)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(12)])
            Color(*BORDER)
            self._line = Line(rounded_rectangle=[self.x, self.y,
                                                 self.width, self.height,
                                                 dp(12)], width=1.0)
        self.bind(pos=self._sync, size=self._sync)
        self._sync()

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = [self.x, self.y, self.width,
                                        self.height, dp(12)]


from kivy.factory import Factory  # noqa: E402
for _name, _cls in (("MediButton", MediButton), ("DangerButton", DangerButton),
                    ("SuccessButton", SuccessButton),
                    ("GhostButton", GhostButton),
                    ("SmallButton", SmallButton),
                    ("ChipButton", ChipButton),
                    ("MediTextInput", MediTextInput)):
    Factory.register(_name, cls=_cls)
