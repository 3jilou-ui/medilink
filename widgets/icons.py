"""Icônes vectorielles dessinées au Canvas Kivy (aucune police d'icônes)."""
import math

from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.widget import Widget

from utils.constants import TEXT


class Icon(Widget):
    name = StringProperty("heart")
    color = ListProperty(TEXT)
    line_width = NumericProperty(1.6)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(24), dp(24)))
        super().__init__(**kwargs)
        self.bind(name=lambda *a: self._redraw(),
                  color=lambda *a: self._redraw(),
                  size=lambda *a: self._redraw(),
                  pos=lambda *a: self._redraw())
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        s = min(self.width, self.height) / 2.0
        if s <= 0:
            return
        with self.canvas:
            Color(*self.color)
            lw = self.line_width
            fn = getattr(self, "_ico_" + self.name, None)
            if fn is None:
                fn = self._ico_dot
            fn(cx, cy, s, lw)

    # -- primitives ----------------------------------------------------
    @staticmethod
    def _circle(cx, cy, r, lw, **kw):
        Line(circle=(cx, cy, r), width=lw, **kw)

    @staticmethod
    def _line(pts, lw, close=False):
        Line(points=pts, width=lw, close=close)

    @staticmethod
    def _dot(cx, cy, r, color=None):
        from kivy.graphics import Color as KColor
        if color:
            KColor(*color)
        Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))

    # -- icônes ----------------------------------------------------------
    def _ico_dot(self, cx, cy, s, lw):
        self._dot(cx, cy, s * 0.3)

    def _ico_home(self, cx, cy, s, lw):
        self._line([cx - s, cy + 0.05 * s, cx, cy + s, cx + s, cy + 0.05 * s], lw)
        self._line([cx - 0.62 * s, cy - 0.05 * s, cx - 0.62 * s, cy - s,
                    cx + 0.62 * s, cy - s, cx + 0.62 * s, cy - 0.05 * s], lw)

    def _ico_pin(self, cx, cy, s, lw):
        self._circle(cx, cy + 0.3 * s, 0.5 * s, lw)
        self._line([cx - 0.36 * s, cy - 0.05 * s, cx, cy - s,
                    cx + 0.36 * s, cy - 0.05 * s], lw)
        self._dot(cx, cy + 0.3 * s, 0.14 * s)

    def _ico_clock(self, cx, cy, s, lw):
        self._circle(cx, cy, 0.8 * s, lw)
        self._line([cx, cy, cx, cy + 0.45 * s], lw)
        self._line([cx, cy, cx + 0.35 * s, cy - 0.1 * s], lw)

    def _ico_bell(self, cx, cy, s, lw):
        Line(circle=(cx, cy + 0.05 * s, 0.62 * s, 180, 360), width=lw)
        self._line([cx - 0.62 * s, cy + 0.05 * s, cx - 0.62 * s, cy - 0.35 * s], lw)
        self._line([cx + 0.62 * s, cy + 0.05 * s, cx + 0.62 * s, cy - 0.35 * s], lw)
        self._line([cx - 0.85 * s, cy - 0.35 * s, cx + 0.85 * s, cy - 0.35 * s], lw)
        self._dot(cx, cy - 0.65 * s, 0.14 * s)

    def _ico_person(self, cx, cy, s, lw):
        self._circle(cx, cy + 0.45 * s, 0.34 * s, lw)
        Line(circle=(cx, cy - 0.75 * s, 0.68 * s, 20, 160), width=lw)

    def _ico_heart(self, cx, cy, s, lw):
        Line(circle=(cx - 0.32 * s, cy + 0.28 * s, 0.36 * s, 0, 200), width=lw)
        Line(circle=(cx + 0.32 * s, cy + 0.28 * s, 0.36 * s, 340, 540), width=lw)
        self._line([cx - 0.66 * s, cy + 0.18 * s, cx, cy - 0.85 * s,
                    cx + 0.66 * s, cy + 0.18 * s], lw)

    def _ico_lungs(self, cx, cy, s, lw):
        self._line([cx, cy + 0.9 * s, cx, cy + 0.2 * s], lw)
        Line(rounded_rectangle=[cx - 0.78 * s, cy - 0.85 * s, 0.55 * s, 1.15 * s,
                                0.25 * s], width=lw)
        Line(rounded_rectangle=[cx + 0.23 * s, cy - 0.85 * s, 0.55 * s, 1.15 * s,
                                0.25 * s], width=lw)

    def _ico_drop(self, cx, cy, s, lw):
        Line(circle=(cx, cy - 0.2 * s, 0.5 * s, 200, 520), width=lw)
        self._line([cx - 0.42 * s, cy + 0.05 * s, cx, cy + 0.9 * s,
                    cx + 0.42 * s, cy + 0.05 * s], lw)

    def _ico_sweat(self, cx, cy, s, lw):
        self._ico_drop(cx - 0.2 * s, cy, s * 0.85, lw)
        self._dot(cx + 0.6 * s, cy - 0.5 * s, 0.12 * s)
        self._dot(cx + 0.65 * s, cy + 0.1 * s, 0.09 * s)

    def _ico_gauge(self, cx, cy, s, lw):
        self._circle(cx, cy, 0.75 * s, lw)
        self._line([cx, cy, cx + 0.4 * s, cy + 0.4 * s], lw)
        self._dot(cx, cy, 0.1 * s)

    def _ico_thermo(self, cx, cy, s, lw):
        Line(rounded_rectangle=[cx - 0.2 * s, cy - 0.35 * s, 0.4 * s, 1.15 * s,
                                0.2 * s], width=lw)
        self._circle(cx, cy - 0.6 * s, 0.3 * s, lw)
        self._line([cx, cy - 0.45 * s, cx, cy + 0.2 * s], lw)

    def _ico_moon(self, cx, cy, s, lw):
        Line(circle=(cx, cy, 0.75 * s, 70, 310), width=lw)
        Line(circle=(cx + 0.35 * s, cy, 0.55 * s, 110, 250), width=lw)

    def _ico_battery(self, cx, cy, s, lw):
        Line(rectangle=[cx - 0.8 * s, cy - 0.4 * s, 1.35 * s, 0.8 * s], width=lw)
        Line(rectangle=[cx + 0.55 * s, cy - 0.18 * s, 0.18 * s, 0.36 * s], width=lw)
        level = getattr(self, "level", 0.78)
        from kivy.graphics import Color as KColor
        KColor(*self.color)
        Ellipse(pos=(cx - 0.68 * s, cy - 0.26 * s),
                size=(1.1 * s * max(0.05, level), 0.52 * s))

    def _ico_bluetooth(self, cx, cy, s, lw):
        self._line([cx - 0.45 * s, cy + 0.5 * s, cx + 0.4 * s, cy - 0.2 * s,
                    cx, cy - 0.7 * s, cx, cy + 0.7 * s,
                    cx + 0.4 * s, cy + 0.2 * s, cx - 0.45 * s, cy - 0.5 * s], lw)

    def _ico_sync(self, cx, cy, s, lw):
        Line(circle=(cx, cy, 0.65 * s, 200, 340), width=lw)
        Line(circle=(cx, cy, 0.65 * s, 20, 160), width=lw)
        self._line([cx + 0.55 * s, cy + 0.45 * s, cx + 0.62 * s, cy + 0.12 * s,
                    cx + 0.28 * s, cy + 0.28 * s], lw)
        self._line([cx - 0.55 * s, cy - 0.45 * s, cx - 0.62 * s, cy - 0.12 * s,
                    cx - 0.28 * s, cy - 0.28 * s], lw)

    def _ico_warning(self, cx, cy, s, lw):
        self._line([cx, cy + 0.85 * s, cx - 0.8 * s, cy - 0.65 * s,
                    cx + 0.8 * s, cy - 0.65 * s], lw, close=True)
        self._line([cx, cy + 0.3 * s, cx, cy - 0.15 * s], lw)
        self._dot(cx, cy - 0.42 * s, 0.09 * s)

    def _ico_ambulance(self, cx, cy, s, lw):
        Line(rectangle=[cx - 0.85 * s, cy - 0.35 * s, 1.05 * s, 0.75 * s], width=lw)
        self._line([cx + 0.2 * s, cy - 0.35 * s, cx + 0.2 * s, cy + 0.1 * s,
                    cx + 0.55 * s, cy + 0.1 * s, cx + 0.8 * s, cy - 0.35 * s], lw)
        self._circle(cx - 0.5 * s, cy - 0.5 * s, 0.18 * s, lw)
        self._circle(cx + 0.45 * s, cy - 0.5 * s, 0.18 * s, lw)
        self._line([cx - 0.5 * s, cy + 0.02 * s, cx - 0.15 * s, cy + 0.02 * s], lw)
        self._line([cx - 0.32 * s, cy - 0.15 * s, cx - 0.32 * s, cy + 0.2 * s], lw)

    def _ico_chat(self, cx, cy, s, lw):
        Line(rounded_rectangle=[cx - 0.8 * s, cy - 0.3 * s, 1.6 * s, 1.0 * s,
                                0.3 * s], width=lw)
        self._line([cx - 0.3 * s, cy - 0.3 * s, cx - 0.45 * s, cy - 0.75 * s,
                    cx - 0.02 * s, cy - 0.3 * s], lw)
        self._dot(cx - 0.35 * s, cy + 0.2 * s, 0.08 * s)
        self._dot(cx, cy + 0.2 * s, 0.08 * s)
        self._dot(cx + 0.35 * s, cy + 0.2 * s, 0.08 * s)

    def _ico_cross(self, cx, cy, s, lw):
        self._circle(cx, cy, 0.8 * s, lw)
        self._line([cx - 0.35 * s, cy, cx + 0.35 * s, cy], lw)
        self._line([cx, cy - 0.35 * s, cx, cy + 0.35 * s], lw)

    def _ico_back(self, cx, cy, s, lw):
        self._line([cx + 0.35 * s, cy + 0.6 * s, cx - 0.35 * s, cy,
                    cx + 0.35 * s, cy - 0.6 * s], lw)

    def _ico_gear(self, cx, cy, s, lw):
        self._circle(cx, cy, 0.4 * s, lw)
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = cx + 0.55 * s * math.cos(a), cy + 0.55 * s * math.sin(a)
            x2, y2 = cx + 0.8 * s * math.cos(a), cy + 0.8 * s * math.sin(a)
            self._line([x1, y1, x2, y2], lw)

    def _ico_phone(self, cx, cy, s, lw):
        Line(rounded_rectangle=[cx - 0.4 * s, cy - 0.8 * s, 0.8 * s, 1.6 * s,
                                0.18 * s], width=lw)
        self._line([cx - 0.15 * s, cy - 0.55 * s, cx + 0.15 * s, cy - 0.55 * s], lw)

    def _ico_info(self, cx, cy, s, lw):
        self._circle(cx, cy, 0.8 * s, lw)
        self._line([cx, cy + 0.35 * s, cx, cy - 0.35 * s], lw)
        self._dot(cx, cy + 0.5 * s, 0.08 * s)

    def _ico_logout(self, cx, cy, s, lw):
        self._line([cx - 0.1 * s, cy + 0.7 * s, cx - 0.7 * s, cy + 0.7 * s,
                    cx - 0.7 * s, cy - 0.7 * s, cx - 0.1 * s, cy - 0.7 * s], lw)
        self._line([cx + 0.1 * s, cy, cx + 0.8 * s, cy], lw)
        self._line([cx + 0.5 * s, cy + 0.3 * s, cx + 0.8 * s, cy,
                    cx + 0.5 * s, cy - 0.3 * s], lw)

    def _ico_send(self, cx, cy, s, lw):
        self._line([cx - 0.7 * s, cy, cx + 0.8 * s, cy + 0.6 * s,
                    cx + 0.8 * s, cy - 0.6 * s], lw, close=True)

    def _ico_doc(self, cx, cy, s, lw):
        Line(rounded_rectangle=[cx - 0.55 * s, cy - 0.8 * s, 1.1 * s, 1.6 * s,
                                0.15 * s], width=lw)
        self._line([cx - 0.3 * s, cy + 0.35 * s, cx + 0.3 * s, cy + 0.35 * s], lw)
        self._line([cx - 0.3 * s, cy, cx + 0.3 * s, cy], lw)
        self._line([cx - 0.3 * s, cy - 0.35 * s, cx + 0.3 * s, cy - 0.35 * s], lw)

    def _ico_lock(self, cx, cy, s, lw):
        Line(rectangle=[cx - 0.6 * s, cy - 0.7 * s, 1.2 * s, 0.9 * s], width=lw)
        Line(circle=(cx, cy + 0.2 * s, 0.35 * s, 0, 180), width=lw)

    def _ico_mail(self, cx, cy, s, lw):
        Line(rectangle=[cx - 0.8 * s, cy - 0.5 * s, 1.6 * s, 1.0 * s], width=lw)
        self._line([cx - 0.8 * s, cy + 0.5 * s, cx, cy - 0.05 * s,
                    cx + 0.8 * s, cy + 0.5 * s], lw)

    def _ico_plus(self, cx, cy, s, lw):
        self._line([cx - 0.6 * s, cy, cx + 0.6 * s, cy], lw)
        self._line([cx, cy - 0.6 * s, cx, cy + 0.6 * s], lw)

    def _ico_minus(self, cx, cy, s, lw):
        self._line([cx - 0.6 * s, cy, cx + 0.6 * s, cy], lw)

    def _ico_filter(self, cx, cy, s, lw):
        self._line([cx - 0.75 * s, cy + 0.6 * s, cx + 0.75 * s, cy + 0.6 * s,
                    cx + 0.15 * s, cy - 0.1 * s, cx + 0.15 * s, cy - 0.7 * s,
                    cx - 0.15 * s, cy - 0.5 * s, cx - 0.15 * s, cy - 0.1 * s],
                   lw, close=True)

    def _ico_bracelet(self, cx, cy, s, lw):
        Line(circle=(cx, cy, 0.45 * s), width=lw)
        Line(rectangle=[cx - 0.28 * s, cy - 0.95 * s, 0.56 * s, 0.5 * s], width=lw)
        Line(rectangle=[cx - 0.28 * s, cy + 0.45 * s, 0.56 * s, 0.5 * s], width=lw)
        self._dot(cx, cy, 0.12 * s)
