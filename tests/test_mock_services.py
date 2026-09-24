"""Tests des services simulés : Bluetooth, Gemini, localisation, données."""
import time

from models.health_data import HealthData
from services.mock_bluetooth import MockBluetoothManager
from services.mock_data_provider import MockDataProvider
from services.mock_gemini import MockGeminiAssistant
from services.mock_location import MockLocationProvider


# -- Bluetooth ---------------------------------------------------------
def test_bluetooth_not_connected_before_connect():
    bt = MockBluetoothManager(time_scale=0)
    bt.disconnect()
    assert bt.is_connected() is False
    assert bt.read_data() is None


def test_bluetooth_connect_is_async_but_completes():
    bt = MockBluetoothManager(time_scale=0)
    bt.disconnect()
    bt.connect()
    # time_scale=0 -> le Timer(0) se déclenche quasi immédiatement
    deadline = time.time() + 2
    while not bt.is_connected() and time.time() < deadline:
        time.sleep(0.02)
    assert bt.is_connected() is True
    assert bt.read_data() is not None


def test_bluetooth_device_info_and_battery():
    bt = MockBluetoothManager()
    info = bt.get_device_info()
    assert info["name"] == "MediLink"
    assert 0 <= info["battery"] <= 100
    assert bt.get_battery() == info["battery"]


def test_bluetooth_test_sensors_returns_pairs():
    bt = MockBluetoothManager()
    sensors = bt.test_sensors()
    assert sensors
    for name, ok in sensors:
        assert isinstance(name, str)
        assert isinstance(ok, bool)


def test_bluetooth_never_crashes_when_unavailable():
    # déconnexion puis lecture : aucune exception, renvoie None
    bt = MockBluetoothManager()
    bt.disconnect()
    assert bt.read_data() is None
    assert bt.get_battery() >= 0


# -- Localisation ------------------------------------------------------
def test_location_returns_triple():
    loc = MockLocationProvider()
    lat, lon, address = loc.get_current_location()
    assert isinstance(lat, float)
    assert isinstance(lon, float)
    assert isinstance(address, str) and address


def test_location_tracking_start_stop():
    loc = MockLocationProvider(time_scale=0)
    loc.start_tracking()
    loc.stop_tracking()          # ne doit pas bloquer ni lever


# -- Gemini (mock) -----------------------------------------------------
def test_gemini_available():
    assert MockGeminiAssistant().available() is True


def test_gemini_initial_guidance_by_parameter():
    g = MockGeminiAssistant()
    for param in ("spo2", "heart_rate", "temperature", "glucose", None):
        lines = g.get_initial_guidance({"abnormal_parameter": param})
        assert isinstance(lines, list) and lines
        assert all(isinstance(l, str) and l for l in lines)


def test_gemini_chat_returns_string():
    g = MockGeminiAssistant()
    for msg in ("Le patient est conscient", "Il respire mal", "ambulance ?",
                "message quelconque"):
        reply = g.chat(msg, {"ambulance_status": "En route"})
        assert isinstance(reply, str) and reply


def test_gemini_chat_bracelet_hint():
    g = MockGeminiAssistant()
    assert "bracelet" in g.chat("Le capteur est mal positionné", {}).lower()


# -- Fournisseur de données -------------------------------------------
def test_data_provider_current_is_health_data():
    p = MockDataProvider(interval=0.01)
    assert isinstance(p.get_current(), HealthData)


def test_data_provider_emergency_scenario_is_critical():
    p = MockDataProvider(interval=0.01)
    p.set_scenario("emergency")
    hd = p.get_current()
    assert hd.heart_rate >= 130
    assert hd.spo2 <= 90


def test_data_provider_remeasure_exits_false_reading():
    p = MockDataProvider(interval=0.01)
    p.set_scenario("false_reading")
    hd = p.remeasure()
    assert isinstance(hd, HealthData)
    assert hd.is_plausible()


def test_data_provider_history_shape():
    p = MockDataProvider(interval=0.01)
    hist = p.get_history("24h")
    assert "labels" in hist and "points" in hist
    assert "heart_rate" in hist["points"]
    assert len(hist["labels"]) == len(hist["points"]["heart_rate"])


def test_data_provider_tick_notifies_listeners():
    p = MockDataProvider(interval=0.01)
    seen = []
    p.add_listener(lambda hd: seen.append(hd))
    p.tick()
    assert len(seen) == 1
