"""Modèle Bracelet (wearable MediLink, sans écran)."""
import time
from dataclasses import dataclass, field


@dataclass
class Bracelet:
    id: str = "MS-0001"
    name: str = "MediLink"
    battery: int = 78
    connected: bool = True
    last_sync: float = field(default_factory=time.time)
    firmware_version: str = "1.0.0"

    @property
    def battery_label(self):
        return f"{int(self.battery)} %"
