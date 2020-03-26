from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from GeoTableUtil import GeoTableUtil
import boto3



'''
Entry point script for testing
'''


if __name__=="__main__": 
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')# initiat dynamodb service ressource
    config=GeoDataManagerConfiguration(dynamodb,'geo_test_1')
    geoDataManager=GeoDataManager(config)
    table_util=GeoTableUtil(config)
    table_util.create_table()

