import dynamodbgeo
from dynamodbgeo.s2 import S2Util
from s2sphere.sphere import LatLng, LatLngRect
from truth.truth import AssertThat


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.874444, 10.241059),
        95, {}, sort=True)
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
        qri)
    AssertThat(latLngRect).IsNotNone()


def test_S2LatLngRect_NewZealand2():
    p1_conv = LatLng.from_degrees(-52.71152508854678, 157.99825332608728)
    print(p1_conv)
    p2_conv = LatLng.from_degrees(-31.329586226597584, 179.77995299846089)
    print(p2_conv)

    rect = LatLngRect(p1_conv,
                      p2_conv)
    AssertThat(rect).IsNotNone()
# It fails bc the max long is 180 and max lat is 90 so as logn as less than 180 it will work, why does the radius query return a long of 186??


def test_S2LatLngRect_NewZealand():
    rect = LatLngRect(LatLng.from_degrees(-52.71152508854678, 157.99825332608728),
                      LatLng.from_degrees(-31.329586226597584, 180.0))
    AssertThat(rect).IsNotNone()


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput_NewZealand():
    # "pathParameters": {
    #     "lat": "-42.02055565757218",
    #     "lng": "172.38910316227407",
    #     "radius": "1188035.19116924",
    #     "proxy": "/path/to/resource"
    # },

    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(-42.02055565757218, 172.38910316227407),
        1188035.19116924, {}, sort=True)
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
        qri)
    AssertThat(latLngRect).IsNotNone()
    # Point across the +-180 antimeridian (~700 km east of center) must be inside the bounding rect
    AssertThat(latLngRect.contains(LatLng.from_degrees(-42.0, -179.0))).IsTrue()


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput_NorthPole():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(90.0, 0.0),
        10000.0, {})
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(qri)
    AssertThat(latLngRect).IsNotNone()
    AssertThat(latLngRect.contains(LatLng.from_degrees(89.95, -135.0))).IsTrue()
    AssertThat(latLngRect.contains(LatLng.from_degrees(89.95, 135.0))).IsTrue()
