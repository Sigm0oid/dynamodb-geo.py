class QueryRadiusRequest:

    def __init__(self, centerPoint, radiusInMeter):
        self.centerPoint = centerPoint
        self.radiusInMeter = radiusInMeter

    def getCenterPoint(self):
        return self.centerPoint

    def getRadiusInMeter(self):
        return self.radiusInMeter
