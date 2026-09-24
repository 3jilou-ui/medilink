"""Modèle MedicalAlert."""
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from utils.formatting import fmt_time


class Severity(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


@dataclass
class MedicalAlert:
    parameter: str                 # clé de métrique (ex: "spo2")
    value: str                     # valeur formatée pour affichage
    severity: Severity
    patient_id: str = ""
    patient_name: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())
    timestamp: float = field(default_factory=time.time)
    location: Optional[tuple] = None          # (lat, lon)
    status: AlertStatus = AlertStatus.ACTIVE
    facility: Optional[str] = None            # nom de la structure proche
    reason: str = ""                          # motif d'annulation / résolution
    closed_at: Optional[float] = None

    @property
    def time_label(self):
        return fmt_time(self.timestamp)

    def cancel(self, reason):
        self.status = AlertStatus.CANCELLED
        self.reason = reason
        self.closed_at = time.time()

    def resolve(self, reason="Retour à des valeurs normales"):
        self.status = AlertStatus.RESOLVED
        self.reason = reason
        self.closed_at = time.time()
