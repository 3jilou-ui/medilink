"""Carte de structure de santé (distance, urgences)."""
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from utils.constants import DANGER, SUCCESS, TEXT_DIM
from utils.formatting import fmt_distance
from widgets.base import CardBox
from widgets.icons import Icon


class FacilityCard(CardBox):
    def __init__(self, facility, distance_km, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(92)

        row1 = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
        icon_name = {"Hôpital": "cross", "Clinique": "home",
                     "Centre médical": "cross"}.get(facility.type, "cross")
        row1.add_widget(Icon(name=icon_name,
                             color=DANGER if facility.emergency_available
                             else SUCCESS,
                             size=(dp(20), dp(20))))
        name = Label(text=facility.name, font_size=sp(14), bold=True,
                     halign="left", valign="middle", size_hint_x=None)
        name.bind(texture_size=lambda inst, val: setattr(inst, "width",
                                                         val[0]))
        row1.add_widget(name)
        row1.add_widget(Widget())
        dist = Label(text=fmt_distance(distance_km), font_size=sp(16),
                     bold=True, color=SUCCESS, halign="right",
                     size_hint_x=None)
        dist.bind(texture_size=lambda inst, val: setattr(inst, "width",
                                                         val[0]))
        row1.add_widget(dist)

        row2 = Label(text=f"{facility.type} — {facility.phone}",
                     font_size=sp(11), color=TEXT_DIM, halign="left",
                     size_hint_y=None, height=dp(18))

        row3 = Label(text=("Urgences 24h/24" if facility.emergency_available
                           else "Sans service d'urgences"),
                     font_size=sp(11), bold=True,
                     color=SUCCESS if facility.emergency_available else TEXT_DIM,
                     halign="left", size_hint_y=None, height=dp(18))

        self.add_widget(row1)
        self.add_widget(row2)
        self.add_widget(row3)
