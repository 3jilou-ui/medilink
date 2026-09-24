"""Fabrique des services selon la configuration (mock aujourd'hui,
réel demain — sans toucher aux écrans)."""
from types import SimpleNamespace

import config
from services.alert_manager import AlertManager
from services.emergency_manager import EmergencyManager
from services.facility_service import FacilityService
from utils.thresholds import ThresholdEngine


def build_services(cfg=None):
    cfg = cfg or config
    scale = cfg.TIME_SCALE

    if cfg.DATA_PROVIDER == "mock":
        from services.mock_data_provider import MockDataProvider
        data_provider = MockDataProvider(interval=cfg.DATA_TICK_SECONDS)
    else:
        raise ValueError(f"DATA_PROVIDER inconnu : {cfg.DATA_PROVIDER}")

    if cfg.BLUETOOTH_PROVIDER == "mock":
        from services.mock_bluetooth import MockBluetoothManager
        bluetooth = MockBluetoothManager(time_scale=scale)
    else:
        raise ValueError(f"BLUETOOTH_PROVIDER inconnu : {cfg.BLUETOOTH_PROVIDER}")

    if cfg.LOCATION_PROVIDER == "mock":
        from services.mock_location import MockLocationProvider
        location = MockLocationProvider(time_scale=scale)
    else:
        raise ValueError(f"LOCATION_PROVIDER inconnu : {cfg.LOCATION_PROVIDER}")

    if cfg.EMERGENCY_PROVIDER == "mock":
        from services.mock_emergency_service import MockEmergencyService
        emergency_service = MockEmergencyService(time_scale=scale)
    else:
        raise ValueError(f"EMERGENCY_PROVIDER inconnu : {cfg.EMERGENCY_PROVIDER}")

    if cfg.AI_PROVIDER == "api":
        from services.gemini_api_assistant import GeminiApiAssistant
        assistant = GeminiApiAssistant(cfg.BACKEND_URL)
    else:
        from services.mock_gemini import MockGeminiAssistant
        assistant = MockGeminiAssistant()

    facilities = FacilityService()
    engine = ThresholdEngine()
    alerts = AlertManager(engine=engine)
    emergency = EmergencyManager(
        location_provider=location,
        facility_service=facilities,
        emergency_service=emergency_service,
        time_scale=scale,
    )

    return SimpleNamespace(
        data_provider=data_provider,
        bluetooth=bluetooth,
        location=location,
        facilities=facilities,
        emergency_service=emergency_service,
        assistant=assistant,
        alert_manager=alerts,
        emergency_manager=emergency,
        threshold_engine=engine,
    )
