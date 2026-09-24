"""Bannière d'urgence pulsante, impossible à manquer."""
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from utils.constants import DANGER, TEXT
from widgets.icons import Icon


class EmergencyBanner(BoxLayout):
    title = StringProperty("ALERTE MÉDICALE")
    subtitle = StringProperty("Intervention en cours")
    pulse = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(10),
                         size_hint_y=None, height=dp(74),
                         padding=(dp(14), dp(10)), **kwargs)
        with self.canvas.before:
            self._glow = Color(DANGER[0], DANGER[1], DANGER[2], 0.22)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(16)])
            self._border = Color(*DANGER)
            self._line = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[dp(16)])
        self.bind(pos=self._sync, size=self._sync, pulse=self._pulse)
        self._warn = Icon(name="warning", color=DANGER,
                          size=(dp(34), dp(34)), size_hint=(None, None))
        self._warn.pos_hint = {"center_y": 0.5}
        texts = BoxLayout(orientation="vertical", spacing=dp(2))
        self._title = Label(text=self.title, font_size=sp(18), bold=True,
                            color=TEXT, halign="left", size_hint_y=None,
                            height=dp(26), valign="middle")
        self._sub = Label(text=self.subtitle, font_size=sp(12), color=TEXT,
                          halign="left", size_hint_y=None, height=dp(18))
        texts.add_widget(self._title)
        texts.add_widget(self._sub)
        self.add_widget(self._warn)
        self.add_widget(texts)
        self.bind(title=self._set_text, subtitle=self._set_text)
        self._anim = Animation(pulse=1.0, duration=0.7) + Animation(pulse=0.0,
                                                                    duration=0.7)
        self._anim.repeat = True

    def start_pulsing(self):
        self._anim.start(self)

    def stop_pulsing(self):
        self._anim.stop(self)

    def _set_text(self, *args):
        self._title.text = self.title
        self._sub.text = self.subtitle

    def _pulse(self, *args):
        alpha = 0.16 + 0.18 * self.pulse
        self._glow.a = alpha
        self._sync()

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.pos = self.pos
        self._line.size = self.size

    def on_disabled(self, *args):
        pass
