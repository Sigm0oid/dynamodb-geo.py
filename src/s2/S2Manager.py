from s2sphere import LatLng as S2LatLng
from s2sphere import Cell as S2Cell
from model import GeoPoint

class S2Manager:
    def generateGeohash(self, geoPoint):
        latLng = S2LatLng.from_degrees(geoPoint.getLatitude(), geoPoint.getLongitude())
        cell = S2Cell.from_lat_lng(latLng)
        cellId = cell.id()
        return cellId.id()
    def generateHashKey(self, geohash, hashKeyLength):
        if geohash < 0:
            hashKeyLength += 1
        geohashString = str(geohash)
        denominator = 10 ** (len(geohashString) - hashKeyLength)
        return int(geohash / denominator)