import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from GeohashRange import GeohashRange
from s2sphere import CellId as S2CellId


class Covering:
    def __init__(self, cellIds: 'S2CellId'):
        self.cellIds = cellIds

    def getGeoHashRanges(self, hashKeyLength: int) -> 'GeohashRange[]':
        ranges = []
        for outerRange in self.cellIds:
            hashRange = GeohashRange(
                outerRange.range_min().id(), outerRange.range_max().id())
            current_ranges = hashRange.trySplit(hashKeyLength)
            for current_range in current_ranges:
                ranges.append(current_range)
        return ranges

    def getNumberOfCells(self):
        return len(self.cellIds)
