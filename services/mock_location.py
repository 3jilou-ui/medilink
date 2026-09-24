"""Localisation simulée : coordonnées fixes autour de Sfax + léger jitter."""
import random
import threading

from services.location_provider import LocationProvider


class MockLocationProvider(LocationProvider):
    def __init__(self, lat=34.7406, lon=10.7603,
                 address="Rue de la Liberté, Sfax, Tunisie", time_scale=1.0):
        super().__init__()
        self.base_lat = lat
        self.base_lon = lon
        self.address = address
        self.time_scale = time_scale
        self._tracking = False
        self._thread = None
        self._rng = random.Random(42)

    def get_current_location(self):
        return (self.base_lat, self.base_lon, self.address)

    def start_tracking(self):
        if self._tracking:
            return
        self._tracking = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop_tracking(self):
        self._tracking = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _loop(self):
        while self._tracking:
            threading.Event().wait(5 * max(self.time_scale, 0.1))
            if not self._tracking:
                break
            lat = self.base_lat + self._rng.uniform(-0.0008, 0.0008)
            lon = self.base_lon + self._rng.uniform(-0.0008, 0.0008)
            self._notify((lat, lon, self.address))
