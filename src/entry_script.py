from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from util.GeoTableUtil import GeoTableUtil
import boto3
from model.PutPointInput import PutPointInput
from model.GetPointInput import GetPointInput
from model.QueryRectangleRequest import QueryRectangleRequest
from model.GeoPoint import GeoPoint
import uuid


'''
Entry point script for testing
'''


if __name__ == "__main__":
    # initiat dynamodb service ressource,
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')
    config = GeoDataManagerConfiguration(dynamodb, 'geo_test_7')
    geoDataManager = GeoDataManager(config)
    table_util = GeoTableUtil(config)
    table_util.create_table()

    print(" Testing the put item function")
    item_dictionary={'Country':'Tunisia','Surface':210} # dictionary that contains the non key attributes

    print(" Testing the put ITem function")
    geoDataManager.put_Point(PutPointInput(GeoPoint(15, 15), str(
        uuid.uuid4()), item_dictionary))
    print(" Testing the Get ITem function")
    print(geoDataManager.get_Point(GetPointInput(
        GeoPoint(15, 15), "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6")))

    print(" Testing the query rectangle function")
    # testing the query rectangle method
    print(geoDataManager.queryRectangle(QueryRectangleRequest(GeoPoint(15, 15),GeoPoint(15, 15))))
    
