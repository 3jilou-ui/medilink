"""Carte d'alerte pour la liste des alertes."""
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from models.alert import AlertStatus, Severity
from utils.constants import (DANGER, METRIC_LABELS, STATUS_COLORS, TEXT_DIM,
                             WARNING)
from widgets.base import CardBox

STATUS_FR = {
    AlertStatus.ACTIVE: "En cours",
    AlertStatus.RESOLVED: "Résolue",
    AlertStatus.CANCELLED: "Annulée",
}


class AlertCard(CardBox):
    alert_id = StringProperty("")
    callback = ObjectProperty(None, allownone=True)

    def __init__(self, alert, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.alert_id = alert.id
        self.callback = callback
        self.size_hint_y = None
        self.height = dp(96)
        self.padding = (dp(16), dp(10))
        color = DANGER if alert.severity == Severity.CRITICAL else WARNING

        # bande latérale colorée
        with self.canvas.before:
            self._stripe_color = Color(*color)
            self._stripe = Rectangle(pos=self.pos, size=(dp(4), self.height))
        self.bind(pos=self._sync_stripe, size=self._sync_stripe)

        row1 = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(8))
        row1.add_widget(Label(text=alert.time_label, font_size=sp(12),
                              bold=True, color=color, halign="left",
                              size_hint_x=None, width=dp(50)))
        sev = Label(text=("Critique" if alert.severity == Severity.CRITICAL
                          else "Attention"),
                    font_size=sp(12), bold=True, color=color, halign="left")
        row1.add_widget(sev)
        row1.add_widget(Widget())
        row1.add_widget(Label(text=STATUS_FR.get(alert.status, ""),
                              font_size=sp(11), color=TEXT_DIM,
                              halign="right", size_hint_x=None, width=dp(70)))

        row2 = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(6))
        row2.add_widget(Label(text=alert.patient_name or "Patient",
                              font_size=sp(13), bold=True, halign="left"))
        row2.add_widget(Widget())

        row3 = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(6))
        row3.add_widget(Label(text=METRIC_LABELS.get(alert.parameter,
                                                     alert.parameter),
                              font_size=sp(12), color=TEXT_DIM, halign="left"))
        row3.add_widget(Label(text=alert.value, font_size=sp(12), bold=True,
                              color=color, halign="left", size_hint_x=None,
                              width=dp(80)))
        row3.add_widget(Widget())

        self.add_widget(row1)
        self.add_widget(row2)
        self.add_widget(row3)

    def _sync_stripe(self, *args):
        self._stripe.pos = (self.x + dp(2), self.y + dp(6))
        self._stripe.size = (dp(4), self.height - dp(12))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback(self.alert_id)
            return True
        return super().on_touch_down(touch)
