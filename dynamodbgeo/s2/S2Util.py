from s2sphere import Angle as S2Angle
from s2sphere import Cap as S2Cap
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
        if radiusInMeter < 0:
            raise ValueError("radiusInMeter must be non-negative")
        centerLatLng = S2LatLng.from_degrees(
            centerPoint.getLatitude(), centerPoint.getLongitude())
        angle = S2Angle.from_radians(radiusInMeter / EARTH_RADIUS_METERS)
        return S2Cap.from_axis_angle(centerLatLng.to_point(), angle).get_rect_bound()
