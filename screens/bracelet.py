"""Écran du bracelet MediLink."""
from kivy.factory import Factory
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import config
from utils.constants import (CYAN, DANGER, SUCCESS, SURFACE_LIGHT, TEXT_DIM,
                             WARNING)
from utils.formatting import fmt_time
from widgets.base import CardBox, Spacer
from widgets.icons import Icon

from . import MediScreen


class BraceletScreen(MediScreen):
    back_to = "profile"

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(self.make_header("Mon bracelet"))
        scroll = ScrollView(do_scroll_y=True, bar_width=dp(3))
        content = GridLayout(cols=1, spacing=dp(12), size_hint_y=None,
                             padding=(dp(14), dp(10), dp(14), dp(14)))
        content.bind(minimum_height=content.setter("height"))

        # carte principale avec illustration canvas
        head = CardBox(spacing=dp(8), size_hint_y=None, height=dp(150))
        with head.canvas.after:
            Color(*SURFACE_LIGHT)
            self._ill_bg = Ellipse(pos=(dp(140), dp(6)),
                                   size=(dp(52), dp(52)))
            Color(*CYAN)
            self._ill_ring = Line(circle=(dp(166), dp(32), dp(20)), width=1.6)
            self._ill_top = Line(rectangle=[dp(158), dp(0), dp(16), dp(10)],
                                 width=1.2)
            self._ill_bot = Line(rectangle=[dp(158), dp(54), dp(16), dp(10)],
                                 width=1.2)

        def _sync_illus(*_args):
            cx = head.x + head.width / 2.0
            by = head.y + head.height - dp(74)
            self._ill_bg.pos = (cx - dp(26), by + dp(6))
            self._ill_ring.circle = (cx, by + dp(32), dp(20))
            self._ill_top.rectangle = [cx - dp(8), by, dp(16), dp(10)]
            self._ill_bot.rectangle = [cx - dp(8), by + dp(54), dp(16),
                                       dp(10)]

        head.bind(pos=_sync_illus, size=_sync_illus)
        _sync_illus()
        head.add_widget(Label(text=config.WEARABLE_NAME, font_size=sp(20),
                              bold=True, size_hint_y=None, height=dp(28)))
        self.conn_label = Label(text="• Connecté", font_size=sp(13),
                                bold=True, color=SUCCESS, size_hint_y=None,
                                height=dp(20))
        head.add_widget(self.conn_label)
        content.add_widget(head)

        # informations
        info = CardBox(spacing=dp(6))
        self.rows = {}
        for key, label in (("battery", "Batterie"),
                           ("bluetooth", "Bluetooth"),
                           ("sync", "Dernière synchronisation"),
                           ("firmware", "Firmware")):
            row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
            row.add_widget(Label(text=label, font_size=sp(12),
                                 color=TEXT_DIM, halign="left",
                                 size_hint_x=None, width=dp(170)))
            val = Label(text="--", font_size=sp(12), bold=True,
                        halign="left")
            row.add_widget(val)
            info.add_widget(row)
            self.rows[key] = val
        content.add_widget(info)

        # boutons
        sync_btn = Factory.MediButton(text="Synchroniser")
        sync_btn.bind(on_release=lambda i: self._sync())
        test_btn = Factory.GhostButton(text="Tester les capteurs")
        test_btn.bind(on_release=lambda i: self._test())
        info_btn = Factory.GhostButton(text="Informations du bracelet")
        info_btn.bind(on_release=lambda i: self._info())
        self.disc_btn = Factory.DangerButton(text="Déconnecter")
        self.disc_btn.bind(on_release=lambda i: self._toggle_connection())
        demo_btn = Factory.GhostButton(text="Mode démonstration")
        demo_btn.bind(on_release=lambda i: self.go("demo"))
        content.add_widget(sync_btn)
        content.add_widget(test_btn)
        content.add_widget(info_btn)
        content.add_widget(self.disc_btn)
        content.add_widget(demo_btn)

        self.result = Label(text="", font_size=sp(11), color=CYAN,
                            halign="left", valign="top", size_hint_y=None,
                            height=dp(90))
        self.result.text_size = (dp(330), None)
        content.add_widget(self.result)
        content.add_widget(Spacer(6))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def refresh(self):
        bracelet = self.state.bracelet
        if not bracelet:
            return
        connected = bracelet.connected
        self.conn_label.text = "• Connecté" if connected else "• Déconnecté"
        self.conn_label.color = SUCCESS if connected else DANGER
        self.rows["battery"].text = bracelet.battery_label
        self.rows["bluetooth"].text = ("Connecté" if connected
                                       else "Déconnecté")
        self.rows["sync"].text = fmt_time(bracelet.last_sync)
        self.rows["firmware"].text = bracelet.firmware_version
        self.disc_btn.text = ("Déconnecter" if connected
                              else "Reconnecter")

    def _sync(self):
        bt = self.state.services.bluetooth
        if not bt.is_connected():
            self.result.text = "Bracelet déconnecté : reconnectez-le d'abord."
            return
        bt.read_data()
        self.state.services.data_provider.tick()
        self.result.text = "Synchronisation effectuée."
        self.refresh()

    def _test(self):
        bt = self.state.services.bluetooth
        results = bt.test_sensors()
        lines = ["Autotest des capteurs :"]
        for name, ok in results:
            lines.append(f"  • {name} : {'OK' if ok else 'INDISPONIBLE'}")
        self.result.text = "\n".join(lines)

    def _info(self):
        info = self.state.services.bluetooth.get_device_info()
        text = (f"Identifiant : {info['id']}\nNom : {info['name']}\n"
                f"Firmware : {info['firmware']}\n"
                f"Prototype : aucun matériel réel n'est connecté.")
        popup = Popup(title="Informations du bracelet",
                      content=Label(text=text, font_size=sp(12),
                                    halign="left", valign="top",
                                    text_size=(dp(260), None)),
                      size_hint=(0.85, 0.45))
        popup.open()

    def _toggle_connection(self):
        bt = self.state.services.bluetooth
        if bt.is_connected():
            bt.disconnect()
        else:
            bt.connect()
        self.refresh()
