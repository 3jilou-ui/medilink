"""Application MediLink : assemblage services + état + écrans."""
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager

import config
from app.navigation import Navigator
from app.state import AppState
from models.patient import DEMO_PATIENT
from screens.ai_assistant import AIAssistantScreen
from screens.alert_detail import AlertDetailScreen
from screens.alerts import AlertsScreen
from screens.bracelet import BraceletScreen
from screens.demo import DemoScreen
from screens.emergency import EmergencyScreen
from screens.health_detail import HealthDetailScreen
from screens.history import HistoryScreen
from screens.home import HomeScreen
from screens.login import LoginScreen
from screens.map import MapScreen
from screens.profile import ProfileScreen
from services import build_services
from utils.thresholds import ThresholdEngine
from widgets.base import align_labels
from widgets.bottom_nav import BottomNav

KV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), "kv", "styles.kv")


class MediLinkApp(App):
    def build(self):
        Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        Window.minimum_width, Window.minimum_height = 320, 480
        self.title = config.APP_NAME
        Builder.load_file(KV_PATH)

        self.services = build_services(config)
        self.state = AppState(self.services, DEMO_PATIENT)
        self.state.bracelet = self.services.bluetooth.bracelet

        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(HealthDetailScreen(name="health_detail"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(MapScreen(name="map"))
        self.sm.add_widget(AlertsScreen(name="alerts"))
        self.sm.add_widget(AlertDetailScreen(name="alert_detail"))
        self.sm.add_widget(EmergencyScreen(name="emergency"))
        self.sm.add_widget(AIAssistantScreen(name="assistant"))
        self.sm.add_widget(BraceletScreen(name="bracelet"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(DemoScreen(name="demo"))

        self.navigator = Navigator(self.sm, BottomNav())
        self.state.navigator = self.navigator

        root = BoxLayout(orientation="vertical")
        root.add_widget(self.sm)
        root.add_widget(self.navigator.nav)

        # démarrage des services simulés
        self.services.data_provider.start()
        self.services.location.start_tracking()
        self.state.health_data = self.services.data_provider.get_current()
        from utils.thresholds import ThresholdEngine
        self.state.statuses = \
            ThresholdEngine().evaluate_health_data(self.state.health_data)

        # rafraîchissement des écrans visibles à chaque changement d'état
        self.state.bind(ui_version=self._refresh_current)
        self.navigator.go("login")
        return root

    def _refresh_current(self, *args):
        screen = self.sm.current_screen
        if screen is not None and getattr(screen, "_built", False):
            screen.refresh()
            align_labels(screen)

    def on_stop(self):
        self.state.stop()
