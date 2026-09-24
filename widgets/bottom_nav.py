"""Navigation basse persistante : Accueil / Carte / Historique / Alertes / Profil."""
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from utils.constants import PRIMARY, SURFACE, TEXT_DIM
from widgets.icons import Icon

TABS = [
    ("home", "Accueil", "home"),
    ("map", "Carte", "pin"),
    ("history", "Historique", "clock"),
    ("alerts", "Alertes", "bell"),
    ("profile", "Profil", "person"),
]


class _NavItem(BoxLayout):
    def __init__(self, screen, label, icon, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2), **kwargs)
        self.screen = screen
        self.icon = Icon(name=icon, color=TEXT_DIM, size=(dp(22), dp(22)),
                         size_hint=(None, None))
        self.icon.pos_hint = {"center_x": 0.5}
        self.label = Label(text=label, font_size=sp(10), color=TEXT_DIM)
        self.add_widget(Widget(size_hint_y=None, height=dp(6)))
        self.add_widget(self.icon)
        self.add_widget(self.label)

    def set_active(self, active):
        color = PRIMARY if active else TEXT_DIM
        self.icon.color = color
        self.label.color = color
        self.label.bold = active


class BottomNav(BoxLayout):
    active = StringProperty("home")
    callback = ObjectProperty(None, allownone=True)
    badge_count = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=dp(62), spacing=0, **kwargs)
        with self.canvas.before:
            Color(*SURFACE)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(0.11, 0.23, 0.37, 1)
            self._top = Line(points=[0, 0, 1, 1], width=1.0)
        self.bind(pos=self._sync, size=self._sync)
        self.items = {}
        for screen, label, icon in TABS:
            item = _NavItem(screen, label, icon)
            self.items[screen] = item
            self.add_widget(item)
        self.bind(active=self._apply)
        self._apply()

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._top.points = [self.x, self.y + self.height,
                            self.x + self.width, self.y + self.height]

    def _apply(self, *args):
        for screen, item in self.items.items():
            item.set_active(screen == self.active)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        for screen, item in self.items.items():
            if item.collide_point(*touch.pos):
                if self.callback:
                    self.callback(screen)
                return True
        return True
