import boto3
from src import  * 
import uuid # used in range key uniquness
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
        uuid.uuid4()),PutItemInput))

    print(" Testing the Get ITem function")
    print(geoDataManager.get_Point(GetPointInput(
        GeoPoint(16, 16), "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6")))

    print(" Testing the query rectangle function")
    # testing the query rectangle method
    print(geoDataManager.queryRectangle(QueryRectangleRequest(GeoPoint(36.878184, 10.242358),GeoPoint(36.879317, 10.243648))))
    print(" query raduis")
    print(geoDataManager.queryRadius(QueryRadiusRequest(GeoPoint(36.879131, 10.243057),95)))
    
    #define a dict of the item to input
    UpdateItemDict= {
            "UpdateExpression": "set Capital = :val1",
            "ConditionExpression": "Capital = :val2",
            "ExpressionAttributeValues": {
                ":val1": {"S": "Tunis"},
                ":val2": {"S": "Ariana"}
            },
            "ReturnValues": "ALL_NEW"
    }
    print(" Testing the Update Item")
    geoDataManager.update_Point(UpdateItemInput(
        GeoPoint(36.879163,10.24312), # latitude then latitude longitude
         "1e955491-d8ba-483d-b7ab-98370a8acf82", # Use this to ensure uniqueness of the hash/range pairs.
         UpdateItemDict # pass the dict that contain the remaining parameters here
         ))
    # Preparing dict of the item to delete
    DeleteItemDict= {
            "ConditionExpression": "attribute_exists(Country)",
            "ReturnValues": "ALL_OLD" 
            # Don't put keys here, they will be generated for you implecitly
        }
    print(" Testing the Delete Item")
    geoDataManager.delete_Point(DeleteItemInput(
        GeoPoint(36.879163,10.24312), # latitude then latitude longitude
         "0df9742f-619b-49e5-b79e-9fb94279d30c", # Use this to ensure uniqueness of the hash/range pairs.
         DeleteItemDict # pass the dict that contain the remaining parameters here
         ))