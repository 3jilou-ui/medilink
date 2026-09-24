"""Profil du patient et accès aux réglages."""
from kivy.factory import Factory
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget

import config
from utils.constants import CYAN, DANGER, PRIMARY, SURFACE_LIGHT, TEXT_DIM
from widgets.base import CardBox, Spacer, wrap_label
from widgets.icons import Icon

from . import MediScreen

MENU = [
    ("person", "Informations personnelles", "personal"),
    ("bracelet", "Bracelet", "bracelet"),
    ("cross", "Médecin traitant", "doctor"),
    ("doc", "Historique médical", "medical"),
    ("bell", "Notifications", "notifications"),
    ("gear", "Paramètres", "settings"),
    ("info", "À propos", "about"),
    ("warning", "Centre de démonstration", "demo"),
    ("logout", "Se déconnecter", "logout"),
]


class _MenuRow(BoxLayout):
    def __init__(self, icon_name, label, action, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(10),
                         size_hint_y=None, height=dp(50),
                         padding=(dp(12), 0), **kwargs)
        self.action = action
        with self.canvas.before:
            self._color = Color(*SURFACE_LIGHT)
            self._rect = None
        self.add_widget(Icon(name=icon_name, color=CYAN,
                             size=(dp(20), dp(20)),
                             size_hint=(None, None)))
        self.add_widget(Label(text=label, font_size=sp(13), bold=True,
                              halign="left"))
        self.add_widget(Widget())


class ProfileScreen(MediScreen):
    back_to = "home"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Mon profil"))
        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        # en-tête profil
        head = CardBox(orientation="horizontal", size_hint_y=None,
                       height=dp(84), spacing=dp(12))
        with head.canvas.after:
            Color(PRIMARY[0], PRIMARY[1], PRIMARY[2], 0.25)
            self._av_bg = Ellipse(pos=(dp(14), dp(14)),
                                  size=(dp(56), dp(56)))
            Color(*CYAN)
            self._av_head = Ellipse(pos=(dp(32), dp(42)),
                                    size=(dp(20), dp(20)))
            self._av_body = Ellipse(pos=(dp(26), dp(22)),
                                    size=(dp(32), dp(18)))

        def _sync_avatar(*_args):
            x = head.x + dp(14)
            y = head.y + (head.height - dp(56)) / 2.0
            self._av_bg.pos = (x, y)
            self._av_head.pos = (x + dp(18), y + dp(28))
            self._av_body.pos = (x + dp(12), y + dp(8))

        head.bind(pos=_sync_avatar, size=_sync_avatar)
        _sync_avatar()
        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        patient = self.state.patient
        texts.add_widget(Label(text=patient.name, font_size=sp(16),
                               bold=True, halign="left", size_hint_y=None,
                               height=dp(24)))
        texts.add_widget(Label(text=f"ID : {patient.id} — {patient.age} ans"
                                      f" — {patient.blood_group}",
                               font_size=sp(11), color=TEXT_DIM,
                               halign="left", size_hint_y=None,
                               height=dp(18)))
        head.add_widget(Widget(size_hint_x=None, width=dp(56)))
        head.add_widget(texts)
        content.add_widget(head)

        # menu
        for icon_name, label, action in MENU:
            row = CardBox(orientation="horizontal", size_hint_y=None,
                          height=dp(52), spacing=dp(10),
                          padding=(dp(12), 0))
            row.add_widget(Icon(name=icon_name, color=CYAN,
                                size=(dp(20), dp(20)),
                                size_hint=(None, None)))
            row.add_widget(Label(text=label, font_size=sp(13), bold=True,
                                 halign="left",
                                 color=DANGER if action == "logout"
                                 else (1, 1, 1, 1)))
            row.add_widget(Widget())
            if action == "notifications":
                switch = Switch(active=True, size_hint=(None, None),
                                size=(dp(46), dp(26)))
                switch.pos_hint = {"center_y": 0.5}
                row.add_widget(switch)
            else:
                row.add_widget(Icon(name="back", color=TEXT_DIM,
                                    size=(dp(16), dp(16)),
                                    size_hint=(None, None)))
            row.bind(on_touch_down=lambda inst, touch, a=action:
                     self._row_touch(inst, touch, a))
            content.add_widget(row)

        content.add_widget(wrap_label(config.DISCLAIMER + "\n"
                                      + config.DISCLAIMER_2,
                                      font_size=sp(10), color=TEXT_DIM,
                                      size_hint_y=None, height=dp(48)))
        content.add_widget(Spacer(6))
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _row_touch(self, inst, touch, action):
        if not inst.collide_point(*touch.pos):
            return False
        self._open(action)
        return True

    def _open(self, action):
        patient = self.state.patient
        if action == "bracelet":
            self.go("bracelet")
        elif action == "demo":
            self.go("demo")
        elif action == "logout":
            self.go("login")
        elif action == "personal":
            self._popup("Informations personnelles",
                        f"{patient.name}\n{patient.age} ans — "
                        f"{patient.blood_group}\n{patient.phone}\n"
                        f"Contact d'urgence : {patient.emergency_contact}")
        elif action == "doctor":
            self._popup("Médecin traitant", patient.doctor)
        elif action == "medical":
            n = len(self.state.alert_manager.alerts)
            self._popup("Historique médical",
                        f"{n} alerte(s) enregistrée(s) dans ce prototype.\n"
                        "Aucun dossier médical réel n'est stocké.")
        elif action == "notifications":
            self._popup("Notifications",
                        "Notifications activées pour les alertes critiques "
                        "(simulé dans ce prototype).")
        elif action == "settings":
            self._popup("Paramètres",
                        f"Fournisseurs actifs :\n"
                        f"données={config.DATA_PROVIDER}, "
                        f"bluetooth={config.BLUETOOTH_PROVIDER},\n"
                        f"position={config.LOCATION_PROVIDER}, "
                        f"urgence={config.EMERGENCY_PROVIDER},\n"
                        f"IA={config.AI_PROVIDER}")
        elif action == "about":
            self._popup("À propos",
                        "MediLink — prototype étudiant.\n"
                        + config.DISCLAIMER + "\n" + config.DISCLAIMER_2)

    def _popup(self, title, text):
        Popup(title=title,
              content=Label(text=text, font_size=sp(12), halign="left",
                            valign="top", text_size=(dp(260), None)),
              size_hint=(0.88, 0.5)).open()
