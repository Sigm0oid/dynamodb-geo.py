from GeoQueryInput import GeoQueryInput
from GeoPoint import GeoPoint


class QueryRadiusRequest(GeoQueryInput):

    def __init__(self, centerPoint: GeoPoint, radiusInMeter: int, query_input_dict: dict = {}):
        GeoQueryInput.__init__(self, query_input_dict)
        self.centerPoint = centerPoint
        self.radiusInMeter = radiusInMeter

    def getCenterPoint(self) -> GeoPoint:
        return self.centerPoint

    def getRadiusInMeter(self) -> int:
        return self.radiusInMeter
