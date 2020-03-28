from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from util.GeoTableUtil import GeoTableUtil
import boto3



'''
Entry point script for testing
'''


if __name__=="__main__": 
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')# initiat dynamodb service ressource,
    config=GeoDataManagerConfiguration(dynamodb,'geo_test_6')
    geoDataManager=GeoDataManager(config)
    table_util=GeoTableUtil(config)
    table_util.create_table()

