class GeoPoint:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def getLatitude(self) -> float:
        return self.latitude

    def getLongitude(self) -> float:
        return self.longitude
