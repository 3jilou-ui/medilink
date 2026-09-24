"""Interface du fournisseur de données de santé.

Le UI ne connaît que cette abstraction : remplacer MockDataProvider par un
fournisseur réel (bracelet / backend) ne nécessite aucune modification
des écrans.
"""
from abc import ABC, abstractmethod


class HealthDataProvider(ABC):
    def __init__(self):
        self._listeners = []

    def add_listener(self, callback):
        self._listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, health_data):
        for cb in list(self._listeners):
            cb(health_data)

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def get_current(self):
        ...

    @abstractmethod
    def get_history(self, period="24h"):
        """Retourne {'labels': [...], 'points': {metric: [valeurs]}}."""

    @abstractmethod
    def set_scenario(self, name):
        """None | 'normal' | 'warning' | 'emergency' | 'false_reading'."""

    @abstractmethod
    def remeasure(self):
        """Demande une nouvelle mesure immédiate."""
