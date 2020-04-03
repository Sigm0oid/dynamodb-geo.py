from .GeoQueryInput import GeoQueryInput


class QueryRadiusRequest(GeoQueryInput):

    def __init__(self, centerPoint, radiusInMeter, query_input_dict={}):
        GeoQueryInput.__init__(self, query_input_dict)
        self.centerPoint = centerPoint
        self.radiusInMeter = radiusInMeter
        # super().__init__(self,query_input_dict)

    def getCenterPoint(self):
        return self.centerPoint

    def getRadiusInMeter(self):
        return self.radiusInMeter
