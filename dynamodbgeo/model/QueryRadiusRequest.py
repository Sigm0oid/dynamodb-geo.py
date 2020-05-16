from GeoQueryInput import GeoQueryInput
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class QueryRadiusRequest(GeoQueryInput):

    def __init__(self, centerPoint: 'GeoPoint', radiusInMeter: int, query_input_dict: dict = {}, sort: bool = False):
        GeoQueryInput.__init__(self, query_input_dict)
        self.centerPoint = centerPoint
        self.radiusInMeter = radiusInMeter
        self.sort = sort

    def getCenterPoint(self) -> 'GeoPoint':
        return self.centerPoint

    def getRadiusInMeter(self) -> int:
        return self.radiusInMeter
