"""Modèle HealthData : une mesure complète reçue du bracelet MediLink."""
import time
from dataclasses import dataclass, field

from utils.validators import validate_field


@dataclass
class HealthData:
    timestamp: float = field(default_factory=time.time)
    heart_rate: float = 78.0
    spo2: float = 98.0
    glucose: float = 1.05
    blood_pressure_systolic: float = 120.0
    blood_pressure_diastolic: float = 80.0
    body_temperature: float = 36.8
    sleep_quality: float = 87.0
    sweat_temperature: float = 35.9

    def value_for(self, metric):
        if metric == "heart_rate":
            return self.heart_rate
        if metric == "spo2":
            return self.spo2
        if metric == "glucose":
            return self.glucose
        if metric == "blood_pressure":
            return (self.blood_pressure_systolic, self.blood_pressure_diastolic)
        if metric == "temperature":
            return self.body_temperature
        if metric == "sleep":
            return self.sleep_quality
        if metric == "sweat":
            return self.sweat_temperature
        return None

    def validate(self):
        """Retourne la liste des incohérences (liste vide = données OK)."""
        errors = []
        for fld in ("heart_rate", "spo2", "glucose", "body_temperature",
                    "sleep_quality", "sweat_temperature",
                    "blood_pressure_systolic", "blood_pressure_diastolic"):
            err = validate_field(fld, getattr(self, fld))
            if err:
                errors.append(err)
        return errors

    def is_plausible(self):
        return not self.validate()

    def as_dict(self):
        return {
            "timestamp": self.timestamp,
            "heart_rate": self.heart_rate,
            "spo2": self.spo2,
            "glucose": self.glucose,
            "blood_pressure_systolic": self.blood_pressure_systolic,
            "blood_pressure_diastolic": self.blood_pressure_diastolic,
            "body_temperature": self.body_temperature,
            "sleep_quality": self.sleep_quality,
            "sweat_temperature": self.sweat_temperature,
        }
