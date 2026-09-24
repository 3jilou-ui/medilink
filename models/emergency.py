"""Machine à états du système d'urgence : états + journal (timeline)."""
import time
from dataclasses import dataclass, field
from enum import Enum

from utils.formatting import fmt_time


class EmergencyState(Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ALERT_CREATED = "ALERT_CREATED"
    LOCATING_PATIENT = "LOCATING_PATIENT"
    FACILITY_FOUND = "FACILITY_FOUND"
    AMBULANCE_REQUESTED = "AMBULANCE_REQUESTED"
    AI_ASSISTANCE_ACTIVE = "AI_ASSISTANCE_ACTIVE"
    CANCELLED = "CANCELLED"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


STATE_LABELS = {
    EmergencyState.NORMAL: "Surveillance normale",
    EmergencyState.WARNING: "Valeurs à surveiller",
    EmergencyState.CRITICAL: "Valeur critique détectée",
    EmergencyState.ALERT_CREATED: "Alerte créée",
    EmergencyState.LOCATING_PATIENT: "Localisation du patient",
    EmergencyState.FACILITY_FOUND: "Structure de santé identifiée",
    EmergencyState.AMBULANCE_REQUESTED: "Ambulance demandée",
    EmergencyState.AI_ASSISTANCE_ACTIVE: "Assistant IA activé",
    EmergencyState.CANCELLED: "Alerte annulée",
    EmergencyState.RESOLVED: "Alerte résolue",
    EmergencyState.FAILED: "Échec du protocole",
}

ACTIVE_STATES = {
    EmergencyState.ALERT_CREATED,
    EmergencyState.LOCATING_PATIENT,
    EmergencyState.FACILITY_FOUND,
    EmergencyState.AMBULANCE_REQUESTED,
    EmergencyState.AI_ASSISTANCE_ACTIVE,
}


@dataclass
class TimelineEntry:
    label: str
    state: EmergencyState
    timestamp: float = field(default_factory=time.time)

    @property
    def time_label(self):
        return fmt_time(self.timestamp)
