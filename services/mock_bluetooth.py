"""Bluetooth simulé : découverte, connexion, transmission, batterie.

Aucun matériel requis : l'application ne plante jamais si le Bluetooth
est indisponible, car le UI ne parle qu'à cette abstraction.
"""
import threading
import time

from models.bracelet import Bracelet
from services.bluetooth_manager import BluetoothManager


class MockBluetoothManager(BluetoothManager):
    def __init__(self, time_scale=1.0):
        super().__init__()
        self.time_scale = time_scale
        self.bracelet = Bracelet()
        self._connecting = False

    # -- connexion -----------------------------------------------------
    def connect(self):
        if self.is_connected() or self._connecting:
            return
        self._connecting = True
        self._notify("discovering", "Recherche du bracelet MediLink...")

        def _done():
            self._connecting = False
            self.bracelet.connected = True
            self.bracelet.last_sync = time.time()
            self._notify("connected", self.bracelet)

        threading.Timer(0.8 * self.time_scale, _done).start()

    def disconnect(self):
        self.bracelet.connected = False
        self._notify("disconnected", self.bracelet)

    def is_connected(self):
        return bool(self.bracelet.connected)

    # -- données -------------------------------------------------------
    def read_data(self):
        if not self.is_connected():
            return None
        self.bracelet.last_sync = time.time()
        self._notify("sync", self.bracelet)
        return {"ok": True, "ts": self.bracelet.last_sync}

    def get_battery(self):
        return int(self.bracelet.battery)

    def get_device_info(self):
        return {
            "id": self.bracelet.id,
            "name": self.bracelet.name,
            "firmware": self.bracelet.firmware_version,
            "battery": self.get_battery(),
            "connected": self.is_connected(),
        }

    # -- démo ----------------------------------------------------------
    def test_sensors(self):
        """Retourne la liste (capteur, ok) du autotest simulé."""
        ok = self.is_connected()
        return [
            ("Fréquence cardiaque", ok),
            ("SpO2", ok),
            ("Glycémie (module CGM)", ok),
            ("Température", ok),
            ("Accéléromètre", ok),
        ]

    def drain_battery(self, amount=1):
        self.bracelet.battery = max(0, self.bracelet.battery - amount)
