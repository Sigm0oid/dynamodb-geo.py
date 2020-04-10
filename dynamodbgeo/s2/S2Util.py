from s2sphere import LatLng as S2LatLng
from s2sphere import LatLngRect as S2LatLngRect
EARTH_RADIUS_METERS = 6367000.0


class S2Util:
    def latLngRectFromQueryRectangleInput(self, QueryRectangleRequest: 'QueryRectangleRequest'):
        queryRectangleRequest = QueryRectangleRequest
        minPoint = queryRectangleRequest.getMinPoint()
        maxPoint = queryRectangleRequest.getMaxPoint()
        latLngRect = None
        if minPoint is not None and maxPoint is not None:
            minLatLng = S2LatLng.from_degrees(
                minPoint.getLatitude(), minPoint.getLongitude())
            maxLatLng = S2LatLng.from_degrees(
                maxPoint.getLatitude(), maxPoint.getLongitude())
            latLngRect = S2LatLngRect.from_point_pair(minLatLng, maxLatLng)
        return latLngRect

    def getBoundingLatLngRectFromQueryRadiusInput(self, QueryRadiusRequest: 'QueryRadiusRequest'):
        centerPoint = QueryRadiusRequest.getCenterPoint()
        radiusInMeter = QueryRadiusRequest.getRadiusInMeter()
        centerLatLng = S2LatLng.from_degrees(
            centerPoint.getLatitude(), centerPoint.getLongitude())
        latReferenceUnit = -1.0 if centerPoint.getLatitude() > 0.0 else 1.0
        latReferenceLatLng = S2LatLng.from_degrees(centerPoint.getLatitude() + latReferenceUnit,
                                                   centerPoint.getLongitude())
        lngReferenceUnit = -1.0 if centerPoint.getLongitude() > 0.0 else 1.0
        lngReferenceLatLng = S2LatLng.from_degrees(centerPoint.getLatitude(), centerPoint.getLongitude()
                                                   + lngReferenceUnit)
        latForRadius = radiusInMeter / \
            (centerLatLng.get_distance(latReferenceLatLng).radians * EARTH_RADIUS_METERS)
        lngForRadius = radiusInMeter / \
            (centerLatLng.get_distance(lngReferenceLatLng).radians * EARTH_RADIUS_METERS)
        minLatLng = S2LatLng.from_degrees(centerPoint.getLatitude() - latForRadius,
                                          centerPoint.getLongitude() - lngForRadius)
        maxLatLng = S2LatLng.from_degrees(centerPoint.getLatitude() + latForRadius,
                                          centerPoint.getLongitude() + lngForRadius)
        return S2LatLngRect(minLatLng, maxLatLng)
