"""Modèle Facility + calcul de distance (Haversine) + données mock."""
import math
from dataclasses import dataclass


@dataclass
class Facility:
    id: str
    name: str
    type: str            # "Hopital" | "Clinique" | "Centre medical"
    latitude: float
    longitude: float
    phone: str = ""
    emergency_available: bool = False
    distance: float = 0.0   # km, rempli par FacilityService


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance orthodromique en kilomètres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


# Structures de santé simulées autour de Sfax (Tunisie).
MOCK_FACILITIES = [
    Facility(
        id="FAC-01", name="Clinique El Habib", type="Clinique",
        latitude=34.7550, longitude=10.7520,
        phone="+216 74 200 100", emergency_available=True,
    ),
    Facility(
        id="FAC-02", name="Hôpital Universitaire Hédi Chaker", type="Hôpital",
        latitude=34.7180, longitude=10.7380,
        phone="+216 74 241 000", emergency_available=True,
    ),
    Facility(
        id="FAC-03", name="Centre Médical Sfax Nord", type="Centre médical",
        latitude=34.7710, longitude=10.7860,
        phone="+216 74 400 300", emergency_available=False,
    ),
]
