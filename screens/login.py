"""Écran de connexion (authentification simulée)."""
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import config
from utils.constants import CYAN, DANGER, PRIMARY, TEXT_DIM
from utils.validators import validate_email
from widgets.base import CardBox, Spacer
from widgets.icons import Icon

from . import MediScreen


class LoginScreen(MediScreen):
    back_to = "login"

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(24),
                         spacing=dp(10))
        root.add_widget(Spacer(30))

        logo_wrap = FloatLayout(size_hint_y=None, height=dp(110))
        with logo_wrap.canvas:
            Color(PRIMARY[0], PRIMARY[1], PRIMARY[2], 0.15)
            self._logo_bg = Ellipse(pos=(dp(120), 0), size=(dp(110), dp(110)))
            Color(PRIMARY[0], PRIMARY[1], PRIMARY[2], 0.35)
            self._logo_ring = Line(circle=(dp(175), dp(55), dp(46)),
                                   width=1.4)

        def _sync_logo(*_args):
            cx = root.center_x
            cy = logo_wrap.center_y
            self._logo_bg.pos = (cx - dp(55), cy - dp(55))
            self._logo_ring.circle = (cx, cy, dp(46))

        logo_wrap.bind(pos=_sync_logo, size=_sync_logo)
        root.bind(pos=_sync_logo, size=_sync_logo)
        Clock.schedule_once(lambda dt: _sync_logo(), 0.1)
        logo = Icon(name="heart", color=CYAN, size=(dp(52), dp(52)),
                    size_hint=(None, None))
        logo.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        logo_wrap.add_widget(logo)
        root.add_widget(logo_wrap)

        root.add_widget(Label(text="MEDILINK", font_size=sp(30), bold=True))
        root.add_widget(Label(text="Surveillance médicale intelligente",
                              font_size=sp(13), color=TEXT_DIM))
        root.add_widget(Label(text="Votre santé, notre priorité",
                              font_size=sp(12), color=CYAN))
        root.add_widget(Spacer(24))

        card = CardBox(spacing=dp(12))
        from kivy.factory import Factory
        self.email = Factory.MediTextInput(
            hint_text="Email", text="demo@medilink.tn",
            input_filter=None)
        self.password = Factory.MediTextInput(
            hint_text="Mot de passe", text="demo", password=True)
        self.error = Label(text="", color=DANGER, font_size=sp(12),
                           size_hint_y=None, height=dp(18))
        connect = Factory.MediButton(text="Se connecter")
        connect.bind(on_release=lambda inst: self._login())
        demo = Factory.GhostButton(text="Mode démonstration")
        demo.bind(on_release=lambda inst: self.go("home"))
        card.add_widget(self.email)
        card.add_widget(self.password)
        card.add_widget(self.error)
        card.add_widget(connect)
        card.add_widget(demo)
        root.add_widget(card)
        root.add_widget(Spacer(14))
        disclaimer = Label(text=config.DISCLAIMER, font_size=sp(10),
                           color=TEXT_DIM, halign="center", valign="middle",
                           size_hint_y=None, height=dp(44))
        disclaimer.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        root.add_widget(disclaimer)
        self.add_widget(root)

    def _login(self):
        if not validate_email(self.email.text):
            self.error.text = "Adresse email invalide."
            return
        if not self.password.text.strip():
            self.error.text = "Mot de passe requis."
            return
        self.error.text = ""
        self.go("home")
