import dynamodbgeo
from dynamodbgeo.s2 import S2Util
from s2sphere.sphere import LatLng, LatLngRect


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.874444, 10.241059),
        95, {}, sort=True)
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
        qri)
    assert latLngRect is not None


def test_S2LatLngRect_NewZealand2():
    p1_conv = LatLng.from_degrees(-52.71152508854678, 157.99825332608728)
    print(p1_conv)
    p2_conv = LatLng.from_degrees(-31.329586226597584, 179.77995299846089)
    print(p2_conv)

    rect = LatLngRect(p1_conv,
                      p2_conv)
    assert rect is not None


def test_S2LatLngRect_NewZealand():
    rect = LatLngRect(LatLng.from_degrees(-52.71152508854678, 157.99825332608728),
                      LatLng.from_degrees(-31.329586226597584, 180.0))
    assert rect is not None


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput_NewZealand():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(-42.02055565757218, 172.38910316227407),
        1188035.19116924, {}, sort=True)
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
        qri)
    assert latLngRect is not None
    # Point across the +-180 antimeridian (~700 km east of center) must be inside the bounding rect
    assert latLngRect.contains(LatLng.from_degrees(-42.0, -179.0))


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput_NorthPole():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(90.0, 0.0),
        10000.0, {})
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(qri)
    assert latLngRect is not None
    assert latLngRect.contains(LatLng.from_degrees(89.95, -135.0))
    assert latLngRect.contains(LatLng.from_degrees(89.95, 135.0))
