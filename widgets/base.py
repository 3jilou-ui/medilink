"""Widgets de base : cartes arrondies, espaceurs."""
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from utils.constants import BORDER, SURFACE


def align_labels(root):
    """Force halign/valign sur les Label dont text_size n'est pas défini.

    Les Label dont la largeur est pilotée par texture_size (auto-largeur)
    sont ignorés pour éviter toute boucle de redimensionnement.
    """
    stack = [root]
    while stack:
        node = stack.pop()
        if isinstance(node, Label) and not getattr(node, "_ml_aligned", False):
            node._ml_aligned = True
            auto_width = any(
                getattr(ob, "__name__", "") != "delayed_call_fn"
                for ob in node.get_property_observers("texture_size"))
            if (node.text_size[0] is None and not auto_width
                    and node.halign in ("left", "right")):
                node.valign = "middle"
                node.bind(width=lambda i, w: setattr(i, "text_size",
                                                     (w, None)))
                node.text_size = (node.width, None)
        stack.extend(getattr(node, "children", ()))


class CardBox(BoxLayout):
    bg_color = ListProperty(SURFACE)
    border_color = ListProperty(BORDER)
    radius = NumericProperty(dp(16))

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", dp(14))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_instr = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size,
                                             radius=[self.radius])
            self._bd_instr = Color(*self.border_color)
            self._bd_line = Line(rounded_rectangle=[self.x, self.y,
                                                    self.width, self.height,
                                                    self.radius], width=1.0)
        self.bind(pos=self._sync, size=self._sync, bg_color=self._sync,
                  border_color=self._sync, radius=self._sync)
        if self.orientation == "vertical" and "height" not in kwargs:
            self.bind(minimum_height=self._auto_height)
            self._auto_height()
        self._sync()

    def _auto_height(self, *args):
        self.height = self.minimum_height

    def _sync(self, *args):
        self._bg_instr.rgba = self.bg_color
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]
        self._bd_instr.rgba = self.border_color
        self._bd_line.rounded_rectangle = [self.x, self.y, self.width,
                                           self.height, self.radius]


class Spacer(Widget):
    def __init__(self, height=10, **kwargs):
        super().__init__(size_hint_y=None, height=dp(height), **kwargs)


def wrap_label(text, **kwargs):
    """Label multi-lignes dont la largeur suit le parent."""
    kwargs.setdefault("halign", "center")
    kwargs.setdefault("valign", "middle")
    lbl = Label(text=text, **kwargs)
    lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    return lbl
