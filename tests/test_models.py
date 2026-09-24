"""Tests des modèles HealthData et Patient."""
from models.health_data import HealthData
from models.patient import DEMO_PATIENT, Patient


def test_health_data_defaults_are_plausible():
    hd = HealthData()
    assert hd.is_plausible()
    assert hd.validate() == []


def test_health_data_value_for_known_metrics():
    hd = HealthData(heart_rate=90, spo2=95, glucose=1.1,
                    blood_pressure_systolic=130, blood_pressure_diastolic=85,
                    body_temperature=37.0)
    assert hd.value_for("heart_rate") == 90
    assert hd.value_for("spo2") == 95
    assert hd.value_for("glucose") == 1.1
    assert hd.value_for("temperature") == 37.0
    assert hd.value_for("blood_pressure") == (130, 85)
    assert hd.value_for("inconnu") is None


def test_health_data_as_dict_contains_all_fields():
    d = HealthData().as_dict()
    for key in ("heart_rate", "spo2", "glucose", "body_temperature",
                "blood_pressure_systolic", "blood_pressure_diastolic",
                "sleep_quality", "sweat_temperature", "timestamp"):
        assert key in d


def test_health_data_validate_flags_impossible_values():
    hd = HealthData(heart_rate=-5, spo2=150)
    errors = hd.validate()
    assert errors  # au moins une incohérence détectée
    assert not hd.is_plausible()


def test_patient_first_name():
    p = Patient(id="X", name="Mohamed Ben Ali", age=46, blood_group="O+")
    assert p.first_name == "Mohamed"


def test_demo_patient_is_coherent():
    assert DEMO_PATIENT.first_name == "Mohamed"
    assert DEMO_PATIENT.location["lat"] > 0
    assert isinstance(DEMO_PATIENT.age, int)
