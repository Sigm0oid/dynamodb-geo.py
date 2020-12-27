
"""
Purpose: A signle point of entry for all the table and dynamodb resource configuration
"""
from s2sphere import RegionCoverer as S2RegionCoverer


class GeoDataManagerConfiguration:

    MERGE_THRESHOLD = 2  # still not clear

    geohashIndexName = "geohash-index"  # name of the LSI

    def __init__(self, tableName: str, dynamodbResource):
        self.tableName = tableName
        self.dynamodbResource = dynamodbResource
        self.table = dynamodbResource.Table(tableName)
        self.S2RegionCoverer = S2RegionCoverer  # this is form the s2 library
        self.hashKeyAttributeName = "hashKey"
        self.rangeKeyAttributeName = "rangeKey"
        self.geohashAttributeName = "geohash"
        self.geoJsonAttributeName = "geoJson"
        self.hashKeyLength = 2
        self.geoJsonPointType = "Point"  # for now only point is supported
