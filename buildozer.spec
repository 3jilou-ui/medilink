[app]

# MediLink — prototype Kivy (build Android futur, non exécuté ici)
title = MediLink
package.name = medilink
package.domain = org.medilink.prototype

source.dir = .
source.include_exts = py,png,jpg,kv,ttf
source.include_patterns = kv/*,assets/*

version = 0.1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# ---------------------------------------------------------------- permissions
# Bluetooth / BLE : connexion au bracelet MediLink (implémentation future).
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,INTERNET,ACCESS_NETWORK_STATE,POST_NOTIFICATIONS,VIBRATE

# API Android minimale / cible
android.api = 33
android.minapi = 21

# Accepter les licences SDK de façon non interactive (nécessaire en CI).
android.accept_sdk_license = True

# Notifications locales (alertes critiques) : via plyer plus tard.
# Vibreur : retours d'urgence.
# Internet : uniquement pour joindre le backend MediLink (proxy Gemini).
# Aucune clé API n'est embarquée dans l'APK.

[buildozer]
log_level = 2
warn_on_root = 1
