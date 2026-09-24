"""Graphiques en lignes dessinés au Canvas Kivy."""
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from utils.constants import BORDER, TEXT_DIM


class GraphCanvas(Widget):
    series = ListProperty([])      # [{'name','color','values':[...]}]
    x_labels = ListProperty([])
    show_dots = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(series=lambda *a: self._redraw(),
                  size=lambda *a: self._redraw(),
                  pos=lambda *a: self._redraw(),
                  x_labels=lambda *a: self._redraw())

    def _redraw(self, *args):
        self.canvas.clear()
        w, h = self.size
        if w <= 1 or h <= 1:
            return
        ox, oy = self.pos
        pad_l, pad_r, pad_t, pad_b = dp(6), dp(6), dp(8), dp(8)
        iw = w - pad_l - pad_r
        ih = h - pad_t - pad_b

        all_values = [v for s in self.series for v in s.get("values", [])
                      if v is not None]
        if not all_values:
            return
        vmin, vmax = min(all_values), max(all_values)
        if vmax - vmin < 1e-6:
            vmin, vmax = vmin - 1, vmax + 1
        margin = (vmax - vmin) * 0.15
        vmin, vmax = vmin - margin, vmax + margin

        with self.canvas:
            # grille horizontale
            Color(BORDER[0], BORDER[1], BORDER[2], 0.6)
            for i in range(4):
                y = oy + pad_t + ih * i / 3.0
                Line(points=[ox + pad_l, y, ox + w - pad_r, y], width=0.7)

            for s in self.series:
                values = [v for v in s.get("values", []) if v is not None]
                if len(values) < 2:
                    continue
                n = len(values)
                pts = []
                for i, v in enumerate(values):
                    x = ox + pad_l + iw * i / (n - 1)
                    y = oy + pad_t + ih * (1 - (v - vmin) / (vmax - vmin))
                    pts.extend([x, y])
                Color(*s.get("color", (1, 1, 1, 1)))
                Line(points=pts, width=1.6)
                if self.show_dots and n <= 60:
                    for i in range(0, n, max(1, n // 24)):
                        x = pts[i * 2]
                        y = pts[i * 2 + 1]
                        Ellipse(pos=(x - dp(2), y - dp(2)),
                                size=(dp(4), dp(4)))


class LineGraph(BoxLayout):
    """Graphique complet : légende + canvas + axe des abscisses."""

    def __init__(self, height=170, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(6), **kwargs)
        self.size_hint_y = None
        self.height = dp(height)
        self.legend = BoxLayout(size_hint_y=None, height=dp(20),
                                spacing=dp(14))
        self.canvas_widget = GraphCanvas()
        self.x_row = BoxLayout(size_hint_y=None, height=dp(18))
        self.add_widget(self.legend)
        self.add_widget(self.canvas_widget)
        self.add_widget(self.x_row)

    def set_data(self, labels, series):
        """series : liste de (nom, couleur, valeurs)."""
        self.canvas_widget.series = [
            {"name": name, "color": color, "values": values}
            for name, color, values in series
        ]
        self.canvas_widget.x_labels = labels
        self.legend.clear_widgets()
        for name, color, _values in series:
            item = BoxLayout(size_hint_x=None, spacing=dp(5))
            dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)))
            with dot.canvas:
                Color(*color)
                Ellipse(pos=dot.pos, size=dot.size)
            dot.bind(pos=lambda inst, val, d=dot: setattr(
                inst.canvas.children[-1], "pos", val))
            lbl = Label(text=name, font_size=sp(10),
                        color=TEXT_DIM, size_hint_x=None)
            lbl.bind(texture_size=lambda inst, val: setattr(inst, "width",
                                                            val[0]))
            item.add_widget(dot)
            item.add_widget(lbl)
            self.legend.add_widget(item)
        self.legend.add_widget(Widget())

        self.x_row.clear_widgets()
        shown = labels[::max(1, len(labels) // 5)] if labels else []
        for text in shown:
            self.x_row.add_widget(Label(text=text, font_size=sp(9),
                                        color=TEXT_DIM))
