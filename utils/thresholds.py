"""Moteur de seuils — unique source des valeurs de référence.

SEUILS DE DÉMONSTRATION : valeurs simplifiées pour le prototype,
elles ne correspondent pas à des références cliniques officielles.
"""

NORMAL = "NORMAL"
WARNING = "WARNING"
CRITICAL = "CRITICAL"

# Chaque entrée : liste de (statut, borne_basse, borne_haute) évaluées dans
# l'ordre ; None = pas de borne. Le premier intervalle contenant la valeur
# gagne ; sinon NORMAL.
DEMO_THRESHOLDS = {
    "heart_rate": [
        (CRITICAL, None, 45), (CRITICAL, 131, None),
        (WARNING, 46, 59), (WARNING, 101, 130),
    ],
    "spo2": [
        (CRITICAL, None, 89),
        (WARNING, 90, 94),
    ],
    "glucose": [
        (CRITICAL, None, 0.55), (CRITICAL, 1.81, None),
        (WARNING, 0.56, 0.69), (WARNING, 1.41, 1.80),
    ],
    "temperature": [
        (CRITICAL, None, 35.0), (CRITICAL, 39.5, None),
        (WARNING, 35.1, 35.9), (WARNING, 37.6, 39.4),
    ],
    "sleep": [
        (CRITICAL, None, 49),
        (WARNING, 50, 69),
    ],
    "sweat": [
        (CRITICAL, 38.6, None), (CRITICAL, None, 29.9),
        (WARNING, 37.6, 38.5), (WARNING, 30.0, 32.9),
    ],
}

# Tension artérielle : couple (systolique, diastolique) en mmHg.
BP_RULES = [
    (CRITICAL, lambda s, d: s >= 180 or s < 80 or d >= 110 or d < 50),
    (WARNING, lambda s, d: s >= 141 or d >= 91 or s < 90 or d < 60),
]

# Plages "normales" affichées à l'utilisateur (texte informatif).
NORMAL_RANGES = {
    "heart_rate": "60 - 100",
    "spo2": "95 - 100",
    "glucose": "0.70 - 1.40",
    "blood_pressure": "90/60 - 140/90",
    "temperature": "36.0 - 37.5",
    "sleep": "70 - 100",
    "sweat": "33.0 - 37.5",
}


class ThresholdEngine:
    """Évalue une mesure et retourne NORMAL / WARNING / CRITICAL."""

    def __init__(self, thresholds=None):
        self.thresholds = thresholds or DEMO_THRESHOLDS

    def evaluate(self, metric, value):
        if value is None:
            return NORMAL
        if metric == "blood_pressure":
            try:
                sys_v, dia_v = value
            except (TypeError, ValueError):
                return NORMAL
            for status, rule in BP_RULES:
                if rule(sys_v, dia_v):
                    return status
            return NORMAL
        for status, lo, hi in self.thresholds.get(metric, []):
            if (lo is None or value >= lo) and (hi is None or value <= hi):
                return status
        return NORMAL

    def evaluate_health_data(self, health_data):
        result = {}
        for metric in ("heart_rate", "spo2", "glucose", "blood_pressure",
                       "temperature", "sleep", "sweat"):
            value = health_data.value_for(metric)
            result[metric] = self.evaluate(metric, value)
        return result

    @staticmethod
    def worst(statuses):
        if CRITICAL in statuses:
            return CRITICAL
        if WARNING in statuses:
            return WARNING
        return NORMAL

    @staticmethod
    def normal_range(metric):
        return NORMAL_RANGES.get(metric, "")
