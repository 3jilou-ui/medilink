# MediLink — Application mobile (prototype)

MediLink est la **brique mobile** d'un écosystème de santé connecté :

```
bracelet MediLink (sans écran)  →  Bluetooth (BLE)  →  application mobile MediLink
        →  backend (proxy Gemini)  →  patient / aidant
        →  système d'urgence  →  structure de santé la plus proche  →  ambulance  →  professionnel
```

Ce dépôt contient **l'application mobile** (Python + Kivy pur, sans KivyMD) et le
**backend FastAPI** qui sert de proxy à Gemini. Les données du bracelet, la
localisation GPS, l'envoi d'ambulance et l'IA sont **simulés (mock)** dans ce
prototype, derrière des abstractions de services remplaçables sans toucher à l'UI.

> **Prototype de démonstration — les données affichées sont simulées et ne
> constituent pas un diagnostic médical.**
>
> **Cette application ne remplace pas l'avis d'un professionnel de santé.**

---

## 1. Prérequis

- Python **3.12** (testé avec CPython 3.12.14).
- Windows : PowerShell **ou** cmd. Les commandes des deux shells sont données.
- Environ 500 Mo d'espace pour l'environnement virtuel.

---

## 2. Installation

Toutes les commandes sont exécutées depuis la **racine du projet**.

### PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### cmd

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si l'activation du venv échoue sous PowerShell, vous pouvez appeler directement
l'interpréteur du venv (utile dans les scripts) :

```
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 3. Lancer l'application mobile

### PowerShell

```powershell
.venv\Scripts\python.exe main.py
```

### cmd

```cmd
.venv\Scripts\python.exe main.py
```

La fenêtre s'ouvre en résolution de test **390×844** (format mobile). L'interface
reste responsive : elle s'adapte à toute autre taille de fenêtre.

Parcours de démonstration complet (voir section « Mode démonstration ») :
**Connexion → Accueil → Simuler une urgence → Alerte critique → Localisation →
Clinique la plus proche → Ambulance → Assistant IA → Consignes → Annulation.**

---

## 4. Lancer le backend (proxy Gemini) — optionnel

Le backend n'est **nécessaire que si vous activez la vraie IA** (`AI_PROVIDER=api`).
Par défaut l'application tourne en IA simulée et fonctionne sans backend.

### PowerShell

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Éditer backend\.env et renseigner GEMINI_API_KEY=...
..\.venv\Scripts\python.exe server.py
```

### cmd

```cmd
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
REM Éditer backend\.env et renseigner GEMINI_API_KEY=...
..\.venv\Scripts\python.exe server.py
```

Le serveur écoute sur `http://127.0.0.1:8000` :

- `GET  /api/health` → `{"status","service","gemini_configured"}`
- `POST /api/emergency-guidance` → `{"guidance":[...],"reply":"..."}`

---

## 5. Sécurité — clé API Gemini

**La clé API n'est JAMAIS présente dans l'application mobile, ni codée en dur.**

- La clé vit uniquement dans `backend/.env` (ou dans la variable d'environnement
  `GEMINI_API_KEY` du serveur).
- `backend/.env.example` est fourni comme modèle : `GEMINI_API_KEY=`.
- `backend/.env` est listé dans `.gitignore` : ne le commitez jamais.
- L'application mobile parle au backend via HTTP ; elle ne voit jamais la clé.

Si la clé est absente ou si Gemini est injoignable, le backend renvoie `null` et
l'application bascule sur des **consignes de repli sûres** sans interrompre le
protocole d'urgence.

---

## 6. Mode démonstration

Le mode démo est activé par défaut (`DEMO_MODE=True`) : toutes les sources de
données (mesures, Bluetooth, GPS, ambulance, IA) sont simulées.

L'écran **Centre de démo** (accessible depuis le Profil) propose :

- **SIMULER UNE URGENCE** — valeurs critiques (FC 145, SpO₂ 87, 39,5 °C) puis
  déclenchement automatique du protocole d'urgence.
