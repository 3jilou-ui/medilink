"""Interface de l'assistant IA d'urgence (Gemini via backend)."""
from abc import ABC, abstractmethod

# Consignes de repli, sûres et prédéfinies, si l'IA est indisponible.
FALLBACK_GUIDANCE = [
    "Restez auprès du patient.",
    "Vérifiez qu'il respire normalement.",
    "Gardez le patient au calme, en position assise ou allongée.",
    "Ne donnez aucun médicament sans avis médical.",
    "Les secours sont en cours d'intervention.",
]


class GeminiAssistant(ABC):
    @abstractmethod
    def available(self):
        ...

    @abstractmethod
    def get_initial_guidance(self, context):
        """Retourne une liste de consignes courtes en français, ou None."""

    @abstractmethod
    def chat(self, message, context):
        """Retourne une réponse courte en français, ou None."""

    @staticmethod
    def build_context(patient, health_data, alert, facility, ambulance_status,
                      location=None):
        return {
            "patient_age": getattr(patient, "age", None),
            "patient_name": getattr(patient, "name", None),
            "health_values": health_data.as_dict() if health_data else None,
            "abnormal_parameter": alert.parameter if alert else None,
            "abnormal_value": alert.value if alert else None,
            "severity": alert.severity.value if alert else None,
            "timestamp": alert.timestamp if alert else None,
            "location": list(location) if location else None,
            "nearest_clinic": facility.name if facility else None,
            "ambulance_status": ambulance_status,
        }
