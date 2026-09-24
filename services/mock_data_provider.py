"""Fournisseur de données simulé : valeurs réalistes et scénarios de démo."""
import random
import threading
import time
from collections import deque

from models.health_data import HealthData
from services.data_provider import HealthDataProvider

# Valeurs de base du patient démo (mode normal).
BASE = dict(heart_rate=78, spo2=98, glucose=1.05, sys=120, dia=80,
            temperature=36.8, sleep=87, sweat=35.9)

# Scénarios de démonstration (valeurs cibles).
SCENARIOS = {
    "normal": None,
    "warning": dict(heart_rate=112, spo2=91, temperature=38.7),
    "emergency": dict(heart_rate=145, spo2=87, temperature=39.5),
    # Lecture manifestement incorrecte (capteur perturbé).
    "false_reading": dict(heart_rate=242, spo2=54, temperature=44.2),
}

JITTER = dict(heart_rate=2.5, spo2=0.6, glucose=0.02, sys=3.0, dia=2.0,
              temperature=0.12, sleep=0.0, sweat=0.15)


class MockDataProvider(HealthDataProvider):
    """Génère des mesures plausibles qui évoluent doucement."""

    def __init__(self, interval=3.0, seed=None):
        super().__init__()
        self.interval = interval
        self._rng = random.Random(seed)
        self._thread = None
        self._running = False
        self._scenario = None
        self._current = HealthData()
        self._buffer = deque(maxlen=200)   # historique 24 h (tick simulés)
        self._seed_history()

    # ------------------------------------------------------------------
    def _seed_history(self):
        now = time.time()
        for i in range(48, 0, -1):  # 48 points = 24 h à 30 min
            hd = self._make_reading(scenario=None)
            hd.timestamp = now - i * 1800
            self._buffer.append(hd)

    def _make_reading(self, scenario=None):
        targets = SCENARIOS.get(scenario) if scenario else None
        r = self._rng
        hr = BASE["heart_rate"] + r.uniform(-4, 4)
        spo2 = BASE["spo2"] + r.uniform(-1, 1)
        glu = BASE["glucose"] + r.uniform(-0.05, 0.05)
        sys_v = BASE["sys"] + r.uniform(-4, 4)
        dia_v = BASE["dia"] + r.uniform(-3, 3)
        temp = BASE["temperature"] + r.uniform(-0.15, 0.15)
        sleep = BASE["sleep"]
        sweat = BASE["sweat"] + r.uniform(-0.2, 0.2)
        if targets:
            hr = targets.get("heart_rate", hr) + r.uniform(-2, 2)
            spo2 = targets.get("spo2", spo2) + r.uniform(-0.5, 0.5)
            temp = targets.get("temperature", temp) + r.uniform(-0.1, 0.1)
            if scenario == "false_reading":
                sys_v, dia_v = 250.0, 150.0
                glu = 4.9
        return HealthData(
            timestamp=time.time(),
            heart_rate=round(hr, 1),
            spo2=round(min(100, spo2), 1),
            glucose=round(glu, 2),
            blood_pressure_systolic=round(sys_v, 1),
            blood_pressure_diastolic=round(dia_v, 1),
            body_temperature=round(temp, 1),
            sleep_quality=sleep,
            sweat_temperature=round(sweat, 1),
        )

    # ------------------------------------------------------------------
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _loop(self):
        while self._running:
            time.sleep(self.interval)
            if not self._running:
                break
            self.tick()

    def tick(self):
        """Produit et publie une nouvelle mesure (utilisable en test)."""
        self._current = self._make_reading(self._scenario)
        self._buffer.append(self._current)
        self._notify(self._current)
        return self._current

    # ------------------------------------------------------------------
    def get_current(self):
        return self._current

    def get_history(self, period="24h"):
        if period == "24h":
            entries = list(self._buffer)
            step = max(1, len(entries) // 24)
            entries = entries[::step] or entries
            labels = [time.strftime("%H:%M", time.localtime(e.timestamp))
                      for e in entries]
        else:
            days = 7 if period == "7d" else 30
            entries, labels = [], []
            now = time.time()
            for i in range(days, 0, -1):
                hd = self._make_reading(None)
                hd.timestamp = now - i * 86400
                # légère tendance jour/nuit pour un rendu vivant
                hd.heart_rate = round(hd.heart_rate + self._rng.uniform(-6, 6))
                entries.append(hd)
                labels.append(time.strftime("%d/%m", time.localtime(hd.timestamp)))
        points = {
            "heart_rate": [e.heart_rate for e in entries],
            "spo2": [e.spo2 for e in entries],
            "glucose": [e.glucose for e in entries],
            "temperature": [e.body_temperature for e in entries],
            "blood_pressure": [e.blood_pressure_systolic for e in entries],
            "sleep": [e.sleep_quality for e in entries],
            "sweat": [e.sweat_temperature for e in entries],
        }
        return {"labels": labels, "points": points}

    def set_scenario(self, name):
        self._scenario = name if name in SCENARIOS else None
        self.tick()

    def remeasure(self):
        """Nouvelle mesure immédiate ; sort du scénario de fausse lecture."""
        if self._scenario == "false_reading":
            self._scenario = None
        return self.tick()