- **AVERTISSEMENT** — valeurs à surveiller (alerte WARNING).
- **LECTURE INCORRECTE** — valeurs aberrantes (capteur perturbé) pour tester
  l'annulation d'une fausse alerte et la « Nouvelle mesure ».
- **ANNULATION** — annule l'alerte en cours.
- **RESET** — remet l'application en surveillance normale.

Le facteur d'accélération `TIME_SCALE` (variable d'environnement) réduit les
temporisations du protocole ; `TIME_SCALE=0` rend les étapes quasi instantanées
(pratique pour les captures et les tests).

---

## 7. Configurer Gemini (IA réelle)

1. Démarrez le backend (section 4) avec une clé valide dans `backend/.env`.
2. Faites pointer l'application sur le backend et activez le fournisseur `api` :

   **PowerShell**
   ```powershell
   $env:MEDILINK_AI_PROVIDER = "api"
   $env:MEDILINK_BACKEND_URL = "http://127.0.0.1:8000"
   .venv\Scripts\python.exe main.py
   ```

   **cmd**
   ```cmd
   set MEDILINK_AI_PROVIDER=api
   set MEDILINK_BACKEND_URL=http://127.0.0.1:8000
   .venv\Scripts\python.exe main.py
   ```

Si le backend est indisponible, l'application continue d'afficher les consignes de
repli — le protocole d'urgence n'est jamais interrompu.

---

## 8. Remplacer les services simulés par du réel

