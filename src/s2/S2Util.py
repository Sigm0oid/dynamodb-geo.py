from s2sphere import LatLng as S2LatLng
from s2sphere import LatLngRect as S2LatLngRect


class S2Util:
    def latLngRectFromQueryRectangleInput(self, QueryRectangleInput):
        queryRectangleRequest = QueryRectangleInput
        minPoint = queryRectangleRequest.getMinPoint()
        maxPoint = queryRectangleRequest.getMaxPoint()
        latLngRect = None
        if minPoint is not None and maxPoint is not None:
            minLatLng = S2LatLng.from_degrees(
                minPoint.getLatitude(), maxPoint.getLongitude())
            maxLatLng = S2LatLng.from_degrees(
                maxPoint.getLatitude(), maxPoint.getLongitude())
            latLngRect = S2LatLngRect.from_point_pair(minLatLng, maxLatLng)
        return latLngRect
