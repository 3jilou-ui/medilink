"""Écran d'urgence : alerte critique, chronologie, ambulance, annulation."""
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from models.emergency import ACTIVE_STATES, EmergencyState
from utils.constants import (CYAN, DANGER, DANGER_DARK, METRIC_LABELS,
                             SUCCESS, TEXT_DIM, WARNING)
from utils.formatting import fmt_duration, fmt_time
from widgets.base import CardBox, Spacer
from widgets.emergency_banner import EmergencyBanner
from widgets.facility_card import FacilityCard
from widgets.icons import Icon

from . import MediScreen

FALSE_READING_OPTIONS = [
    "Bracelet mal positionné",
    "Capteur perturbé",
    "Valeur manifestement incorrecte",
    "Nouvelle mesure",
]


class EmergencyScreen(MediScreen):
    back_to = "home"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Urgence", back=False))

        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        # bannière pulsante
        self.banner = EmergencyBanner()
        content.add_widget(self.banner)

        # fiche synthèse
        info = CardBox(spacing=dp(6))
        self.info_rows = {}
        info.add_widget(Label(text="Synthèse de l'alerte", font_size=sp(14),
                              bold=True, halign="left", size_hint_y=None,
                              height=dp(22)))
        for key, label in (("patient", "Patient"),
                           ("issue", "Problème détecté"),
                           ("value", "Valeur actuelle"),
                           ("time", "Heure"),
                           ("status", "Statut")):
            row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
            row.add_widget(Label(text=label, font_size=sp(12),
                                 color=TEXT_DIM, halign="left",
                                 size_hint_x=None, width=dp(120)))
            val = Label(text="--", font_size=sp(13), bold=True,
                        halign="left")
            row.add_widget(val)
            info.add_widget(row)
            self.info_rows[key] = val
        content.add_widget(info)

        # structure de santé
        self.facility_card = CardBox(spacing=dp(8))
        self.facility_title = Label(text="Patient localisé",
                                     font_size=sp(14), bold=True,
                                     color=SUCCESS, halign="left",
                                     size_hint_y=None, height=dp(22))
        self.facility_body = GridLayout(cols=1, spacing=dp(8),
                                         size_hint_y=None)
        self.facility_body.bind(
            minimum_height=self.facility_body.setter("height"))
        self.facility_card.add_widget(self.facility_title)
        self.facility_card.add_widget(self.facility_body)
        content.add_widget(self.facility_card)

        # ambulance
        self.amb_card = CardBox(spacing=dp(6))
        amb_head = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
        amb_head.add_widget(Icon(name="ambulance", color=DANGER,
                                 size=(dp(22), dp(22))))
        amb_head.add_widget(Label(text="Secours", font_size=sp(14),
                                  bold=True, halign="left"))
        amb_head.add_widget(Widget())
        self.amb_status = Label(text="--", font_size=sp(13), bold=True,
                                color=WARNING, halign="right",
                                valign="middle", size_hint_x=None,
                                width=dp(170), text_size=(dp(170), None))
        amb_head.add_widget(self.amb_status)
        self.amb_eta = Label(text="", font_size=sp(12), color=CYAN,
                             halign="left", size_hint_y=None, height=dp(20))
        self.amb_card.add_widget(amb_head)
        self.amb_card.add_widget(self.amb_eta)
        content.add_widget(self.amb_card)

        # chronologie
        tl_card = CardBox(spacing=dp(6))
        tl_card.add_widget(Label(text="Chronologie", font_size=sp(14),
                                 bold=True, halign="left",
                                 size_hint_y=None, height=dp(22)))
        self.timeline_list = GridLayout(cols=1, spacing=dp(4),
                                        size_hint_y=None)
        self.timeline_list.bind(
            minimum_height=self.timeline_list.setter("height"))
        tl_card.add_widget(self.timeline_list)
        content.add_widget(tl_card)

        # boutons d'action
        actions = CardBox(spacing=dp(10), bg_color=(0, 0, 0, 0),
                          border_color=(0, 0, 0, 0))
        data_btn = Factory.MediButton(text="VOIR LES DONNÉES")
        data_btn.bind(on_release=lambda i: self._view_data())
        loc_btn = Factory.GhostButton(text="LOCALISER")
        loc_btn.bind(on_release=lambda i: self.go("map"))
        ai_btn = Factory.GhostButton(text="OUVRIR L'ASSISTANT")
        ai_btn.bind(on_release=lambda i: self.go("assistant"))
        cancel_btn = Factory.DangerButton(text="ANNULER L'ALERTE")
        cancel_btn.height = dp(56)
        cancel_btn.bind(on_release=lambda i: self._show_confirm())
        actions.add_widget(data_btn)
        actions.add_widget(loc_btn)
        actions.add_widget(ai_btn)
        actions.add_widget(cancel_btn)
        self.actions_card = actions
        content.add_widget(actions)

        # panneau de confirmation
        self.confirm_card = CardBox(spacing=dp(10), bg_color=DANGER_DARK)
        self.confirm_card.add_widget(Label(
            text="Êtes-vous certain que cette alerte est incorrecte ?",
            font_size=sp(14), bold=True, halign="center",
            size_hint_y=None, height=dp(40)))
        confirm_btn = Factory.DangerButton(text="CONFIRMER L'ANNULATION")
        confirm_btn.bind(on_release=lambda i: self._confirm_cancel())
        back_btn = Factory.GhostButton(text="RETOUR")
        back_btn.bind(on_release=lambda i: self._hide_confirm())
        self.confirm_card.add_widget(confirm_btn)
        self.confirm_card.add_widget(back_btn)
        content.add_widget(self.confirm_card)

        # panneau "alerte annulée / résolue"
        self.done_card = CardBox(spacing=dp(8))
        self.done_title = Label(text="ALERTE ANNULÉE", font_size=sp(18),
                                bold=True, color=SUCCESS, halign="center",
                                size_hint_y=None, height=dp(28))
        self.done_reason = Label(text="", font_size=sp(12), color=TEXT_DIM,
                                 halign="center", size_hint_y=None,
                                 height=dp(34))
        home_btn = Factory.MediButton(text="Retour au monitoring")
        home_btn.bind(on_release=lambda i: self.go("home"))
        self.done_card.add_widget(self.done_title)
        self.done_card.add_widget(self.done_reason)
        self.done_card.add_widget(home_btn)
        content.add_widget(self.done_card)

        # lecture incorrecte
        false_card = CardBox(spacing=dp(8))
        false_card.add_widget(Label(text="Valeur incorrecte ?",
                                    font_size=sp(14), bold=True,
                                    halign="left", size_hint_y=None,
                                    height=dp(22)))
        opts = GridLayout(cols=2, spacing=dp(8), size_hint_y=None,
                          height=dp(88))
        for opt in FALSE_READING_OPTIONS:
            btn = Factory.SmallButton(text=opt)
            btn.bind(on_release=lambda i, o=opt: self._false_reading(o))
            opts.add_widget(btn)
        false_card.add_widget(opts)
        self.false_note = Label(text="", font_size=sp(11), color=CYAN,
                                halign="left", size_hint_y=None,
                                height=dp(32))
        false_card.add_widget(self.false_note)
        content.add_widget(false_card)
        content.add_widget(Spacer(6))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _view_data(self):
        em = self.state.services.emergency_manager
        metric = em.alert.parameter if em.alert else "heart_rate"
        self.go("health_detail", metric=metric)

    def _show_confirm(self):
        self.confirm_card.disabled = False
        self.confirm_card.opacity = 1
        self._confirm_visible = True
        self.refresh()

    def _hide_confirm(self):
        self._confirm_visible = False
        self.refresh()

    def _confirm_cancel(self):
        self._confirm_visible = False
        self.state.cancel_emergency()

    def _false_reading(self, option):
        if option == "Nouvelle mesure":
            self.false_note.text = "Nouvelle mesure en cours..."
            self.state.remeasure()
            Clock.schedule_once(lambda dt: self._after_remeasure(), 1.2)
        else:
            self.false_note.text = (f"Signalement enregistré : {option}. "
                                    "Utilisez « Nouvelle mesure » après "
                                    "avoir corrigé le bracelet.")

    def _after_remeasure(self):
        self.false_note.text = ("Nouvelle mesure reçue. Si les valeurs sont "
                                "normales, l'alerte sera résolue "
                                "automatiquement.")

    # ------------------------------------------------------------------
    def refresh(self):
        em = self.state.services.emergency_manager
        alert = em.alert
        active = em.state in ACTIVE_STATES

        self.banner.start_pulsing() if active else self.banner.stop_pulsing()
        if em.state == EmergencyState.CANCELLED:
            self.banner.title = "ALERTE ANNULÉE"
            self.banner.subtitle = em.cancel_reason or "Alerte annulée"
        elif em.state == EmergencyState.RESOLVED:
            self.banner.title = "ALERTE RÉSOLUE"
            self.banner.subtitle = "Retour à des valeurs normales"
        else:
            self.banner.title = "ALERTE MÉDICALE"
            self.banner.subtitle = "Intervention en cours"

        if alert:
            self.info_rows["patient"].text = alert.patient_name or "--"
            self.info_rows["issue"].text = METRIC_LABELS.get(
                alert.parameter, alert.parameter)
            hd = self.state.health_data
            if hd:
                from utils.formatting import fmt_value
                self.info_rows["value"].text = fmt_value(
                    alert.parameter, hd.value_for(alert.parameter))
            self.info_rows["time"].text = fmt_time(alert.timestamp)
        from models.emergency import STATE_LABELS
        self.info_rows["status"].text = ("INTERVENTION EN COURS" if active
                                         else STATE_LABELS.get(em.state, "--"))

        # structure de santé
        self.facility_body.clear_widgets()
        if em.facility is not None and em.location is not None:
            self.facility_title.text = ("Patient localisé — structure de "
                                        "santé identifiée")
            self.facility_body.add_widget(
                FacilityCard(em.facility, em.distance_km or 0.0))
        else:
            self.facility_title.text = "Localisation du patient en cours..."

        # ambulance
        self.amb_status.text = em.ambulance_status
        self.amb_eta.text = (f"Temps estimé : {fmt_duration(em.eta_seconds)}"
                             if em.eta_seconds else "")

        # chronologie
        self.timeline_list.clear_widgets()
        for entry in em.timeline:
            row = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(8))
            row.add_widget(Label(text=entry.time_label, font_size=sp(11),
                                 color=CYAN, bold=True, halign="left",
                                 size_hint_x=None, width=dp(46)))
            row.add_widget(Label(text="\u2022", font_size=sp(13), color=CYAN,
                                 halign="left", size_hint_x=None,
                                 width=dp(12)))
            row.add_widget(Label(text=entry.label, font_size=sp(12),
                                 halign="left"))
            self.timeline_list.add_widget(row)
        if not em.timeline:
            self.timeline_list.add_widget(Label(
                text="Aucun événement.", font_size=sp(11), color=TEXT_DIM,
                size_hint_y=None, height=dp(20)))

        # visibilité des panneaux
        confirm_visible = getattr(self, "_confirm_visible", False) and active
        self.confirm_card.size_hint_y = None
        self.confirm_card.height = dp(150) if confirm_visible else 0
        self.confirm_card.opacity = 1 if confirm_visible else 0
        self.confirm_card.disabled = not confirm_visible

        done_visible = em.state in (EmergencyState.CANCELLED,
                                    EmergencyState.RESOLVED)
        self.done_card.height = dp(150) if done_visible else 0
        self.done_card.opacity = 1 if done_visible else 0
        self.done_card.disabled = not done_visible
        if done_visible:
            if em.state == EmergencyState.CANCELLED:
                self.done_title.text = "ALERTE ANNULÉE"
                self.done_reason.text = ("Motif : " + (em.cancel_reason
                                                       or "--"))
            else:
                self.done_title.text = "ALERTE RÉSOLUE"
                self.done_reason.text = "Valeurs revenues à la normale."

        self.actions_card.height = dp(220) if active else 0
        self.actions_card.opacity = 1 if active else 0
        self.actions_card.disabled = not active