L'UI ne parle **qu'aux abstractions** ; jamais directement au Bluetooth, à Gemini
ou au GPS. Pour passer en réel, implémentez l'interface correspondante puis
changez le fournisseur dans `config.py` (ou via variable d'environnement) — sans
modifier aucun écran.

| Abstraction (`services/`)      | Mock actuel               | Variable d'env.             | Pour du réel                                  |
|--------------------------------|---------------------------|-----------------------------|-----------------------------------------------|
| `HealthDataProvider`           | `mock_data_provider.py`   | `MEDILINK_DATA_PROVIDER`    | flux de mesures du bracelet                   |
| `BluetoothManager`             | `mock_bluetooth.py`       | `MEDILINK_BLUETOOTH_PROVIDER`| `ble` — pile BLE native (Android/iOS)         |
| `LocationProvider`             | `mock_location.py`        | `MEDILINK_LOCATION_PROVIDER`| `gps` — géolocalisation native                |
| `EmergencyService`             | `mock_emergency_service.py`| `MEDILINK_EMERGENCY_PROVIDER`| intégration réelle de dispatch (hors prototype) |
| `GeminiAssistant`              | `mock_gemini.py`          | `MEDILINK_AI_PROVIDER`      | `api` → `gemini_api_assistant.py` + backend   |

**Le mock d'urgence ne fait jamais d'appel réel : il ne contacte aucun hôpital et
ne dépêche aucune ambulance.** Une implémentation réelle devra respecter les
contraintes légales et de sécurité applicables.

La fabrique des services est `services.build_services(config)` — un seul point
d'assemblage.

---

## 9. Tests

### PowerShell

```powershell
.venv\Scripts\python.exe -m pytest
```

### cmd

```cmd
.venv\Scripts\python.exe -m pytest
```

Les tests couvrent : `HealthData`, `Patient`, `ThresholdEngine`, `AlertManager`,
la machine à états `EmergencyManager` (transitions, annulation, résolution),
la distance Haversine et la structure la plus proche, `MockBluetoothManager` et
`MockGeminiAssistant`.

---

## 10. Build Android (APK)

`buildozer.spec` définit la construction Android et liste les permissions qui
seront requises par les implémentations **réelles** (aucune n'est utilisée par le
prototype 100 % mock) :

```
BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN,
ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION,
INTERNET, ACCESS_NETWORK_STATE, POST_NOTIFICATIONS, VIBRATE
```

Buildozer ne tourne que sous **Linux/WSL/macOS** (jamais sous Windows natif).

### Option A — GitHub Actions (recommandé, aucune installation locale)

Un workflow est fourni : `.github/workflows/build-apk.yml`.

1. Poussez ce projet sur un dépôt GitHub.
2. Ouvrez l'onglet **Actions** → **Build Android APK** → **Run workflow**
   (ou poussez un commit sur `main`).
3. À la fin de la build (~20–45 min la première fois, plus rapide ensuite grâce
   au cache), téléchargez l'artefact **`medilink-debug-apk`** en bas de la page
   du run : il contient le fichier `.apk`.
4. Copiez l'APK sur le téléphone, autorisez « sources inconnues », installez.

### Option B — Linux / WSL local

```bash
pip install buildozer cython
buildozer android debug      # APK généré dans bin/
```

Le fichier APK généré **ne contient aucune clé API** : l'IA passe toujours par le
backend. L'application étant 100 % mock, l'APK fonctionne de manière autonome
(aucun backend requis sur le téléphone pour la démonstration).

---

## 11. Variables d'environnement

Toutes les valeurs de `config.py` peuvent être surchargées par variables
d'environnement préfixées `MEDILINK_` :

| Variable                        | Défaut             | Rôle                                   |
|---------------------------------|--------------------|----------------------------------------|
| `MEDILINK_DEMO_MODE`            | `True`             | active les mocks                        |
| `MEDILINK_DATA_PROVIDER`        | `mock`             | fournisseur de mesures                  |
| `MEDILINK_BLUETOOTH_PROVIDER`   | `mock`             | pile Bluetooth                          |
| `MEDILINK_LOCATION_PROVIDER`    | `mock`             | localisation                            |
| `MEDILINK_EMERGENCY_PROVIDER`   | `mock`             | dispatch d'urgence                      |
| `MEDILINK_AI_PROVIDER`          | `mock`             | `mock` ou `api`                         |
| `MEDILINK_BACKEND_URL`          | `http://127.0.0.1:8000` | URL du backend FastAPI             |
| `MEDILINK_WINDOW_WIDTH/HEIGHT`  | `390` / `844`      | résolution de la fenêtre de test        |
| `MEDILINK_DATA_TICK_SECONDS`    | `3.0`              | intervalle entre deux mesures simulées  |
| `MEDILINK_TIME_SCALE`           | `1.0`              | accélération des temporisations (`0` = instantané) |

---

## 12. Structure du projet

```
74d195e5/
├── main.py                     # point d'entrée
├── config.py                   # configuration centrale (env MEDILINK_*)
├── requirements.txt
├── buildozer.spec              # build Android (permissions futures)
├── .gitignore
├── app/                        # shell applicatif
│   ├── application.py          # MediLinkApp + boucle de rafraîchissement
│   ├── navigation.py           # Navigator + BottomNav
│   └── state.py                # AppState (EventDispatcher)
├── models/                     # HealthData, Patient, Alert, Facility,
│   └── ...                     # Bracelet, Emergency (machine à états)
├── services/                   # abstractions + mocks + fabrique
│   ├── __init__.py             # build_services(config)
│   ├── *manager.py / *service.py
│   └── mock_*.py
├── screens/                    # login, home, health_detail, history, map,
│   └── ...                     # alerts, alert_detail, emergency,
│                               # ai_assistant, bracelet, profile, demo
├── widgets/                    # cards, graph, map, chat_bubble, bottom_nav…
├── utils/                      # thresholds, formatting, validators, constants
├── kv/
│   └── styles.kv               # thème médical sombre
├── backend/                    # proxy FastAPI pour Gemini
│   ├── server.py
│   ├── gemini_gateway.py       # SYSTEM_INSTRUCTION + appel REST Gemini
│   ├── requirements.txt
│   ├── .env.example            # GEMINI_API_KEY=  (jamais commiter .env)
│   └── README.md
└── tests/                      # pytest (modèles, services, urgence)
```

---

## 13. Note d'architecture

Règle dure respectée dans tout le code : **l'UI ne contient aucune logique
Bluetooth, Gemini, GPS ou de dispatch d'urgence.** Ces responsabilités vivent
dans les services, derrière des interfaces, assemblées par `build_services`.
Le remplacement d'un mock par une implémentation réelle ne demande **aucune**
modification des écrans.
