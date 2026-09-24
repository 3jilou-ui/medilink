# Backend MediLink (proxy Gemini)

Ce backend FastAPI est le **seul** endroit où la clé Gemini existe.
L'application mobile ne contient aucune clé API : elle appelle
`POST /api/emergency-guidance` et affiche la réponse ou bascule sur ses
consignes de repli si le backend est injoignable.

## Installation

```powershell
# PowerShell
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```cmd
rem cmd
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Clé API

```powershell
copy .env.example .env
# puis éditer .env : GEMINI_API_KEY=votre_cle
```

La clé peut aussi être passée par variable d'environnement
`GEMINI_API_KEY`. Ne jamais commiter `.env`.

## Lancement

```powershell
.venv\Scripts\python.exe server.py
# ou
.venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000
```

## Endpoints

- `GET /api/health` : état du service + `gemini_configured`.
- `POST /api/emergency-guidance` : corps
  `{"context": {...}, "message": "question éventuelle"}` →
  `{"guidance": ["consigne 1", ...], "reply": "texte"}`.

Contexte attendu (envoyé par l'app) : âge du patient, valeurs de santé,
paramètre anormal, sévérité, horodatage, position, structure la plus proche,
statut des secours.

Sans clé ou en cas d'erreur Gemini, l'endpoint répond
`{"guidance": null, ...}` ; l'application mobile affiche alors ses consignes
de repli prédéfinies sans interrompre le protocole d'urgence.
