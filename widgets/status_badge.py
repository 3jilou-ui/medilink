"""Badge de statut coloré (Normale / Attention / Critique)."""
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.label import Label

from utils.constants import STATUS_COLORS, STATUS_LABELS


class StatusBadge(Label):
    status = StringProperty("NORMAL")

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dp(26))
        kwargs.setdefault("font_size", sp(11))
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(status=self._update, texture_size=self._update_size)
        self._update()

    def _update(self, *args):
        self.text = STATUS_LABELS.get(self.status, self.status)
        color = STATUS_COLORS.get(self.status, STATUS_COLORS["NORMAL"])
        self.color = color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(color[0], color[1], color[2], 0.16)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(8)])
        self.bind(pos=self._move, size=self._move)
        self._update_size()

    def _move(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _update_size(self, *args):
        self.width = self.texture_size[0] + dp(20)
        self.height = max(dp(26), self.texture_size[1] + dp(10))
