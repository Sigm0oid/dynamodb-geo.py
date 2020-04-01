from GeohashRange import GeohashRange
from s2sphere import CellId as S2CellId


class Covering:
    def __init__(self, cellIds):
        self.cellIds = cellIds

    def getGeoHashRanges(self, hashKeyLength):
        ranges = []
        for outerRange in self.cellIds:
            hashRange = GeohashRange(
                outerRange.range_min().id, outerRange.range_max().id)
            current_ranges = hashRange.trySplit(hashKeyLength)
            for current_range in current_ranges:
                ranges.append(current_range)
        return ranges

    def getNumberOfCells(self):
        return len(self.cellIds)
