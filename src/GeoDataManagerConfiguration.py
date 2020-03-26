class GeoDataManagerConfiguration:

    MERGE_THRESHOLD = 2 # still not clear
    
    

    geohashIndexName = "geohash-index" # name of the LSI

    



    def __init__(self,dynamoDBClient, tableName):
        self.dynamoDBClient = dynamoDBClient # dynamodb client taken from aws sdk
        self.tableName = tableName
        #self.S2RegionCoverer = S2RegionCoverer # this is form the s2 library
        self.hashKeyAttributeName = "hashKey"
        self.rangeKeyAttributeName = "rangeKey"
        self.geohashAttributeName = "geohash"
        self.geoJsonAttributeName = "geoJson"
        self.hashKeyLength = 2
