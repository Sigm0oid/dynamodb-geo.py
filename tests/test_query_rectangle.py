import uuid

import dynamodbgeo
from dynamodbgeo.util import GeoTableUtil

from vars import dynamodbResource


def test_query_rectangle():
    try:
        table_name = str(uuid.uuid4())
        config = dynamodbgeo.GeoDataManagerConfiguration(
            table_name, dynamodbResource)
        geoDataManager = dynamodbgeo.GeoDataManager(config)
        table_util = GeoTableUtil(config)
        create_table_input = table_util.getCreateTableRequest()
        # tweaking the base table parameters
        create_table_input["ProvisionedThroughput"]['ReadCapacityUnits'] = 5
        # pass the input to create_table method
        table_util.create_table(create_table_input)
        PutItemInput = {
            'Item': {
                'Country': "Italy",
                'Capital': "Tunis",
                'year': '2020'
            },
            # ... Anything else to pass through to `putItem`, eg ConditionExpression
            'ConditionExpression': "attribute_not_exists(hashKey)"
        }
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.879163, 10.243120),
            "inside",
            PutItemInput
        ))
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.879502, 10.242143),
            "outside",
            PutItemInput))
        QueryRectangleInput = {
            "FilterExpression": "Country = :val1",
            "ExpressionAttributeValues": {
                ":val1": "Italy",
            }
        }
        result = geoDataManager.queryRectangle(
            dynamodbgeo.QueryRectangleRequest(
                dynamodbgeo.GeoPoint(36.878184, 10.242358),
                dynamodbgeo.GeoPoint(36.879317, 10.243648), QueryRectangleInput))
        if len(result) != 1 or result[0]["rangeKey"] != "inside":
            assert False
        assert True
    except:
        assert False
