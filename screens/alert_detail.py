"""Détail complet d'une alerte médicale."""
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from models.alert import AlertStatus, Severity
from models.emergency import STATE_LABELS
from utils.constants import (DANGER, METRIC_LABELS, SUCCESS, TEXT_DIM,
                             WARNING)
from utils.formatting import fmt_datetime
from widgets.base import CardBox, Spacer
from widgets.status_badge import StatusBadge

from . import MediScreen


class AlertDetailScreen(MediScreen):
    back_to = "alerts"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alert_id = None

    def set_params(self, alert_id=None, **_):
        self.alert_id = alert_id

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Détail de l'alerte"))
        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        self.content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                                  padding=(dp(14), dp(10), dp(14), dp(14)))
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _row(self, card, label, value, color=None):
        row = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(8))
        row.add_widget(Label(text=label, font_size=sp(12), color=TEXT_DIM,
                             halign="left", size_hint_x=None,
                             width=dp(130)))
        row.add_widget(Label(text=value, font_size=sp(12), bold=True,
                             color=color or (1, 1, 1, 1), halign="left"))
        card.add_widget(row)

    def refresh(self):
        self.content.clear_widgets()
        alert = self.state.alert_manager.get(self.alert_id)
        if alert is None:
            self.content.add_widget(Label(text="Alerte introuvable.",
                                          font_size=sp(14)))
            return
        color = DANGER if alert.severity == Severity.CRITICAL else WARNING

        head = CardBox(spacing=dp(6))
        head.add_widget(Label(text="ALERTE MÉDICALE", font_size=sp(17),
                              bold=True, color=color, halign="left",
                              size_hint_y=None, height=dp(26)))
        row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
        row.add_widget(Label(text=METRIC_LABELS.get(alert.parameter,
                                                    alert.parameter),
                             font_size=sp(14), bold=True, halign="left"))
        row.add_widget(Label(text=alert.value, font_size=sp(14), bold=True,
                             color=color, halign="left", size_hint_x=None,
                             width=dp(90)))
        row.add_widget(Widget())
        row.add_widget(StatusBadge(status=("CRITICAL" if alert.severity
                                            == Severity.CRITICAL
                                            else "WARNING")))
        head.add_widget(row)
        self.content.add_widget(head)

        info = CardBox(spacing=dp(6))
        info.add_widget(Label(text="Informations", font_size=sp(14),
                              bold=True, halign="left", size_hint_y=None,
                              height=dp(22)))
        self._row(info, "Patient", alert.patient_name or "--")
        self._row(info, "Heure", fmt_datetime(alert.timestamp))
        self._row(info, "Statut", alert.status.value)
        loc = (f"{alert.location[0]:.4f}, {alert.location[1]:.4f}"
               if alert.location else "Non localisée")
        self._row(info, "Localisation", loc)
        self._row(info, "Structure proche", alert.facility or "--")
        self.content.add_widget(info)

        em = self.state.services.emergency_manager
        if em.alert is alert:
            em_card = CardBox(spacing=dp(6))
            em_card.add_widget(Label(text="Protocole d'urgence",
                                     font_size=sp(14), bold=True,
                                     halign="left", size_hint_y=None,
                                     height=dp(22)))
            self._row(em_card, "État", STATE_LABELS.get(em.state,
                                                        em.state.value),
                      color=color)
            self._row(em_card, "Ambulance", em.ambulance_status)
            self._row(em_card, "Assistant IA",
                      "Actif" if em.state.value == "AI_ASSISTANCE_ACTIVE"
                      else "Inactif",
                      color=SUCCESS if em.state.value == "AI_ASSISTANCE_ACTIVE"
                      else TEXT_DIM)
            if alert.status == AlertStatus.CANCELLED:
                self._row(em_card, "Annulation", alert.reason or "--",
                          color=WARNING)
            em_card.add_widget(Spacer(2))
            em_card.add_widget(Label(text="Chronologie", font_size=sp(12),
                                     bold=True, halign="left",
                                     size_hint_y=None, height=dp(18)))
            for entry in em.timeline:
                trow = BoxLayout(size_hint_y=None, height=dp(20),
                                 spacing=dp(8))
                trow.add_widget(Label(text=entry.time_label,
                                      font_size=sp(11), color=TEXT_DIM,
                                      halign="left", size_hint_x=None,
                                      width=dp(48)))
                trow.add_widget(Label(text=entry.label, font_size=sp(11),
                                      halign="left"))
                em_card.add_widget(trow)
            self.content.add_widget(em_card)

        buttons = CardBox(spacing=dp(8), bg_color=(0, 0, 0, 0),
                          border_color=(0, 0, 0, 0))
        loc_btn = Factory.MediButton(text="Voir la localisation")
        loc_btn.bind(on_release=lambda inst: self.go("map"))
        ai_btn = Factory.GhostButton(text="Ouvrir l'assistant")
        ai_btn.bind(on_release=lambda inst: self.go("assistant"))
        buttons.add_widget(loc_btn)
        buttons.add_widget(ai_btn)
        if alert.status == AlertStatus.ACTIVE:
            cancel = Factory.DangerButton(text="Annuler l'alerte")
            cancel.bind(on_release=lambda inst: self._cancel(alert))
            buttons.add_widget(cancel)
        self.content.add_widget(buttons)
        self.content.add_widget(Spacer(6))

    def _cancel(self, alert):
        em = self.state.services.emergency_manager
        if em.alert is alert and em.is_active:
            self.go("emergency")
        else:
            self.state.alert_manager.close_alert(
                alert, reason="Valeur incorrecte / mesure suspecte")
            self.refresh()
