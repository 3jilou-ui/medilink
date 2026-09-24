"""Historique multi-paramètres sur 24 h / 7 j / 30 j."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utils.constants import METRIC_COLORS, METRIC_LABELS
from widgets.base import CardBox
from widgets.graph import LineGraph

from . import MediScreen

PERIOD_LABELS = [("24h", "24 H"), ("7d", "7 J"), ("30d", "30 J")]
HISTORY_METRICS = ["heart_rate", "spo2", "glucose", "temperature",
                   "blood_pressure"]


class HistoryScreen(MediScreen):
    back_to = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.period = "24h"
        self.graphs = {}

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Historique"))

        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        periods = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        for key, label in PERIOD_LABELS:
            chip = Factory.ChipButton(text=label, group="hist_period")
            chip.state = "down" if key == self.period else "normal"
            chip.bind(on_release=lambda inst, k=key: self._set_period(k))
            periods.add_widget(chip)
        periods.add_widget(Widget())
        content.add_widget(periods)

        for metric in HISTORY_METRICS:
            card = CardBox(spacing=dp(6))
            title = Label(text=METRIC_LABELS.get(metric, metric),
                          font_size=sp(13), bold=True, halign="left",
                          size_hint_y=None, height=dp(20))
            graph = LineGraph(height=150)
            card.add_widget(title)
            card.add_widget(graph)
            content.add_widget(card)
            self.graphs[metric] = graph

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _set_period(self, period):
        self.period = period
        self.refresh()

    def refresh(self):
        hist = self.state.services.data_provider.get_history(self.period)
        for metric, graph in self.graphs.items():
            color = METRIC_COLORS.get(metric, (1, 1, 1, 1))
            graph.set_data(hist["labels"],
                           [(METRIC_LABELS.get(metric, metric), color,
                             hist["points"].get(metric, []))])
