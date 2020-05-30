import dynamodbgeo
from vars import dynamodb
import uuid


def test_query_radius_sort():
    try:
        table_name = str(uuid.uuid4())
        config = dynamodbgeo.GeoDataManagerConfiguration(
            dynamodb, table_name)
        geoDataManager = dynamodbgeo.GeoDataManager(config)
        table_util = dynamodbgeo.GeoTableUtil(config)
        create_table_input = table_util.getCreateTableRequest()
        # tweaking the base table parameters
        create_table_input["ProvisionedThroughput"]['ReadCapacityUnits'] = 5
        # pass the input to create_table method
        table_util.create_table(create_table_input)
        PutItemInput = {
            'Item': {
                'Country': {'S': "Italy"},
                'Capital': {'S': "Tunis"},
                'year': {'S': '2020'}
            },
            # ... Anything else to pass through to `putItem`, eg ConditionExpression
            'ConditionExpression': "attribute_not_exists(hashKey)"
        }
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.874419, 10.241062),
            "1",
            PutItemInput))
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.874507, 10.240857),
            "2",
            PutItemInput))
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.874617, 10.241441),
            "3",
            PutItemInput))
        QueryRadiusInput = {
            "FilterExpression": "Country = :val1",
            "ExpressionAttributeValues": {
                ":val1": {"S": "Italy"},
            }
        }
        result = geoDataManager.queryRadius(
            dynamodbgeo.QueryRadiusRequest(
                dynamodbgeo.GeoPoint(36.874444, 10.241059),
                95, QueryRadiusInput, sort=True))
        if len(result) != 3 or result[0]["rangeKey"]["S"] != "1" or result[1]["rangeKey"]["S"] != "2" or result[2]["rangeKey"]["S"] != "3":
            assert False
        assert True
    except:
        assert False
