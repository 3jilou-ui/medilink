"""Navigation centrale : ScreenManager + navigation basse."""
from kivy.properties import StringProperty

MAIN_TABS = ("home", "map", "history", "alerts", "profile")
# Écrans sans barre de navigation basse.
NO_NAV = {"login", "emergency", "assistant", "demo", "alert_detail"}


class Navigator:
    def __init__(self, screen_manager, bottom_nav):
        self.sm = screen_manager
        self.nav = bottom_nav
        self.nav.callback = self.go
        self.current = StringProperty("login")

    def go(self, name, **params):
        screen = self.sm.get_screen(name)
        if params and hasattr(screen, "set_params"):
            screen.set_params(**params)
        self.sm.current = name
        self.current = name
        if name in MAIN_TABS:
            self.nav.active = name
        self.nav.size_hint_y = None if name in NO_NAV else None
        from kivy.metrics import dp
        self.nav.height = dp(6) if name in NO_NAV else dp(62)
        self.nav.opacity = 0 if name in NO_NAV else 1
        self.nav.disabled = name in NO_NAV

    def back(self, default="home"):
        screen = self.sm.get_screen(self.sm.current)
        self.go(getattr(screen, "back_to", default))
