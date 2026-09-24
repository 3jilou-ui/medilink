"""Interface du fournisseur de localisation (GPS)."""
from abc import ABC, abstractmethod


class LocationProvider(ABC):
    def __init__(self):
        self._listeners = []

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self, location):
        for cb in list(self._listeners):
            cb(location)

    @abstractmethod
    def get_current_location(self):
        """Retourne (lat, lon, adresse)."""

    @abstractmethod
    def start_tracking(self):
        ...

    @abstractmethod
    def stop_tracking(self):
        ...
