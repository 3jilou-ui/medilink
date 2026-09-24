"""État global : relie les services (threads) au UI (thread principal)."""
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import DictProperty, ListProperty, ObjectProperty, \
    StringProperty

from models.alert import AlertStatus, Severity
from models.emergency import ACTIVE_STATES, EmergencyState
from utils.thresholds import NORMAL


class AppState(EventDispatcher):
    health_data = ObjectProperty(None, allownone=True)
    statuses = DictProperty({})
    alerts = ListProperty([])
    bracelet = ObjectProperty(None, allownone=True)
    emergency_state = StringProperty("NORMAL")
    ui_version = ObjectProperty(0)   # incrémenté pour forcer le refresh

    def __init__(self, services, patient):
        super().__init__()
        self.services = services
        self.patient = patient
        self.navigator = None
        self._wire()

    # ------------------------------------------------------------------
    def _wire(self):
        s = self.services
        s.data_provider.add_listener(self._on_data_thread)
        s.bluetooth.add_listener(self._on_bt_thread)
        s.alert_manager.add_listener(self._on_alert_thread)
        s.emergency_manager.add_listener(self._on_emergency_thread)

    @property
    def alert_manager(self):
        return self.services.alert_manager

    @property
    def emergency_manager(self):
        return self.services.emergency_manager

    def stop(self):
        s = self.services
        s.data_provider.stop()
        s.location.stop_tracking()

    # -- callbacks depuis les threads services ---------------------------
    def _on_main(self, fn, *args):
        Clock.schedule_once(lambda dt: fn(*args), 0)

    def _on_data_thread(self, health_data):
        self._on_main(self._apply_data, health_data)

    def _on_bt_thread(self, event, payload):
        self._on_main(self._apply_bt, event, payload)

    def _on_alert_thread(self, alert):
        self._on_main(self._apply_alert, alert)

    def _on_emergency_thread(self, manager):
        self._on_main(self._apply_emergency)

    # -- application sur le thread UI -------------------------------------
    def _apply_data(self, health_data):
        self.health_data = health_data
        self.statuses = self.services.threshold_engine.evaluate_health_data(
            health_data)
        location = self.services.location.get_current_location()
        self.services.alert_manager.process(health_data, self.patient,
                                            location)
        # résolution automatique si retour à la normale pendant l'urgence
        em = self.services.emergency_manager
        if em.is_active and all(v == NORMAL for v in self.statuses.values()):
            em.resolve()
            self._close_active(AlertStatus.RESOLVED,
                               "Nouvelle mesure normale")
        self._bump()

    def _apply_bt(self, event, payload):
        self.bracelet = self.services.bluetooth.bracelet
        self._bump()

    def _apply_alert(self, alert):
        self.alerts = list(self.services.alert_manager.alerts)
        if (alert.severity == Severity.CRITICAL
                and alert.status.value == "ACTIVE"):
            em = self.services.emergency_manager
            if not em.is_active:
                em.start(alert)
        self._bump()

    def _apply_emergency(self):
        em = self.services.emergency_manager
        self.emergency_state = em.state.value
        if self.navigator:
            current = self.navigator.sm.current
            if em.state in ACTIVE_STATES and current not in (
                    "emergency", "assistant"):
                self.navigator.go("emergency")
        self._bump()

    def _bump(self):
        self.ui_version = self.ui_version + 1

    # ------------------------------------------------------------------
    # Actions de démonstration
    # ------------------------------------------------------------------
    def simulate_emergency(self):
        self.services.data_provider.set_scenario("emergency")

    def simulate_warning(self):
        self.services.data_provider.set_scenario("warning")

    def simulate_false_reading(self):
        self.services.data_provider.set_scenario("false_reading")

    def cancel_emergency(self):
        em = self.services.emergency_manager
        if em.is_active:
            em.cancel("Valeur incorrecte / mesure suspecte")
            self._close_active(AlertStatus.CANCELLED,
                               "Valeur incorrecte / mesure suspecte")
            self.services.data_provider.set_scenario(None)

    def remeasure(self):
        self.services.data_provider.remeasure()

    def _close_active(self, status, reason):
        for alert in list(self.services.alert_manager.active_alerts()):
            self.services.alert_manager.close_alert(alert, status=status,
                                                    reason=reason)

    def reset_demo(self):
        self.services.emergency_manager.reset()
        self.services.data_provider.set_scenario(None)
        self._close_active(AlertStatus.RESOLVED,
                           "Réinitialisation de la démonstration")
        self._bump()

    # -- vibrations (si supportées, ex: Android) ---------------------------
    def vibrate(self, seconds=0.6):
        try:
            from plyer import vibrator
            vibrator.vibrate(seconds)
        except Exception:
            pass
