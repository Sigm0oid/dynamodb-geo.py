from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from util.GeoTableUtil import GeoTableUtil
import boto3
from model.PutPointInput import PutPointInput
from model.GeoPoint import GeoPoint
import uuid



'''
Entry point script for testing
'''


if __name__=="__main__": 
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')# initiat dynamodb service ressource,
    config=GeoDataManagerConfiguration(dynamodb,'geo_test_1')
    geoDataManager=GeoDataManager(config)
    table_util=GeoTableUtil(config)
    table_util.create_table()
    geoDataManager.put_Point(PutPointInput(GeoPoint(10,10),str(uuid.uuid4()),"{country: { S: 'UK' },capital: { S: 'London' } }"))
    

