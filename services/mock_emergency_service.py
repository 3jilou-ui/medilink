"""Service d'urgence SIMULÉ.

Aucun appel réel : ne contacte jamais un vrai hôpital, ne dépêche jamais
une vraie ambulance. Uniquement des statuts de démonstration.
"""
import threading

from services.emergency_service import EmergencyService

STAGES = [
    (0.0, "Recherche des secours..."),
    (1.2, "Structure de santé sélectionnée"),
    (2.4, "Ambulance demandée"),
    (3.6, "Ambulance en route"),
]


class MockEmergencyService(EmergencyService):
    def __init__(self, time_scale=1.0):
        self.time_scale = time_scale
        self._timers = []
        self.status = "Aucune demande en cours"
        self.eta_seconds = None
        self.facility = None
        self.cancelled = False

    def request_ambulance(self, facility, location, callback):
        self.cancel_request()
        self.cancelled = False
        self.facility = facility
        distance = getattr(facility, "distance", 2.0) or 2.0
        # ~40 km/h en ville
        self.eta_seconds = max(180, int(distance / 40.0 * 3600))

        def _fire(text, with_eta):
            if self.cancelled:
                return
            self.status = text
            callback(text, self.eta_seconds if with_eta else None)

        for delay, text in STAGES:
            t = threading.Timer(delay * self.time_scale,
                                _fire, args=(text, text == "Ambulance en route"))
            t.daemon = True
            t.start()
            self._timers.append(t)
        return True

    def cancel_request(self):
        self.cancelled = True
        for t in self._timers:
            t.cancel()
        self._timers.clear()
        self.status = "Demande annulée"

    def get_status(self):
        return {
            "status": self.status,
            "eta_seconds": self.eta_seconds,
            "facility": self.facility,
            "cancelled": self.cancelled,
        }
