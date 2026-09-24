"""Client HTTP minimal vers le backend MediLink (proxy Gemini).

Aucune clé API côté mobile : le backend fait office de passerelle.
"""
import json
import urllib.error
import urllib.request


class BackendApiClient:
    def __init__(self, base_url, timeout=6.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def post_json(self, path, payload):
        """Retourne le dict JSON ou None en cas d'échec (jamais d'exception)."""
        url = self.base_url + path
        data = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError):
            return None

    def get_json(self, path):
        try:
            with urllib.request.urlopen(self.base_url + path,
                                        timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError):
            return None
