"""Configuration centrale de MediLink.

Toutes les valeurs peuvent être surchargées par variables d'environnement
(prefixe MEDILINK_) sans modifier le code.
"""
import os


def _env(key, default):
    return os.environ.get("MEDILINK_" + key, default)


def _env_bool(key, default):
    val = os.environ.get("MEDILINK_" + key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


APP_NAME = _env("APP_NAME", "MediLink")
WEARABLE_NAME = _env("WEARABLE_NAME", "MediLink")

# Prototype : toutes les données sont simulées par défaut.
DEMO_MODE = _env_bool("DEMO_MODE", True)

DATA_PROVIDER = _env("DATA_PROVIDER", "mock")          # mock | (futur: real)
BLUETOOTH_PROVIDER = _env("BLUETOOTH_PROVIDER", "mock")  # mock | (futur: ble)
LOCATION_PROVIDER = _env("LOCATION_PROVIDER", "mock")   # mock | (futur: gps)
EMERGENCY_PROVIDER = _env("EMERGENCY_PROVIDER", "mock")  # mock | (futur: real)
AI_PROVIDER = _env("AI_PROVIDER", "mock")               # mock | api

# URL du backend FastAPI (proxy Gemini). Jamais de clé API dans l'app mobile.
BACKEND_URL = _env("BACKEND_URL", "http://127.0.0.1:8000")

DEBUG = _env_bool("DEBUG", True)

# Résolution de test desktop (le UI reste responsive).
WINDOW_WIDTH = int(_env("WINDOW_WIDTH", "390"))
WINDOW_HEIGHT = int(_env("WINDOW_HEIGHT", "844"))

# Intervalle (secondes) entre deux mesures simulées.
DATA_TICK_SECONDS = float(_env("DATA_TICK_SECONDS", "3.0"))

# Facteur d'accélération des temporisations (tests = 0).
TIME_SCALE = float(_env("TIME_SCALE", "1.0"))

DISCLAIMER = (
    "Prototype de démonstration — les données affichées sont simulées et ne "
    "constituent pas un diagnostic médical."
)
DISCLAIMER_2 = (
    "Cette application ne remplace pas l'avis d'un professionnel de santé."
)
