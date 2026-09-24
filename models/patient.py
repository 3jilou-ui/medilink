"""Modèle Patient + données de démonstration."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Patient:
    id: str
    name: str
    age: int
    blood_group: str
    phone: str = ""
    emergency_contact: str = ""
    doctor: str = ""
    location: dict = field(default_factory=dict)  # {lat, lon, address}

    @property
    def first_name(self):
        return self.name.split(" ")[0] if self.name else ""


# Données de démonstration (prototype).
DEMO_PATIENT = Patient(
    id="BR-0251",
    name="Mohamed Ben Ali",
    age=46,
    blood_group="O+",
    phone="+216 22 123 456",
    emergency_contact="Amel Ben Ali (épouse) — +216 22 987 654",
    doctor="Dr Ahmed Ben Salah — Médecin généraliste",
    location={
        "lat": 34.7406,
        "lon": 10.7603,
        "address": "Rue de la Liberté, Sfax, Tunisie",
    },
)
