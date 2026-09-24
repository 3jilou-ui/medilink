"""Écran d'accueil : état de santé en un coup d'œil."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import config
from utils.constants import (CYAN, METRIC_COLORS, METRIC_ORDER, PRIMARY,
                             SUCCESS, TEXT_DIM)
from utils.formatting import fmt_time
from widgets.base import CardBox, Spacer, wrap_label
from widgets.graph import LineGraph
from widgets.health_card import HealthCard
from widgets.icons import Icon

from . import IconButton, MediScreen


class HomeScreen(MediScreen):
    back_to = "home"

    def build_ui(self):
        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        self.content = GridLayout(cols=1, spacing=dp(12),
                                  size_hint_y=None,
                                  padding=(dp(14), dp(10), dp(14), dp(14)))
        self.content.bind(minimum_height=self.content.setter("height"))

        # -- en-tête -----------------------------------------------------
        header = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        patient = self.state.patient
        texts.add_widget(Label(text=f"Bonjour, {patient.first_name}",
                               font_size=sp(20), bold=True, halign="left",
                               size_hint_y=None, height=dp(28)))
        texts.add_widget(Label(text="Voici l'état actuel de votre santé",
                               font_size=sp(12), color=TEXT_DIM,
                               halign="left", size_hint_y=None,
                               height=dp(18)))
        self.notif_button = IconButton("bell", icon_size=22, box=44,
                                       on_press_cb=lambda: self.go("alerts"))
        self.notif_badge = Label(text="", color=(1, 1, 1, 1),
                                 font_size=sp(9), bold=True,
                                 size_hint=(None, None), size=(dp(16), dp(16)))
        from kivy.graphics import Color, Ellipse
        with self.notif_badge.canvas.before:
            self._badge_color = Color(1, 0.23, 0.36, 1)
            self._badge_ellipse = Ellipse(pos=(0, 0), size=(dp(16), dp(16)))
        self.notif_badge.bind(pos=self._sync_badge, size=self._sync_badge)
        badge_wrap = BoxLayout(size_hint=(None, None), size=(dp(44), dp(44)))
        self.notif_badge.pos_hint = {"x": 0.62, "y": 0.62}
        badge_wrap.add_widget(self.notif_badge)
        header.add_widget(texts)
        header.add_widget(badge_wrap)
        header.add_widget(self.notif_button)
        self.content.add_widget(header)

        # -- carte bracelet ----------------------------------------------
        self.bracelet_card = CardBox(orientation="horizontal",
                                     size_hint_y=None, height=dp(78),
                                     spacing=dp(12))
        self.bracelet_icon = Icon(name="bracelet", color=CYAN,
                                  size=(dp(34), dp(34)),
                                  size_hint=(None, None))
        self.bracelet_icon.pos_hint = {"center_y": 0.5}
        mid = BoxLayout(orientation="vertical", spacing=dp(2))
        self.bracelet_title = Label(text="Bracelet connecté",
                                    font_size=sp(14), bold=True,
                                    halign="left", size_hint_y=None,
                                    height=dp(22))
        self.bracelet_live = Label(text="• Données en temps réel",
                                   font_size=sp(11), color=SUCCESS,
                                   halign="left", size_hint_y=None,
                                   height=dp(18))
        self.bracelet_sync = Label(text="", font_size=sp(10),
                                   color=TEXT_DIM, halign="left",
                                   size_hint_y=None, height=dp(16))
        mid.add_widget(self.bracelet_title)
        mid.add_widget(self.bracelet_live)
        mid.add_widget(self.bracelet_sync)
        right = BoxLayout(orientation="vertical", spacing=dp(2),
                          size_hint_x=None, width=dp(86))
        self.battery_label = Label(text="78 %", font_size=sp(16), bold=True,
                                   color=SUCCESS, halign="right",
                                   size_hint_y=None, height=dp(24))
        right.add_widget(self.battery_label)
        right.add_widget(Label(text="Batterie", font_size=sp(10),
                               color=TEXT_DIM, halign="right",
                               size_hint_y=None, height=dp(16)))
        right.add_widget(Widget())
        self.bracelet_card.add_widget(self.bracelet_icon)
        self.bracelet_card.add_widget(mid)
        self.bracelet_card.add_widget(right)
        self.bracelet_card.bind(on_touch_down=self._bracelet_touch)
        self.content.add_widget(self.bracelet_card)

        # -- cartes de santé ----------------------------------------------
        self.grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.cards = {}
        for metric in METRIC_ORDER:
            card = HealthCard(metric=metric)
            card.callback = lambda m: self.go("health_detail", metric=m)
            self.cards[metric] = card
            self.grid.add_widget(card)
        self.content.add_widget(self.grid)

        # -- graphique 24 h -------------------------------------------------
        graph_card = CardBox(spacing=dp(8))
        graph_card.add_widget(Label(text="Évolution des paramètres (24 h)",
                                    font_size=sp(14), bold=True,
                                    halign="left", size_hint_y=None,
                                    height=dp(22)))
        self.graph = LineGraph(height=170)
        graph_card.add_widget(self.graph)
        self.content.add_widget(graph_card)

        # -- démo + mentions -------------------------------------------------
        demo_btn = Factory.GhostButton(text="Centre de démonstration")
        demo_btn.bind(on_release=lambda inst: self.go("demo"))
        self.content.add_widget(demo_btn)
        self.content.add_widget(wrap_label(config.DISCLAIMER,
                                           font_size=sp(10), color=TEXT_DIM,
                                           size_hint_y=None, height=dp(40)))
        scroll.add_widget(self.content)
        self.add_widget(scroll)

    # ------------------------------------------------------------------
    def _sync_badge(self, *args):
        self._badge_ellipse.pos = self.notif_badge.pos
        self._badge_ellipse.size = self.notif_badge.size

    def _bracelet_touch(self, inst, touch):
        if inst.collide_point(*touch.pos):
            self.go("bracelet")
            return True
        return False

    def refresh(self):
        state = self.state
        hd = state.health_data
        if hd:
            for metric, card in self.cards.items():
                card.update(hd, state.statuses.get(metric, "NORMAL"))
            hist = state.services.data_provider.get_history("24h")
            self.graph.set_data(
                hist["labels"],
                [("Fréquence cardiaque", METRIC_COLORS["heart_rate"],
                  hist["points"]["heart_rate"]),
                 ("SpO2", METRIC_COLORS["spo2"], hist["points"]["spo2"]),
                 ("Température", METRIC_COLORS["temperature"],
                  hist["points"]["temperature"])],
            )
        bracelet = state.bracelet
        if bracelet:
            connected = bracelet.connected
            self.bracelet_title.text = ("Bracelet connecté" if connected
                                        else "Bracelet déconnecté")
            self.bracelet_live.text = ("• Données en temps réel" if connected
                                       else "• Aucune connexion")
            self.bracelet_live.color = SUCCESS if connected else (1, 0.23,
                                                                  0.36, 1)
            self.bracelet_icon.color = CYAN if connected else TEXT_DIM
            self.bracelet_sync.text = ("Dernière synchronisation : "
                                       + fmt_time(bracelet.last_sync))
            self.battery_label.text = bracelet.battery_label
            self.battery_label.color = (SUCCESS if bracelet.battery > 30
                                        else (1, 0.65, 0.15, 1))
        active = len(state.alert_manager.active_alerts())
        self.notif_badge.text = str(active) if active else ""
        self._badge_color.a = 1.0 if active else 0.0
