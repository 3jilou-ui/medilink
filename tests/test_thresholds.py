"""Tests du ThresholdEngine (unique source des seuils)."""
from models.health_data import HealthData
from utils.thresholds import (CRITICAL, NORMAL, WARNING, ThresholdEngine)


def test_normal_values():
    e = ThresholdEngine()
    assert e.evaluate("heart_rate", 78) == NORMAL
    assert e.evaluate("spo2", 98) == NORMAL
    assert e.evaluate("temperature", 36.8) == NORMAL
    assert e.evaluate("glucose", 1.05) == NORMAL


def test_warning_values():
    e = ThresholdEngine()
    assert e.evaluate("heart_rate", 112) == WARNING
    assert e.evaluate("spo2", 92) == WARNING
    assert e.evaluate("temperature", 38.0) == WARNING


def test_critical_values():
    e = ThresholdEngine()
    assert e.evaluate("heart_rate", 145) == CRITICAL
    assert e.evaluate("spo2", 87) == CRITICAL
    assert e.evaluate("temperature", 39.5) == CRITICAL
    assert e.evaluate("heart_rate", 40) == CRITICAL


def test_emergency_scenario_is_critical():
    e = ThresholdEngine()
    hd = HealthData(heart_rate=145, spo2=87, body_temperature=39.5)
    result = e.evaluate_health_data(hd)
    assert result["heart_rate"] == CRITICAL
    assert result["spo2"] == CRITICAL
    assert result["temperature"] == CRITICAL
    assert e.worst(result.values()) == CRITICAL


def test_blood_pressure_rules():
    e = ThresholdEngine()
    assert e.evaluate("blood_pressure", (120, 80)) == NORMAL
    assert e.evaluate("blood_pressure", (150, 95)) == WARNING
    assert e.evaluate("blood_pressure", (190, 120)) == CRITICAL
    # entrée invalide -> NORMAL (jamais d'exception)
    assert e.evaluate("blood_pressure", None) == NORMAL


def test_none_value_is_normal():
    assert ThresholdEngine().evaluate("spo2", None) == NORMAL


def test_worst_precedence():
    assert ThresholdEngine.worst([NORMAL, WARNING]) == WARNING
    assert ThresholdEngine.worst([WARNING, CRITICAL]) == CRITICAL
    assert ThresholdEngine.worst([NORMAL, NORMAL]) == NORMAL


def test_normal_range_text():
    assert "95" in ThresholdEngine.normal_range("spo2")
    assert ThresholdEngine.normal_range("inconnu") == ""
