"""Backend MediLink : proxy Gemini pour l'assistant d'urgence.

Aucune clé API n'est embarquée dans l'application mobile : le mobile appelle
ce backend, qui seul détient GEMINI_API_KEY (environnement ou backend/.env).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional

from gemini_gateway import GeminiGateway

app = FastAPI(title="MediLink Backend", version="1.0.0",
              description="Proxy Gemini du prototype MediLink.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway = GeminiGateway()


class GuidanceRequest(BaseModel):
    context: Dict[str, Any] = {}
    message: Optional[str] = None


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "medilink-backend",
            "gemini_configured": gateway.configured()}


@app.post("/api/emergency-guidance")
def emergency_guidance(req: GuidanceRequest):
    text = gateway.generate(req.context, req.message)
    if not text:
        return {"guidance": None, "reply": None,
                "error": "Gemini indisponible ou clé absente"}
    lines = GeminiGateway.to_lines(text)
    if req.message:
        return {"guidance": lines, "reply": text}
    return {"guidance": lines, "reply": None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
