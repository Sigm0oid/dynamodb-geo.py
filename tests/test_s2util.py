import dynamodbgeo
from dynamodbgeo.util import GeoTableUtil
from truth.truth import AssertThat
from dynamodbgeo.s2 import S2Util
from dynamodbgeo.model import QueryRadiusRequest


def test_s2util_getBoundingLatLngRectFromQueryRadiusInput():
    qri = dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(36.874444, 10.241059),
        95, {}, sort=True)
    latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
        qri)
    AssertThat(latLngRect).IsNotNone()


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
