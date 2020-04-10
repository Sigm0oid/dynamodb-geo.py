from s2sphere import LatLng as S2LatLng
from s2sphere import Cell as S2Cell


class S2Manager:
    def generateGeohash(self, geoPoint: 'GeoPoint'):
        latLng = S2LatLng.from_degrees(
            geoPoint.getLatitude(), geoPoint.getLongitude())
        cell = S2Cell.from_lat_lng(latLng)
        cellId = cell.id()
        return cellId.id()

    def generateHashKey(self, geohash: int, hashKeyLength: int):
        if geohash < 0:
            hashKeyLength += 1
        geohashString = str(geohash)
        denominator = 10 ** (len(geohashString) - hashKeyLength)
        return int(geohash / denominator)
