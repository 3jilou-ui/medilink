"""Assistant IA simulé : consignes prédéfinies, aucune connexion requise."""
from services.gemini_assistant import FALLBACK_GUIDANCE, GeminiAssistant


class MockGeminiAssistant(GeminiAssistant):
    def available(self):
        return True

    def get_initial_guidance(self, context):
        parameter = (context or {}).get("abnormal_parameter")
        lines = []
        if parameter == "spo2":
            lines.append("Asseyez le patient, épaules relâchées.")
            lines.append("Libérez les voies respiratoires et desserrez "
                         "les vêtements serrés.")
        elif parameter == "heart_rate":
            lines.append("Faites asseoir le patient au calme.")
            lines.append("Respirez lentement avec lui pour le rassurer.")
        elif parameter == "temperature":
            lines.append("Hydratez le patient par petites gorgées.")
            lines.append("Retirez les couches de vêtements superflues.")
        elif parameter == "glucose":
            lines.append("Si le patient est conscient, donnez un sucre rapide.")
        else:
            lines.append("Restez auprès du patient.")
        lines.extend([
            "Vérifiez qu'il respire normalement.",
            "Gardez le patient au calme.",
            "Les secours sont en cours d'intervention.",
        ])
        return lines

    def chat(self, message, context):
        msg = (message or "").lower()
        if "conscient" in msg:
            return ("C'est un bon signe. Restez avec lui, parlez-lui "
                    "calmement et surveillez sa respiration jusqu'à "
                    "l'arrivée des secours.")
        if "respire" in msg:
            return ("Si la respiration est difficile, asseyez le patient "
                    "et desserrez ses vêtements. Ne le laissez pas seul.")
        if "bracelet" in msg or "positionné" in msg or "capteur" in msg:
            return ("Repositionnez le bracelet bien à plat sur le poignet. "
                    "Une mesure incorrecte peut expliquer une valeur "
                    "anormale. Utilisez « Nouvelle mesure » après ajustement.")
        if "ambulance" in msg or "secours" in msg:
            status = (context or {}).get("ambulance_status", "")
            return f"Statut actuel : {status}. Restez joignable par téléphone."
        if "peur" in msg or "stress" in msg or "calme" in msg:
            return ("Respirez lentement et restez près du patient. Votre "
                    "calme l'aide directement. Les secours arrivent.")
        return ("Notez ce que vous observez et restez auprès du patient. "
                "Les secours sont prévenus ; suivez les consignes affichées.")
