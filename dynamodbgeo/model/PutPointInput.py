class PutPointInput:
    def __init__(self, GeoPoint: 'GeoPoint', RangeKeyValue: str, ExtraFields: dict = None):
        self.GeoPoint = GeoPoint
        self.RangeKeyValue = RangeKeyValue
        self.ExtraFields = ExtraFields if ExtraFields is not None else {}
