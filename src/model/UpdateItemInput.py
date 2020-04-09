

class UpdateItemInput:

    def __init__(self, GeoPoint: 'GeoPoint', RangeKeyValue: str, ExtraFields):
        self.GeoPoint = GeoPoint
        self.RangeKeyValue = RangeKeyValue
        self.ExtraFields = ExtraFields

