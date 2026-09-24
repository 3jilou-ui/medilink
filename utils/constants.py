"""Constantes globales : couleurs, métriques, libellés français."""

def rgba(hex_str, alpha=1.0):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16) / 255.0,
            int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0,
            alpha)


def darken(color, factor=0.8):
    return [color[0] * factor, color[1] * factor, color[2] * factor,
            color[3] if len(color) > 3 else 1.0]


def button_rgba(color, state, default=None):
    """Couleur de fond d'un bouton, tolérante à une propriété non initialisée."""
    color = color or default or PRIMARY
    return darken(color, 0.82) if state == "down" else list(color)


def ghost_rgba(border_color, state):
    if state == "down":
        return list(SURFACE_LIGHT)
    return [0, 0, 0, 0]


# ---- Palette (source de vérité : maquettes MediWatch) ----
BACKGROUND = rgba("#071426")      # navy très sombre
SURFACE = rgba("#0C1F38")         # cartes bleu profond
SURFACE_LIGHT = rgba("#12294A")   # cartes secondaires
BORDER = rgba("#1B3A5F")
PRIMARY = rgba("#2E9BF5")         # bleu électrique
PRIMARY_DARK = rgba("#1B6FC2")
CYAN = rgba("#35D6F0")            # accent cyan
TEXT = rgba("#FFFFFF")
TEXT_DIM = rgba("#8FA8C4")
SUCCESS = rgba("#2FD47A")         # vert santé
WARNING = rgba("#FFA726")         # orange alerte
DANGER = rgba("#FF3B5C")          # rouge urgence
DANGER_DARK = rgba("#5A1220")
PURPLE = rgba("#8B7BF5")

STATUS_COLORS = {
    "NORMAL": SUCCESS,
    "WARNING": WARNING,
    "CRITICAL": DANGER,
}

STATUS_LABELS = {
    "NORMAL": "Normale",
    "WARNING": "Attention",
    "CRITICAL": "Critique",
}

# ---- Métriques de santé ----
METRIC_HEART_RATE = "heart_rate"
METRIC_SPO2 = "spo2"
METRIC_GLUCOSE = "glucose"
METRIC_BLOOD_PRESSURE = "blood_pressure"
METRIC_TEMPERATURE = "temperature"
METRIC_SLEEP = "sleep"
METRIC_SWEAT = "sweat"

METRIC_LABELS = {
    METRIC_HEART_RATE: "Fréquence cardiaque",
    METRIC_SPO2: "SpO2",
    METRIC_GLUCOSE: "Glycémie",
    METRIC_BLOOD_PRESSURE: "Tension artérielle",
    METRIC_TEMPERATURE: "Température corporelle",
    METRIC_SLEEP: "Qualité du sommeil",
    METRIC_SWEAT: "Température de transpiration",
}

METRIC_UNITS = {
    METRIC_HEART_RATE: "BPM",
    METRIC_SPO2: "%",
    METRIC_GLUCOSE: "g/L",
    METRIC_BLOOD_PRESSURE: "mmHg",
    METRIC_TEMPERATURE: "°C",
    METRIC_SLEEP: "%",
    METRIC_SWEAT: "°C",
}

METRIC_ICONS = {
    METRIC_HEART_RATE: "heart",
    METRIC_SPO2: "lungs",
    METRIC_GLUCOSE: "drop",
    METRIC_BLOOD_PRESSURE: "gauge",
    METRIC_TEMPERATURE: "thermo",
    METRIC_SLEEP: "moon",
    METRIC_SWEAT: "sweat",
}

METRIC_COLORS = {
    METRIC_HEART_RATE: DANGER,
    METRIC_SPO2: CYAN,
    METRIC_GLUCOSE: rgba("#F472B6"),
    METRIC_BLOOD_PRESSURE: SUCCESS,
    METRIC_TEMPERATURE: WARNING,
    METRIC_SLEEP: PURPLE,
    METRIC_SWEAT: rgba("#38BDF8"),
}

# Ordre d'affichage
METRIC_ORDER = [
    METRIC_HEART_RATE, METRIC_SPO2, METRIC_GLUCOSE,
    METRIC_BLOOD_PRESSURE, METRIC_TEMPERATURE, METRIC_SLEEP, METRIC_SWEAT,
]

# Périodes d'historique
PERIODS = [("24h", "24 H"), ("7d", "7 J"), ("30d", "30 J")]
