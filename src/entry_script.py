from GeoDataManagerConfiguration import GeoDataManagerConfiguration
from GeoDataManager import GeoDataManager
from util.GeoTableUtil import GeoTableUtil
import boto3
from model.PutPointInput import PutPointInput
from model.GetPointInput import GetPointInput
from model.QueryRectangleRequest import QueryRectangleRequest
from model.GeoPoint import GeoPoint
from model.QueryRadiusRequest import QueryRadiusRequest
import uuid


'''
Entry point script for testing
'''


if __name__ == "__main__":
    # initiat dynamodb service ressource,
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')
    config = GeoDataManagerConfiguration(dynamodb, 'geo_test_8')
    geoDataManager = GeoDataManager(config)
    
    table_util = GeoTableUtil(config)
    create_table_input=table_util.getCreateTableRequest()

    #tweaking the base table parameters 
    create_table_input["ProvisionedThroughput"]['ReadCapacityUnits']=5
    
    #pass the input to create_table method
    table_util.create_table(create_table_input)

    print(" Testing the put item function")
        
    #define a dict of the item to input
    PutItemInput = {
            'Item': {
                'Country': {'S': "Tunisia"},
                'Capital': {'S': "Tunis"},
                'year': {'S': '2020'}
            },
            'ConditionExpression': "attribute_not_exists(hashKey)" # ... Anything else to pass through to `putItem`, eg ConditionExpression
                
    }
    print(" Testing the put ITem inside the rectengle ")
    geoDataManager.put_Point(PutPointInput(
        GeoPoint(36.879163, 10.243120), # latitude then latitude longitude
         str( uuid.uuid4()), # Use this to ensure uniqueness of the hash/range pairs.
         PutItemInput
         ))
    print(" Testing the put ITem outside the rectengle ")
    geoDataManager.put_Point(PutPointInput(GeoPoint(36.879502, 10.242143), str(
        uuid.uuid4()), {}))

    print(" Testing the Get ITem function")
    print(geoDataManager.get_Point(GetPointInput(
        GeoPoint(16, 16), "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6")))

    print(" Testing the query rectangle function")
    # testing the query rectangle method
    print(geoDataManager.queryRectangle(QueryRectangleRequest(GeoPoint(36.878184, 10.242358),GeoPoint(36.879317, 10.243648))))
    print(" query raduis")
    print(geoDataManager.queryRadius(QueryRadiusRequest(GeoPoint(36.879131, 10.243057),95))) 