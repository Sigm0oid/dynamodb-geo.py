import boto3
import dynamodbgeo
import uuid  # used in range key uniquness
'''
Entry point script for testing
'''


if __name__ == "__main__":
    # initiat dynamodb service ressource,
    dynamodbResource = boto3.resource('dynamodb', region_name='us-east-2')
    config = dynamodbgeo.GeoDataManagerConfiguration(
        'geo_test_8', dynamodbResource)
    geoDataManager = dynamodbgeo.GeoDataManager(config)

    table_util = dynamodbgeo.GeoTableUtil(config)
    create_table_input = table_util.getCreateTableRequest()

    # tweaking the base table parameters
    create_table_input["ProvisionedThroughput"]['ReadCapacityUnits'] = 5

    # pass the input to create_table method
    table_util.create_table(create_table_input)

    # define a dict of the item to input
    PutItemInput = {
        'Item': {
            'Country': "Italy",
            'Capital': "Tunis",
            'year': '2020'
        },
        # ... Anything else to pass through to `putItem`, eg ConditionExpression
        'ConditionExpression': "attribute_not_exists(hashKey)"

    }
    print(" Testing the put ITem inside the rectengle ")
    geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        # latitude then latitude longitude
        dynamodbgeo.GeoPoint(36.879163, 10.243120),
        # Use this to ensure uniqueness of the hash/range pairs.
        str(uuid.uuid4()),
        PutItemInput
    ))

    print(" Testing the put ITem outside the rectengle ")
    geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.879502, 10.242143),
        str(uuid.uuid4()),
        PutItemInput))

    print(" Testing the Get ITem function")
    print(geoDataManager.get_Point(
        dynamodbgeo.GetPointInput(
            dynamodbgeo.GeoPoint(16, 16),
            "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6"
        )))

    print(" Testing the query rectangle function with QueryRectangleInput passed in parameters ")

    QueryRectangleInput = {
        "FilterExpression": "Country = :val1",
        "ExpressionAttributeValues": {
            ":val1": "Italy",
        }
    }
    # testing the query rectangle method
    print(geoDataManager.queryRectangle(
        dynamodbgeo.QueryRectangleRequest(
            dynamodbgeo.GeoPoint(36.878184, 10.242358),
            dynamodbgeo.GeoPoint(36.879317, 10.243648), QueryRectangleInput)))

    print(" Testing the put ITem inside circle radius")

    geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.874419, 10.241062),
        str(uuid.uuid4()),
        PutItemInput))

    geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.874507, 10.240857),
        str(uuid.uuid4()),
        PutItemInput))

    geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(36.874617, 10.241441),
        str(uuid.uuid4()),
        PutItemInput))

    print(" Testing query raduis with sorting and filtring")

    QueryRadiusInput = {
        "FilterExpression": "Country = :val1",
        "ExpressionAttributeValues": {
            ":val1": "Italy",
        }
    }

    print(geoDataManager.queryRadius(
        dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.874444, 10.241059),
            95, QueryRadiusInput, sort=True)))

    # define a dict of the item to input
    UpdateItemDict = {
        "UpdateExpression": "set Capital = :val1",
        "ConditionExpression": "Capital = :val2",
        "ExpressionAttributeValues": {
            ":val1": "Tunis",
            ":val2": "Ariana"
        },
        "ReturnValues": "ALL_NEW"
    }
    print(" Testing the Update Item")
    geoDataManager.update_Point(dynamodbgeo.UpdateItemInput(
        # latitude then latitude longitude
        dynamodbgeo.GeoPoint(36.879163, 10.24312),
        # Use this to ensure uniqueness of the hash/range pairs.
        "1e955491-d8ba-483d-b7ab-98370a8acf82",
        UpdateItemDict  # pass the dict that contain the remaining parameters here
    ))
    # Preparing dict of the item to delete
    DeleteItemDict = {
        "ConditionExpression": "attribute_exists(Country)",
        "ReturnValues": "ALL_OLD"
        # Don't put keys here, they will be generated for you implecitly
    }
    print(" Testing the Delete Item")
    geoDataManager.delete_Point(
        dynamodbgeo.DeleteItemInput(
            # latitude then latitude longitude
            dynamodbgeo.GeoPoint(36.879163, 10.24312),
            # Use this to ensure uniqueness of the hash/range pairs.
            "0df9742f-619b-49e5-b79e-9fb94279d30c",
            DeleteItemDict  # pass the dict that contain the remaining parameters here
        ))
