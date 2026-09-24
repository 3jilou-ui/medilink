"""Base commune des écrans MediLink."""
from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from utils.constants import TEXT_DIM
from widgets.base import align_labels
from widgets.icons import Icon


class IconButton(ButtonBehavior, FloatLayout):
    """Bouton carré transparent contenant une icône canvas."""

    def __init__(self, icon_name, color=None, icon_size=22, box=40,
                 on_press_cb=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(box), dp(box)),
                         **kwargs)
        self.icon = Icon(name=icon_name, color=color or TEXT_DIM,
                         size=(dp(icon_size), dp(icon_size)))
        self.icon.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.add_widget(self.icon)
        if on_press_cb:
            self.bind(on_release=lambda inst: on_press_cb())


class MediScreen(Screen):
    back_to = "home"
    title = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False

    # -- accès globaux ---------------------------------------------------
    @property
    def app(self):
        return App.get_running_app()

    @property
    def state(self):
        return self.app.state

    @property
    def nav(self):
        return self.app.navigator

    def go(self, name, **params):
        self.nav.go(name, **params)

    def back(self):
        self.nav.go(self.back_to)

    # -- cycle de vie -----------------------------------------------------
    def on_pre_enter(self, *args):
        if not self._built:
            self.build_ui()
            self._built = True
        self.refresh()
        align_labels(self)

    def build_ui(self):
        raise NotImplementedError

    def refresh(self):
        pass

    def set_params(self, **params):
        pass

    # -- helpers ----------------------------------------------------------
    def make_header(self, title=None, back=True, right_widget=None):
        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8),
                           padding=(dp(10), dp(6)))
        if back:
            btn = IconButton("back", on_press_cb=self.back)
            header.add_widget(btn)
        else:
            header.add_widget(Widget(size_hint_x=None, width=dp(8)))
        title_label = Label(text=title or self.title, font_size=sp(17),
                            bold=True, halign="left", valign="middle")
        self.header_label = title_label
        header.add_widget(title_label)
        if right_widget:
            header.add_widget(right_widget)
        else:
            header.add_widget(Widget(size_hint_x=None, width=dp(8)))
        return header
