"""Bulle de chat (assistant IA / accompagnant)."""
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from utils.constants import PRIMARY_DARK, SURFACE_LIGHT, TEXT
from widgets.base import CardBox


class ChatBubble(BoxLayout):
    who = StringProperty("ai")   # 'ai' | 'user'
    message = StringProperty("")

    def __init__(self, who="ai", message="", **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         spacing=0, **kwargs)
        self.who = who
        self.message = message
        self.padding = (dp(6), 0)
        self.bubble = CardBox(
            bg_color=PRIMARY_DARK if who == "user" else SURFACE_LIGHT,
            border_color=(0, 0, 0, 0), size_hint_x=None,
            padding=(dp(12), dp(10)))
        self.bubble.radius = dp(14)
        self.label = Label(text=message, font_size=sp(13), color=TEXT,
                           halign="left", valign="top",
                           size_hint=(None, None))
        self.label.bind(texture_size=self._resize)
        self.bubble.add_widget(self.label)
        if who == "user":
            self.add_widget(BoxLayout())
        self.add_widget(self.bubble)
        if who == "ai":
            self.add_widget(BoxLayout())
        self.bind(message=self._set_message, parent=self._fit,
                  width=self._fit)
        self._fit()

    def _set_message(self, *args):
        self.label.text = self.message

    def _max_width(self):
        base = self.parent.width if self.parent else self.width
        return max(dp(120), (base or dp(390)) - dp(48))

    def _fit(self, *args):
        self.label.text_size = (self._max_width() - dp(24), None)
        self._resize()

    def _resize(self, *args):
        tw, th = self.label.texture_size
        self.label.size = (tw, th)
        self.bubble.width = tw + dp(24)
        self.bubble.height = th + dp(20)
        self.height = th + dp(28)
