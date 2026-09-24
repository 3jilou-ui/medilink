"""Recherche de la structure de santé la plus proche (Haversine)."""
from models.facility import MOCK_FACILITIES, haversine_km


class FacilityService:
    def __init__(self, facilities=None):
        self.facilities = facilities if facilities is not None else MOCK_FACILITIES

    def find_facilities(self, location, limit=None):
        """Retourne [(facility, distance_km)] triée par distance."""
        lat, lon = location[0], location[1]
        ranked = []
        for fac in self.facilities:
            dist = haversine_km(lat, lon, fac.latitude, fac.longitude)
            fac.distance = dist
            ranked.append((fac, dist))
        ranked.sort(key=lambda item: item[1])
        return ranked[:limit] if limit else ranked

    def find_nearest_facility(self, location):
        ranked = self.find_facilities(location)
        if not ranked:
            return None, None
        return ranked[0]
