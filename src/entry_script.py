from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from util.GeoTableUtil import GeoTableUtil
import boto3
from model.PutPointInput import PutPointInput
from model.GetPointInput import GetPointInput
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
    geoDataManager.put_Point(PutPointInput(GeoPoint(10, 10), str(
        uuid.uuid4()), "{country: { S: 'UK' },capital: { S: 'London' } }"))
    print(geoDataManager.get_Point(GetPointInput(
        GeoPoint(10, 10), "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6")))
