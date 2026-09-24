"""Interface du service d'urgence (demande d'ambulance)."""
from abc import ABC, abstractmethod


class EmergencyService(ABC):
    @abstractmethod
    def request_ambulance(self, facility, location, callback):
        """callback(statut_texte, eta_secondes_ou_None)."""

    @abstractmethod
    def cancel_request(self):
        ...

    @abstractmethod
    def get_status(self):
        ...
