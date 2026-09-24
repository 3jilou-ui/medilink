"""Assistant IA réel : passe par le backend FastAPI (jamais de clé en local).

Si le backend est injoignable, `available()` reste True mais les appels
retournent None ; l'écran bascule alors sur FALLBACK_GUIDANCE sans
interrompre le protocole d'urgence.
"""
from services.api_client import BackendApiClient
from services.gemini_assistant import GeminiAssistant


class GeminiApiAssistant(GeminiAssistant):
    def __init__(self, base_url):
        self.client = BackendApiClient(base_url)

    def available(self):
        return self.client.get_json("/api/health") is not None

    def get_initial_guidance(self, context):
        resp = self.client.post_json("/api/emergency-guidance",
                                     {"context": context, "message": None})
        if not resp:
            return None
        guidance = resp.get("guidance")
        if isinstance(guidance, list):
            return [str(g) for g in guidance]
        if isinstance(guidance, str):
            return [guidance]
        return None

    def chat(self, message, context):
        resp = self.client.post_json("/api/emergency-guidance",
                                     {"context": context, "message": message})
        if not resp:
            return None
        reply = resp.get("reply") or resp.get("guidance")
        if isinstance(reply, list):
            reply = " ".join(str(r) for r in reply)
        return str(reply) if reply else None
