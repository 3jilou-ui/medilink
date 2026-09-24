"""Liste des alertes avec filtres."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from widgets.alert_card import AlertCard
from widgets.base import Spacer

from . import MediScreen

FILTERS = [("all", "Toutes"), ("critical", "Critiques"),
           ("warning", "Attention"), ("resolved", "Résolues"),
           ("cancelled", "Annulées")]


class AlertsScreen(MediScreen):
    back_to = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter = "all"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Alertes"))

        chips = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6),
                          padding=(dp(14), 0))
        for key, label in FILTERS:
            chip = Factory.ChipButton(text=label, group="alert_filter")
            chip.state = "down" if key == self.filter else "normal"
            chip.bind(on_release=lambda inst, k=key: self._set_filter(k))
            chips.add_widget(chip)
        chips.add_widget(Widget())
        root.add_widget(chips)

        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        self.content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                                  padding=(dp(14), dp(10), dp(14), dp(14)))
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _set_filter(self, key):
        self.filter = key
        self.refresh()

    def refresh(self):
        self.content.clear_widgets()
        alerts = self.state.alert_manager.filtered(self.filter)
        if not alerts:
            self.content.add_widget(Label(
                text="Aucune alerte pour ce filtre.",
                font_size=sp(13), color=(0.56, 0.66, 0.77, 1),
                size_hint_y=None, height=dp(40)))
        for alert in alerts:
            self.content.add_widget(
                AlertCard(alert,
                          callback=lambda aid: self.go("alert_detail",
                                                       alert_id=aid)))
        self.content.add_widget(Spacer(6))
