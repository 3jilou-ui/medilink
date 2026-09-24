"""Validation légère des données saisies ou reçues."""
import re

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

# Plages physiquement plausibles (contrôle de cohérence, pas un diagnostic).
PLAUSIBLE = {
    "heart_rate": (20, 250),
    "spo2": (50, 100),
    "glucose": (0.2, 6.0),
    "body_temperature": (30.0, 45.0),
    "sleep_quality": (0, 100),
    "sweat_temperature": (20.0, 45.0),
    "blood_pressure_systolic": (50, 260),
    "blood_pressure_diastolic": (30, 160),
}


def validate_email(email):
    return bool(EMAIL_RE.match((email or "").strip()))


def validate_phone(phone):
    digits = re.sub(r"\D", "", phone or "")
    return 6 <= len(digits) <= 15


def validate_field(field, value):
    """Retourne None si plausible, sinon un message d'erreur en français."""
    if value is None:
        return f"Valeur manquante : {field}"
    if field not in PLAUSIBLE:
        return None
    lo, hi = PLAUSIBLE[field]
    try:
        v = float(value)
    except (TypeError, ValueError):
        return f"Valeur invalide : {field}"
    if not (lo <= v <= hi):
        return f"Valeur improbable pour {field} : {value}"
    return None
