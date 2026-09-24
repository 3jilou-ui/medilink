"""Interface de gestion Bluetooth / BLE du bracelet MediLink."""
from abc import ABC, abstractmethod


class BluetoothManager(ABC):
    def __init__(self):
        self._listeners = []

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self, event, payload=None):
        for cb in list(self._listeners):
            cb(event, payload)

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self):
        ...

    @abstractmethod
    def is_connected(self):
        ...

    @abstractmethod
    def read_data(self):
        ...

    @abstractmethod
    def get_battery(self):
        ...

    @abstractmethod
    def get_device_info(self):
        ...
