"""Détail d'un paramètre de santé (réutilisable pour toutes les métriques)."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utils.constants import METRIC_COLORS, METRIC_LABELS, METRIC_UNITS
from utils.formatting import fmt_time, fmt_value
from utils.thresholds import ThresholdEngine
from widgets.base import CardBox, Spacer
from widgets.graph import LineGraph
from widgets.status_badge import StatusBadge

from . import MediScreen

PERIOD_LABELS = [("24h", "24 H"), ("7d", "7 J"), ("30d", "30 J")]


class HealthDetailScreen(MediScreen):
    back_to = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metric = "heart_rate"
        self.period = "24h"

    def set_params(self, metric=None, **_):
        if metric:
            self.metric = metric

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header(back=True))

        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        # valeur actuelle
        value_card = CardBox(spacing=dp(6))
        self.title_label = Label(text="", font_size=sp(13),
                                 color=(0.72, 0.82, 0.92, 1), halign="left",
                                 size_hint_y=None, height=dp(20))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.value_label = Label(text="--", font_size=sp(34), bold=True,
                                 size_hint_x=None)
        self.value_label.bind(texture_size=lambda i, v: setattr(i, "width",
                                                                 v[0]))
        self.unit_label = Label(text="", font_size=sp(13),
                                color=(0.56, 0.66, 0.77, 1), halign="left",
                                valign="bottom", size_hint_x=None)
        self.unit_label.bind(texture_size=lambda i, v: setattr(i, "width",
                                                                v[0]))
        row.add_widget(self.value_label)
        row.add_widget(self.unit_label)
        row.add_widget(Widget())
        self.badge = StatusBadge()
        row.add_widget(self.badge)
        self.range_label = Label(text="", font_size=sp(11),
                                 color=(0.56, 0.66, 0.77, 1), halign="left",
                                 size_hint_y=None, height=dp(16))
        value_card.add_widget(self.title_label)
        value_card.add_widget(row)
        value_card.add_widget(self.range_label)
        content.add_widget(value_card)

        # périodes
        periods = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        self.period_chips = {}
        for key, label in PERIOD_LABELS:
            chip = Factory.ChipButton(text=label, group="hd_period")
            chip.state = "down" if key == self.period else "normal"
            chip.bind(on_release=lambda inst, k=key: self._set_period(k))
            self.period_chips[key] = chip
            periods.add_widget(chip)
        periods.add_widget(Widget())
        content.add_widget(periods)

        self.graph = LineGraph(height=190)
        content.add_widget(self.graph)

        # mesures récentes
        recent_card = CardBox(spacing=dp(6))
        recent_card.add_widget(Label(text="Mesures récentes",
                                     font_size=sp(14), bold=True,
                                     halign="left", size_hint_y=None,
                                     height=dp(22)))
        self.recent_list = GridLayout(cols=1, spacing=dp(4),
                                      size_hint_y=None)
        self.recent_list.bind(minimum_height=self.recent_list.setter("height"))
        recent_card.add_widget(self.recent_list)
        content.add_widget(recent_card)
        content.add_widget(Spacer(6))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _set_period(self, period):
        self.period = period
        self.refresh()

    def refresh(self):
        metric = self.metric
        state = self.state
        self.header_label.text = METRIC_LABELS.get(metric, metric).upper()
        self.title_label.text = METRIC_LABELS.get(metric, metric)
        self.unit_label.text = METRIC_UNITS.get(metric, "")
        hd = state.health_data
        if hd:
            value = hd.value_for(metric)
            self.value_label.text = fmt_value(metric, value)
            self.badge.status = state.statuses.get(metric, "NORMAL")
        self.range_label.text = ("Plage normale (démo) : "
                                 + ThresholdEngine.normal_range(metric))
        hist = state.services.data_provider.get_history(self.period)
        color = METRIC_COLORS.get(metric, (1, 1, 1, 1))
        values = hist["points"].get(metric, [])
        if metric == "blood_pressure":
            values = values  # systolique
        self.graph.set_data(hist["labels"],
                            [(METRIC_LABELS.get(metric, metric), color,
                              values)])
        # mesures récentes (8 dernières)
        self.recent_list.clear_widgets()
        recent = state.services.data_provider.get_history("24h")
        labels = recent["labels"]
        vals = recent["points"].get(metric, [])
        for lbl, val in list(zip(labels, vals))[-8:][::-1]:
            row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
            row.add_widget(Label(text=lbl, font_size=sp(11),
                                 color=(0.56, 0.66, 0.77, 1), halign="left",
                                 size_hint_x=None, width=dp(60)))
            row.add_widget(Label(text=fmt_value(metric, val),
                                 font_size=sp(12), bold=True, halign="left"))
            row.add_widget(Widget())
            self.recent_list.add_widget(row)
