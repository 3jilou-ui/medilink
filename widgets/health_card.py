"""Carte de paramètre de santé (accueil) : icône, titre, valeur, statut."""
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from utils.constants import (METRIC_COLORS, METRIC_ICONS, METRIC_LABELS,
                             METRIC_UNITS, STATUS_COLORS)
from utils.formatting import fmt_value
from widgets.base import CardBox
from widgets.icons import Icon
from widgets.status_badge import StatusBadge


class HealthCard(CardBox):
    metric = StringProperty("heart_rate")
    status = StringProperty("NORMAL")
    callback = ObjectProperty(None, allownone=True)

    def __init__(self, metric="heart_rate", **kwargs):
        super().__init__(**kwargs)
        self.metric = metric
        self.padding = dp(12)
        color = METRIC_COLORS.get(metric, STATUS_COLORS["NORMAL"])

        header = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
        self.icon = Icon(name=METRIC_ICONS.get(metric, "heart"),
                         color=color, size=(dp(22), dp(22)))
        title = Label(text=METRIC_LABELS.get(metric, metric),
                      font_size=sp(12), color=(0.72, 0.82, 0.92, 1),
                      halign="left", valign="middle", size_hint_x=None)
        title.bind(texture_size=lambda inst, val: setattr(
            inst, "width", val[0]))
        header.add_widget(self.icon)
        header.add_widget(title)
        header.add_widget(Widget())

        value_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        self.value_label = Label(text="--", font_size=sp(26), bold=True,
                                 size_hint_x=None)
        self.value_label.bind(texture_size=lambda inst, val: setattr(
            inst, "width", val[0]))
        self.unit_label = Label(text=METRIC_UNITS.get(metric, ""),
                                font_size=sp(12), color=(0.56, 0.66, 0.77, 1),
                                halign="left", valign="bottom",
                                size_hint_x=None)
        self.unit_label.bind(texture_size=lambda inst, val: setattr(
            inst, "width", val[0]))
        value_row.add_widget(self.value_label)
        value_row.add_widget(self.unit_label)
        value_row.add_widget(Widget())

        self.badge = StatusBadge(status=self.status)

        self.add_widget(header)
        self.add_widget(value_row)
        self.add_widget(self.badge)
        self.bind(status=self._on_status)
        self.size_hint_y = None
        self.height = dp(132)

    def _on_status(self, *args):
        self.badge.status = self.status

    def update(self, health_data, status):
        value = health_data.value_for(self.metric)
        self.value_label.text = fmt_value(self.metric, value)
        self.status = status

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback(self.metric)
            return True
        return super().on_touch_down(touch)
