"""Tests de FacilityService : Haversine, tri par distance, plus proche."""
from models.facility import Facility, haversine_km
from services.facility_service import FacilityService

# Position de référence : Sfax (Tunisie), comme le patient démo.
SFAX = (34.7406, 10.7603)


def test_haversine_zero_for_same_point():
    assert haversine_km(34.74, 10.76, 34.74, 10.76) == 0.0


def test_haversine_known_distance():
    # ~1 degré de latitude ≈ 111 km.
    d = haversine_km(0.0, 0.0, 1.0, 0.0)
    assert 110 <= d <= 112


def test_haversine_symmetric():
    a = haversine_km(34.74, 10.76, 34.80, 10.90)
    b = haversine_km(34.80, 10.90, 34.74, 10.76)
    assert abs(a - b) < 1e-6


def test_find_facilities_sorted_by_distance():
    facs = [
        Facility(id="A", name="Loin", type="Clinique", latitude=35.5,
                 longitude=11.5),
        Facility(id="B", name="Pres", type="Clinique", latitude=34.75,
                 longitude=10.76),
    ]
    svc = FacilityService(facs)
    ranked = svc.find_facilities(SFAX)
    assert ranked[0][0].name == "Pres"
    assert ranked[0][1] <= ranked[1][1]


def test_find_nearest_facility_returns_closest():
    svc = FacilityService()          # MOCK_FACILITIES par défaut
    fac, dist = svc.find_nearest_facility(SFAX)
    assert fac is not None
    assert dist is not None
    assert dist >= 0
    # la plus proche doit être la première du classement complet
    ranked = svc.find_facilities(SFAX)
    assert ranked[0][0].id == fac.id


def test_limit_parameter():
    svc = FacilityService()
    assert len(svc.find_facilities(SFAX, limit=1)) == 1


def test_empty_service_returns_none():
    svc = FacilityService([])
    fac, dist = svc.find_nearest_facility(SFAX)
    assert fac is None and dist is None
