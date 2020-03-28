
from .GeoPoint import GeoPoint


class PutPointInput:
    def __init__(self,GeoPoint,RangeKeyValue,ExtraFields):
        self.GeoPoint=GeoPoint
        self.RangeKeyValue=RangeKeyValue
        self.ExtraFields=ExtraFields
