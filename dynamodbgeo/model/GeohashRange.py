from dynamodbgeo import GeoDataManagerConfiguration
from dynamodbgeo.s2 import S2Manager
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GeohashRange:
    def __init__(self, range1: int, range2: int):
        self.rangeMin = min(range1, range2)
        self.rangeMax = max(range1, range2)

    def getRangeMin(self) -> int:
        return self.rangeMin

    def setRangeMin(self, rangeMin: int):
        self.rangeMin = rangeMin

    def getRangeMax(self) -> int:
        return self.rangeMax

    def setRangeMax(self, rangeMax: int):
        self.rangeMax = rangeMax

    def tryMerge(self, range: int) -> bool:
        if range.getRangeMin() - self.rangeMax <= GeoDataManagerConfiguration.MERGE_THRESHOLD and range.getRangeMin() - self.rangeMax > 0:
            self.rangeMax = range.getRangeMax()
            return True
        if self.rangeMin - range.getRangeMax() <= GeoDataManagerConfiguration.MERGE_THRESHOLD and self.rangeMin - range.getRangeMax() > 0:
            self.rangeMin = range.getRangeMin()
            return True
        return False

    def trySplit(self, hashKeyLength: int) -> 'GeohashRange[]':
        result = []
        minHashKey = S2Manager().generateHashKey(self.rangeMin, hashKeyLength)
        maxHashKey = S2Manager().generateHashKey(self.rangeMax, hashKeyLength)
        denominator = 10 ** (len(str(self.rangeMin)) - len(str(minHashKey)))
        if minHashKey == maxHashKey:
            result.append(self)
        else:
            for l in range(minHashKey, maxHashKey + 1):
                if l > 0:
                    result.append(GeohashRange(self.rangeMin if l == minHashKey else l * denominator,
                                               self.rangeMax if l == maxHashKey else (
                                                   l + 1) * denominator - 1
                                               ))
                else:
                    result.append(GeohashRange(self.rangeMin if l == minHashKey else (l - 1) * denominator + 1,
                                               self.rangeMax if l == maxHashKey else l * denominator - 1
                                               ))
        return result
