from .GeoQueryInput import GeoQueryInput 


class QueryRectangleRequest(GeoQueryInput):

    def __init__(self, minPoint, maxPoint,query_input_dict={}):
        GeoQueryInput.__init__(self,query_input_dict)
        self.minPoint = minPoint
        self.maxPoint = maxPoint

    def getMinPoint(self):
        return self.minPoint

    def getMaxPoint(self):
        return self.maxPoint
