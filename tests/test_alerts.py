"""Tests de l'AlertManager : création, résolution, annulation, filtres."""
from models.alert import AlertStatus, Severity
from models.health_data import HealthData
from models.patient import DEMO_PATIENT
from services.alert_manager import AlertManager
from utils.thresholds import ThresholdEngine


def _manager():
    return AlertManager(engine=ThresholdEngine())


def test_critical_measurement_creates_alert():
    m = _manager()
    created = m.process(HealthData(spo2=87), DEMO_PATIENT)
    assert len(created) == 1
    alert = created[0]
    assert alert.severity == Severity.CRITICAL
    assert alert.parameter == "spo2"
    assert alert.status == AlertStatus.ACTIVE
    assert m.active_for("spo2") is alert


def test_no_alert_for_normal_values():
    m = _manager()
    created = m.process(HealthData(), DEMO_PATIENT)
    assert created == []
    assert m.active_alerts() == []


def test_warning_then_normal_resolves():
    m = _manager()
    created = m.process(HealthData(heart_rate=112), DEMO_PATIENT)
    assert created and created[0].severity == Severity.WARNING
    assert m.active_for("heart_rate") is not None
    # retour à la normale -> l'alerte WARNING est résolue
    m.process(HealthData(heart_rate=78), DEMO_PATIENT)
    assert m.active_for("heart_rate") is None
    resolved = m.filtered("resolved")
    assert resolved and resolved[0].status == AlertStatus.RESOLVED


def test_close_alert_cancels():
    m = _manager()
    alert = m.process(HealthData(spo2=87), DEMO_PATIENT)[0]
    m.close_alert(alert, AlertStatus.CANCELLED, "Lecture incorrecte")
    assert alert.status == AlertStatus.CANCELLED
    assert alert.reason == "Lecture incorrecte"
    assert m.active_for("spo2") is None
    assert alert in m.filtered("cancelled")


def test_filters():
    m = _manager()
    m.process(HealthData(spo2=87), DEMO_PATIENT)          # critique
    m.process(HealthData(heart_rate=112), DEMO_PATIENT)    # attention
    assert len(m.filtered("critical")) >= 1
    assert len(m.filtered("warning")) >= 1
    assert len(m.filtered("all")) >= 2


def test_listener_is_notified():
    m = _manager()
    seen = []
    m.add_listener(lambda a: seen.append(a))
    m.process(HealthData(spo2=87), DEMO_PATIENT)
    assert len(seen) == 1
    assert seen[0].severity == Severity.CRITICAL


def test_get_by_id():
    m = _manager()
    alert = m.process(HealthData(spo2=87), DEMO_PATIENT)[0]
    assert m.get(alert.id) is alert
    assert m.get("INCONNU") is None
