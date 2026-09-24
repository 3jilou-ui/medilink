"""EmergencyManager : machine à états explicite du protocole d'urgence.

SANTE -> DANGER -> ALERTE -> LOCALISATION -> STRUCTURE PROCHE ->
AMBULANCE -> ASSISTANT IA -> CONSIGNES -> ANNULATION / RESOLUTION.

Les transitions sont déclaratives : aucun enchevêtrement de booléens.
"""
import threading

from models.emergency import (ACTIVE_STATES, EmergencyState, TimelineEntry)

S = EmergencyState

ALLOWED_TRANSITIONS = {
    S.NORMAL: {S.WARNING, S.CRITICAL, S.ALERT_CREATED},
    S.WARNING: {S.NORMAL, S.CRITICAL, S.ALERT_CREATED},
    S.CRITICAL: {S.NORMAL, S.ALERT_CREATED},
    S.ALERT_CREATED: {S.LOCATING_PATIENT, S.CANCELLED, S.FAILED},
    S.LOCATING_PATIENT: {S.FACILITY_FOUND, S.CANCELLED, S.FAILED},
    S.FACILITY_FOUND: {S.AMBULANCE_REQUESTED, S.CANCELLED, S.FAILED},
    S.AMBULANCE_REQUESTED: {S.AI_ASSISTANCE_ACTIVE, S.CANCELLED, S.FAILED},
    S.AI_ASSISTANCE_ACTIVE: {S.CANCELLED, S.RESOLVED, S.FAILED},
    S.CANCELLED: {S.NORMAL},
    S.RESOLVED: {S.NORMAL},
    S.FAILED: {S.NORMAL},
}


class EmergencyManager:
    def __init__(self, location_provider, facility_service,
                 emergency_service, time_scale=1.0, scheduler=None):
        self.location_provider = location_provider
        facility_service_ref = facility_service
        self.facility_service = facility_service_ref
        self.emergency_service = emergency_service
        self.time_scale = time_scale
        # scheduler(fn, delay) injectable pour les tests (delay=0).
        self._scheduler = scheduler or self._default_scheduler

        self.state = S.NORMAL
        self.timeline = []
        self.alert = None
        self.facility = None
        self.distance_km = None
        self.location = None
        self.ambulance_status = "Aucune demande en cours"
        self.eta_seconds = None
        self.cancel_reason = ""
        self._listeners = []

    # -- infrastructure -------------------------------------------------
    @staticmethod
    def _default_scheduler(fn, delay):
        t = threading.Timer(delay, fn)
        t.daemon = True
        t.start()
        return t

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self):
        for cb in list(self._listeners):
            cb(self)

    def _set_state(self, new_state):
        allowed = ALLOWED_TRANSITIONS.get(self.state, set())
        if new_state not in allowed:
            raise ValueError(
                f"Transition interdite : {self.state.value} -> {new_state.value}")
        self.state = new_state
        self._notify()

    def _log(self, label, state=None):
        self.timeline.append(TimelineEntry(label=label,
                                           state=state or self.state))
        self._notify()

    @property
    def is_active(self):
        return self.state in ACTIVE_STATES

    # -- protocole ------------------------------------------------------
    def start(self, alert):
        if self.is_active:
            return False
        self.alert = alert
        self.timeline.clear()
        self.cancel_reason = ""
        if self.state in (S.CANCELLED, S.RESOLVED, S.FAILED):
            self.state = S.NORMAL
        self._set_state(S.CRITICAL)
        self._log("Anomalie détectée", S.CRITICAL)
        self._set_state(S.ALERT_CREATED)
        self._log("Alerte créée", S.ALERT_CREATED)
        self._scheduler(self._step_locate, 0.8 * self.time_scale)
        return True

    def _step_locate(self):
        if not self.is_active:
            return
        self._set_state(S.LOCATING_PATIENT)
        self._log("Localisation du patient en cours", S.LOCATING_PATIENT)
        try:
            lat, lon, address = self.location_provider.get_current_location()
        except Exception:
            self._fail("Localisation indisponible")
            return
        self.location = (lat, lon, address)
        self._log("Patient localisé", S.LOCATING_PATIENT)
        self._scheduler(self._step_facility, 0.6 * self.time_scale)

    def _step_facility(self):
        if not self.is_active:
            return
        try:
            facility, distance = self.facility_service.find_nearest_facility(
                self.location)
        except Exception:
            facility, distance = None, None
        if facility is None:
            self._fail("Aucune structure de santé trouvée")
            return
        self.facility = facility
        self.distance_km = distance
        if self.alert is not None:
            self.alert.facility = facility.name
        self._set_state(S.FACILITY_FOUND)
        self._log(f"Clinique la plus proche identifiée : {facility.name}",
                  S.FACILITY_FOUND)
        self._scheduler(self._step_ambulance, 0.6 * self.time_scale)

    def _step_ambulance(self):
        if not self.is_active:
            return
        self._set_state(S.AMBULANCE_REQUESTED)
        self._log("Ambulance demandée", S.AMBULANCE_REQUESTED)
        self.emergency_service.request_ambulance(
            self.facility, self.location, self._on_ambulance_status)
        self._scheduler(self._step_ai, 1.0 * self.time_scale)

    def _on_ambulance_status(self, text, eta_seconds):
        self.ambulance_status = text
        if eta_seconds:
            self.eta_seconds = eta_seconds
            self._log(f"Ambulance en route — temps estimé "
                      f"{int(eta_seconds // 60):02d}:{int(eta_seconds % 60):02d}",
                      self.state)
        self._notify()

    def _step_ai(self):
        if not self.is_active:
            return
        self._set_state(S.AI_ASSISTANCE_ACTIVE)
        self._log("Assistant IA activé", S.AI_ASSISTANCE_ACTIVE)
        self._log("Consignes affichées", S.AI_ASSISTANCE_ACTIVE)

    def _fail(self, reason):
        self.state = S.FAILED
        self._log(f"Échec : {reason}", S.FAILED)

    # -- issue ----------------------------------------------------------
    def cancel(self, reason="Valeur incorrecte / mesure suspecte"):
        if not self.is_active:
            return False
        self.cancel_reason = reason
        self.emergency_service.cancel_request()
        self.ambulance_status = "Demande annulée"
        self._set_state(S.CANCELLED)
        self._log(f"Alerte annulée — {reason}", S.CANCELLED)
        return True

    def resolve(self, reason="Retour à des valeurs normales"):
        if not self.is_active:
            return False
        self.emergency_service.cancel_request()
        self.ambulance_status = "Intervention terminée"
        self._set_state(S.RESOLVED)
        self._log(reason, S.RESOLVED)
        return True

    def reset(self):
        self.emergency_service.cancel_request()
        self.state = S.NORMAL
        self.timeline.clear()
        self.alert = None
        self.facility = None
        self.distance_km = None
        self.location = None
        self.eta_seconds = None
        self.ambulance_status = "Aucune demande en cours"
        self.cancel_reason = ""
        self._notify()
