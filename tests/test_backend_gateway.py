"""Tests de la passerelle Gemini (sans appel réseau).

On vérifie le prompt système, la construction du prompt utilisateur, le
formatage en lignes et l'absence de clé -> generate() retourne None.
"""
import os
import sys

BACKEND = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from gemini_gateway import (SYSTEM_INSTRUCTION, GeminiGateway,  # noqa: E402
                            build_user_prompt, load_api_key)


def test_system_instruction_is_french_and_safe():
    assert "Respond in French" in SYSTEM_INSTRUCTION
    assert "do not diagnose" in SYSTEM_INSTRUCTION.lower()
    assert "never invent measurements" in SYSTEM_INSTRUCTION.lower()


def test_build_user_prompt_includes_context():
    ctx = {"patient_age": 46, "abnormal_parameter": "spo2",
           "abnormal_value": "87 %", "severity": "CRITICAL",
           "nearest_clinic": "Clinique El Habib",
           "ambulance_status": "En route"}
    prompt = build_user_prompt(ctx, None)
    assert "46" in prompt
    assert "spo2" in prompt
    assert "Clinique El Habib" in prompt
    assert "consignes" in prompt.lower()


def test_build_user_prompt_with_message():
    prompt = build_user_prompt({}, "Il respire mal ?")
    assert "Il respire mal ?" in prompt


def test_to_lines_strips_and_filters():
    text = "- Reste calme\n•  Assieds le patient\n\n   \nAppelle les secours"
    lines = GeminiGateway.to_lines(text)
    assert lines == ["Reste calme", "Assieds le patient", "Appelle les secours"]
    assert GeminiGateway.to_lines("") == []
    assert GeminiGateway.to_lines(None) == []


def test_unconfigured_gateway_returns_none():
    gw = GeminiGateway(api_key="")
    assert gw.configured() is False
    # sans clé, aucun appel réseau n'est tenté
    assert gw.generate({"abnormal_parameter": "spo2"}) is None


def test_load_api_key_reads_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "  test-key  ")
    assert load_api_key() == "test-key"
