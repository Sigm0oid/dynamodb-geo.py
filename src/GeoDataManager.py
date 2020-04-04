
"""
Purpose: A wrapper on the top of DynamoDBManager for performing CRUD operation on our DynamoBD table
"""
import GeoDataManagerConfiguration
from DynamoDBManager import DynamoDBManager
from model import PutPointInput
from model import GetPointInput
from model.Covering import Covering
from s2.S2Util import S2Util
from s2.S2Manager import S2Manager


class GeoDataManager:

    def __init__(self, config):
        self.config = config
        self.dynamoDBManager = DynamoDBManager(config)

    def put_Point(self, putPointInput):
        return self.dynamoDBManager.put_Point(putPointInput)

    def get_Point(self, getPointInput):
        return self.dynamoDBManager.get_Point(getPointInput)

    def batch_write_points(self):
        pass

    def update_point(self):
        pass

    def delete_point(self):
        pass

    def dispatchQueries(self, covering, geoQueryInput):
        """
        Generating multiple query from the covering area and running query on the DynamoDB table
        """
        ranges = covering.getGeoHashRanges(self.config.hashKeyLength)
        results = []
        for range in ranges:
            hashKey = S2Manager().generateHashKey(range.rangeMin, self.config.hashKeyLength)
            results.append(self.dynamoDBManager.queryGeohash(
                geoQueryInput.QueryInput, hashKey, range))
        return results

    def queryRectangle(self, QueryRectangleInput):
        latLngRect = S2Util().latLngRectFromQueryRectangleInput(
            QueryRectangleInput)
        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        results = self.dispatchQueries(covering, QueryRectangleInput)
        return results

    def queryRadius(self, QueryRadiusInput):
        latLngRect = S2Util().getBoundingLatLngRectFromQueryRadiusInput(
            QueryRadiusInput)
        covering = Covering(
            self.config.S2RegionCoverer().get_covering(latLngRect))
        results = self.dispatchQueries(covering, QueryRadiusInput)
        return results
