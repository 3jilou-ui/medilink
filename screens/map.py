"""Carte prototype : patient localisé + structures de santé proches."""
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from utils.constants import CYAN, SUCCESS, TEXT_DIM
from widgets.base import CardBox, Spacer
from widgets.facility_card import FacilityCard
from widgets.icons import Icon
from widgets.map_widget import MockMapWidget

from . import MediScreen


class MapScreen(MediScreen):
    back_to = "home"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Carte"))

        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        map_card = CardBox(padding=dp(6), size_hint_y=None, height=dp(330))
        self.map = MockMapWidget()
        map_card.add_widget(self.map)
        content.add_widget(map_card)

        loc_card = CardBox(orientation="horizontal", size_hint_y=None,
                           height=dp(64), spacing=dp(10))
        pin = Icon(name="pin", color=CYAN, size=(dp(26), dp(26)),
                   size_hint=(None, None))
        pin.pos_hint = {"center_y": 0.5}
        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        texts.add_widget(Label(text="Patient localisé", font_size=sp(14),
                               bold=True, color=SUCCESS, halign="left",
                               size_hint_y=None, height=dp(22)))
        self.address_label = Label(text="", font_size=sp(11),
                                   color=TEXT_DIM, halign="left",
                                   size_hint_y=None, height=dp(18))
        texts.add_widget(self.address_label)
        loc_card.add_widget(pin)
        loc_card.add_widget(texts)
        content.add_widget(loc_card)

        content.add_widget(Label(text="Structures de santé à proximité",
                                 font_size=sp(14), bold=True, halign="left",
                                 size_hint_y=None, height=dp(22)))
        self.facility_list = GridLayout(cols=1, spacing=dp(10),
                                        size_hint_y=None)
        self.facility_list.bind(
            minimum_height=self.facility_list.setter("height"))
        content.add_widget(self.facility_list)
        content.add_widget(Spacer(6))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def refresh(self):
        state = self.state
        lat, lon, address = state.services.location.get_current_location()
        self.address_label.text = address
        ranked = state.services.facilities.find_facilities((lat, lon))
        self.map.set_data((lat, lon, address), ranked)
        self.facility_list.clear_widgets()
        for fac, dist in ranked:
            self.facility_list.add_widget(FacilityCard(fac, dist))
