r"""Auto-test piloté : démarre l'app, déroule le scénario d'urgence complet
puis vérifie chaque étape du flux d'acceptation.

Usage : .venv\Scripts\python.exe dev_smoke.py
"""
import os
import sys

os.environ.setdefault("MEDILINK_TIME_SCALE", "0.25")
os.environ.setdefault("MEDILINK_DATA_TICK_SECONDS", "1.0")

from kivy.clock import Clock  # noqa: E402

from app.application import MediLinkApp  # noqa: E402
from models.emergency import ACTIVE_STATES, EmergencyState  # noqa: E402

RESULTS = []


def check(label, condition):
    RESULTS.append((label, bool(condition)))
    print(f"[{'OK ' if condition else 'FAIL'}] {label}")


class SmokeApp(MediLinkApp):
    def on_start(self):
        Clock.schedule_once(lambda dt: self.step_home(), 1.0)

    def step_home(self):
        self.navigator.go("home")
        check("APP START -> HOME", self.sm.current == "home")
        check("HEALTH DATA DISPLAYED", self.state.health_data is not None)
        Clock.schedule_once(lambda dt: self.step_emergency(), 1.5)

    def step_emergency(self):
        self.state.simulate_emergency()
        Clock.schedule_once(lambda dt: self.step_critical(), 2.0)

    def step_critical(self):
        em = self.services.emergency_manager
        hd = self.state.health_data
        check("CRITICAL VALUES", hd.heart_rate > 130 and hd.spo2 < 90)
        check("MEDICAL ALERT", any(
            a.severity.value == "CRITICAL"
            for a in self.services.alert_manager.alerts))
        check("EMERGENCY SCREEN OPENED", self.sm.current == "emergency")
        Clock.schedule_once(lambda dt: self.step_located(), 2.0)

    def step_located(self):
        em = self.services.emergency_manager
        check("PATIENT LOCATION", em.location is not None)
        check("NEAREST CLINIC", em.facility is not None)
        Clock.schedule_once(lambda dt: self.step_ambulance(), 2.0)

    def step_ambulance(self):
        em = self.services.emergency_manager
        check("AMBULANCE REQUESTED",
              em.state in (EmergencyState.AMBULANCE_REQUESTED,
                           EmergencyState.AI_ASSISTANCE_ACTIVE))
        Clock.schedule_once(lambda dt: self.step_ai(), 2.5)

    def step_ai(self):
        em = self.services.emergency_manager
        check("AMBULANCE EN ROUTE", "route" in em.ambulance_status.lower()
              or em.eta_seconds is not None)
        check("AI ASSISTANT STATE",
              em.state == EmergencyState.AI_ASSISTANCE_ACTIVE)
        self.navigator.go("assistant")
        check("ASSISTANT SCREEN", self.sm.current == "assistant")
        Clock.schedule_once(lambda dt: self.step_cancel(), 2.0)

    def step_cancel(self):
        self.navigator.go("emergency")
        self.state.cancel_emergency()
        Clock.schedule_once(lambda dt: self.step_cancelled(), 1.0)

    def step_cancelled(self):
        em = self.services.emergency_manager
        alert = self.services.alert_manager.alerts[0] \
            if self.services.alert_manager.alerts else None
        check("ALERT = CANCELLED",
              em.state == EmergencyState.CANCELLED
              and alert is not None and alert.status.value == "CANCELLED")
        self.navigator.go("home")
        check("RETURN TO NORMAL MONITORING", self.sm.current == "home")
        Clock.schedule_once(lambda dt: self.finish(), 1.0)

    def finish(self):
        failed = [label for label, ok in RESULTS if not ok]
        print("=" * 60)
        if failed:
            print(f"SMOKE TEST : {len(failed)} ÉCHEC(S) : {failed}")
        else:
            print(f"SMOKE TEST : {len(RESULTS)} VÉRIFICATIONS OK")
        print("=" * 60)
        self.stop()


if __name__ == "__main__":
    SmokeApp().run()
    sys.exit(0 if all(ok for _, ok in RESULTS) else 1)
