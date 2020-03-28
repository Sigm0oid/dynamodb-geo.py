class QueryRectangleRequest:

    def __init__(self, minPoint, maxPoint):
        self.minPoint = minPoint
        self.maxPoint = maxPoint

    def getMinPoint(self):
        return self.minPoint

    def getMaxPoint(self):
        return self.maxPoint
