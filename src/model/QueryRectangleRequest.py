from GeoQueryInput import GeoQueryInput
from GeoPoint import GeoPoint


class QueryRectangleRequest(GeoQueryInput):

    def __init__(self, minPoint: GeoPoint, maxPoint: GeoPoint, query_input_dict: dict = {}):
        GeoQueryInput.__init__(self, query_input_dict)
        self.minPoint = minPoint
        self.maxPoint = maxPoint

    def getMinPoint(self) -> GeoPoint:
        return self.minPoint

    def getMaxPoint(self) -> GeoPoint:
        return self.maxPoint
