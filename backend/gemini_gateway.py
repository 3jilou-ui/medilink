"""Passerelle Gemini : la clé API reste côté backend, jamais côté mobile."""
import json
import os
import urllib.error
import urllib.request

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-2.0-flash:generateContent")

SYSTEM_INSTRUCTION = (
    "You are an emergency-support assistant inside a medical technology "
    "prototype.\n"
    "\n"
    "You provide calm, concise, general emergency-support guidance to a "
    "patient's caretaker while professional emergency services are being "
    "arranged.\n"
    "\n"
    "You do not diagnose.\n"
    "You do not replace emergency professionals.\n"
    "You must never invent measurements.\n"
    "Use only the supplied patient context.\n"
    "Do not prescribe medication.\n"
    "Do not invent doses.\n"
    "Do not claim certainty that the patient is safe.\n"
    "When serious danger is suspected, professional emergency services take "
    "priority.\n"
    "\n"
    "Respond in French.\n"
    "\n"
    "Keep instructions short and easy to understand."
)


def load_api_key():
    """GEMINI_API_KEY depuis l'environnement, sinon backend/.env."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"\'')
    return ""


def build_user_prompt(context, message=None):
    ctx = context or {}
    lines = [
        "Contexte patient fourni par l'application MediLink :",
        f"- âge du patient : {ctx.get('patient_age')}",
        f"- valeurs actuelles : {ctx.get('health_values')}",
        f"- paramètre anormal : {ctx.get('abnormal_parameter')} "
        f"({ctx.get('abnormal_value')})",
        f"- sévérité : {ctx.get('severity')}",
        f"- horodatage : {ctx.get('timestamp')}",
        f"- position : {ctx.get('location')}",
        f"- structure la plus proche : {ctx.get('nearest_clinic')}",
        f"- statut des secours : {ctx.get('ambulance_status')}",
    ]
    if message:
        lines.append(f"\nQuestion de l'accompagnant : {message}")
    else:
        lines.append("\nDonne immédiatement 3 à 5 consignes courtes pour "
                     "l'accompagnant.")
    lines.append("\nRéponds en français, une consigne par ligne, sans "
                 "numérotation.")
    return "\n".join(lines)


class GeminiGateway:
    """Appelle l'API Gemini et retourne du texte français, ou None."""

    def __init__(self, api_key=None, timeout=12.0):
        self.api_key = api_key if api_key is not None else load_api_key()
        self.timeout = timeout

    def configured(self):
        return bool(self.api_key)

    def generate(self, context, message=None):
        if not self.configured():
            return None
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user",
                          "parts": [{"text": build_user_prompt(context,
                                                                message)}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 300},
        }
        req = urllib.request.Request(
            GEMINI_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "x-goog-api-key": self.api_key},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError):
            return None
        try:
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, IndexError, TypeError):
            return None

    @staticmethod
    def to_lines(text):
        if not text:
            return []
        return [ln.strip(" -•\t") for ln in text.splitlines()
                if ln.strip(" -•\t")]
