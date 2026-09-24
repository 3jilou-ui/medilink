"""AlertManager : écoute les mesures et crée les alertes médicales."""
from models.alert import AlertStatus, MedicalAlert, Severity
from utils.formatting import fmt_value
from utils.thresholds import CRITICAL, NORMAL, WARNING, ThresholdEngine


class AlertManager:
    def __init__(self, engine=None):
        self.engine = engine or ThresholdEngine()
        self.alerts = []            # historique complet (plus récent d'abord)
        self._active = {}           # metric -> MedicalAlert active
        self._listeners = []

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self, alert):
        for cb in list(self._listeners):
            cb(alert)

    # ------------------------------------------------------------------
    def process(self, health_data, patient, location=None):
        """Analyse une mesure ; crée / résout les alertes. Retourne les
        alertes nouvellement créées."""
        created = []
        statuses = self.engine.evaluate_health_data(health_data)
        for metric, status in statuses.items():
            active = self._active.get(metric)
            if status == CRITICAL:
                if active is None or active.severity != Severity.CRITICAL:
                    if active is not None:
                        active.resolve("Remplacée par une alerte critique")
                    alert = self._create(metric, health_data, patient,
                                         Severity.CRITICAL, location)
                    created.append(alert)
            elif status == WARNING:
                if active is None:
                    alert = self._create(metric, health_data, patient,
                                         Severity.WARNING, location)
                    created.append(alert)
            else:  # NORMAL
                if active is not None and active.severity == Severity.WARNING:
                    active.resolve()
                    del self._active[metric]
                    self._notify(active)
        return created

    def _create(self, metric, health_data, patient, severity, location):
        alert = MedicalAlert(
            parameter=metric,
            value=fmt_value(metric, health_data.value_for(metric)),
            severity=severity,
            patient_id=patient.id if patient else "",
            patient_name=patient.name if patient else "",
            location=(location[0], location[1]) if location else None,
        )
        self.alerts.insert(0, alert)
        self._active[metric] = alert
        self._notify(alert)
        return alert

    # ------------------------------------------------------------------
    def active_alerts(self):
        return list(self._active.values())

    def active_for(self, metric):
        return self._active.get(metric)

    def close_alert(self, alert, status=AlertStatus.CANCELLED, reason=""):
        if status == AlertStatus.CANCELLED:
            alert.cancel(reason)
        else:
            alert.resolve(reason)
        for metric, act in list(self._active.items()):
            if act is alert:
                del self._active[metric]
        self._notify(alert)

    def get(self, alert_id):
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None

    def filtered(self, kind="all"):
        if kind == "all":
            return list(self.alerts)
        if kind == "critical":
            return [a for a in self.alerts if a.severity == Severity.CRITICAL]
        if kind == "warning":
            return [a for a in self.alerts if a.severity == Severity.WARNING]
        if kind == "resolved":
            return [a for a in self.alerts if a.status == AlertStatus.RESOLVED]
        if kind == "cancelled":
            return [a for a in self.alerts if a.status == AlertStatus.CANCELLED]
        return list(self.alerts)
