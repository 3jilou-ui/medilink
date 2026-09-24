"""Centre de démonstration : déclenche les scénarios sans matériel."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

import config
from utils.constants import DANGER, TEXT_DIM, WARNING
from widgets.base import CardBox, Spacer, wrap_label

from . import MediScreen


class DemoScreen(MediScreen):
    back_to = "home"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Centre de démonstration"))
        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(wrap_label(
            "Toutes les données sont simulées : aucun bracelet, aucun "
            "GPS, aucune ambulance réelle ne sont sollicités.",
            font_size=sp(12), color=TEXT_DIM, size_hint_y=None,
            height=dp(48)))

        emergency_btn = Factory.DangerButton(text="SIMULER UNE URGENCE",
                                             height=dp(60))
        emergency_btn.bind(on_release=lambda i: self._run("emergency"))
        warning_btn = Factory.MediButton(text="SIMULER UN AVERTISSEMENT",
                                         height=dp(52))
        warning_btn.bg_color = WARNING
        warning_btn.bind(on_release=lambda i: self._run("warning"))
        false_btn = Factory.GhostButton(text="SIMULER UNE LECTURE INCORRECTE",
                                        height=dp(52))
        false_btn.bind(on_release=lambda i: self._run("false_reading"))
        cancel_btn = Factory.GhostButton(text="SIMULER ANNULATION",
                                         height=dp(52))
        cancel_btn.bind(on_release=lambda i: self._run("cancel"))
        reset_btn = Factory.MediButton(text="RESET", height=dp(52))
        reset_btn.bind(on_release=lambda i: self._run("reset"))

        content.add_widget(emergency_btn)
        content.add_widget(warning_btn)
        content.add_widget(false_btn)
        content.add_widget(cancel_btn)
        content.add_widget(reset_btn)

        info = CardBox(spacing=dp(6))
        info.add_widget(Label(text="Scénario d'urgence simulé",
                              font_size=sp(13), bold=True, halign="left",
                              size_hint_y=None, height=dp(20)))
        info.add_widget(wrap_label(
            "FC 145 BPM — SpO2 87 % — 39.5 °C\n"
            "Alerte créée, patient localisé, clinique la plus proche "
            "identifiée, ambulance simulée, assistant IA activé, "
            "annulation possible.",
            halign="left", valign="top", font_size=sp(11), color=TEXT_DIM,
            size_hint_y=None, height=dp(86)))
        content.add_widget(info)
        content.add_widget(wrap_label(config.DISCLAIMER, font_size=sp(10),
                                      color=TEXT_DIM, size_hint_y=None,
                                      height=dp(40)))
        content.add_widget(Spacer(6))
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _run(self, scenario):
        state = self.state
        if scenario == "emergency":
            state.simulate_emergency()
            self.go("home")
        elif scenario == "warning":
            state.simulate_warning()
            self.go("home")
        elif scenario == "false_reading":
            state.simulate_false_reading()
            self.go("home")
        elif scenario == "cancel":
            state.cancel_emergency()
            self.go("home")
        elif scenario == "reset":
            state.reset_demo()
            self.go("home")
