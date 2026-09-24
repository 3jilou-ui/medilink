"""Tests de la machine à états EmergencyManager.

Un scheduler synchrone (delay ignoré, exécution immédiate) rend le protocole
déterministe : start -> localisation -> structure -> ambulance -> assistant IA.
"""
import pytest

from models.alert import Severity
from models.emergency import EmergencyState as S
from models.health_data import HealthData
from models.patient import DEMO_PATIENT
from services.alert_manager import AlertManager
from services.emergency_manager import ALLOWED_TRANSITIONS, EmergencyManager
from services.facility_service import FacilityService
from services.mock_emergency_service import MockEmergencyService
from services.mock_location import MockLocationProvider
from utils.thresholds import ThresholdEngine


def _sync_scheduler(fn, delay):
    fn()


def _alert():
    m = AlertManager(engine=ThresholdEngine())
    return m.process(HealthData(spo2=87, heart_rate=145), DEMO_PATIENT)[0]


def _manager():
    return EmergencyManager(
        location_provider=MockLocationProvider(),
        facility_service=FacilityService(),
        emergency_service=MockEmergencyService(time_scale=0),
        time_scale=0,
        scheduler=_sync_scheduler,
    )


def test_initial_state_is_normal():
    mgr = _manager()
    assert mgr.state == S.NORMAL
    assert not mgr.is_active
    assert mgr.timeline == []


def test_full_protocol_reaches_ai_assistance():
    mgr = _manager()
    assert mgr.start(_alert()) is True
    # le scheduler synchrone déroule tout le protocole
    assert mgr.state == S.AI_ASSISTANCE_ACTIVE
    assert mgr.is_active
    assert mgr.facility is not None
    assert mgr.location is not None
    assert mgr.distance_km is not None
    labels = [e.label for e in mgr.timeline]
    assert any("localis" in l.lower() or "Localisation" in l for l in labels)
    assert any("Ambulance demandée" in l for l in labels)


def test_start_twice_is_ignored():
    mgr = _manager()
    mgr.start(_alert())
    assert mgr.start(_alert()) is False   # déjà actif


def test_cancel_from_active():
    mgr = _manager()
    mgr.start(_alert())
    assert mgr.cancel("Lecture incorrecte") is True
    assert mgr.state == S.CANCELLED
    assert mgr.cancel_reason == "Lecture incorrecte"
    assert mgr.ambulance_status == "Demande annulée"
    assert not mgr.is_active


def test_cancel_when_not_active_returns_false():
    mgr = _manager()
    assert mgr.cancel("x") is False


def test_resolve_from_active():
    mgr = _manager()
    mgr.start(_alert())
    assert mgr.resolve("Retour à la normale") is True
    assert mgr.state == S.RESOLVED
    assert not mgr.is_active


def test_reset_returns_to_normal():
    mgr = _manager()
    mgr.start(_alert())
    mgr.cancel("x")
    mgr.reset()
    assert mgr.state == S.NORMAL
    assert mgr.alert is None
    assert mgr.timeline == []


def test_restart_after_cancel():
    mgr = _manager()
    mgr.start(_alert())
    mgr.cancel("x")
    # après annulation, un nouveau protocole peut démarrer
    assert mgr.start(_alert()) is True
    assert mgr.state == S.AI_ASSISTANCE_ACTIVE


def test_illegal_transition_raises():
    mgr = _manager()
    # NORMAL -> AI_ASSISTANCE_ACTIVE n'est pas autorisé
    with pytest.raises(ValueError):
        mgr._set_state(S.AI_ASSISTANCE_ACTIVE)


def test_allowed_transitions_table_is_complete():
    # chaque état possède une entrée dans la table déclarative
    for state in S:
        assert state in ALLOWED_TRANSITIONS


def test_location_failure_moves_to_failed():
    class Boom:
        def get_current_location(self):
            raise RuntimeError("GPS indisponible")

    mgr = EmergencyManager(
        location_provider=Boom(),
        facility_service=FacilityService(),
        emergency_service=MockEmergencyService(time_scale=0),
        time_scale=0,
        scheduler=_sync_scheduler,
    )
    mgr.start(_alert())
    assert mgr.state == S.FAILED


def test_severity_of_alert_is_critical():
    a = _alert()
    assert a.severity == Severity.CRITICAL
