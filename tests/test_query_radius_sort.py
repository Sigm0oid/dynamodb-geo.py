import uuid

import dynamodbgeo
from dynamodbgeo.util import GeoTableUtil
from truth.truth import AssertThat

from vars import dynamodbResource


def test_query_radius_sort():
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
            ":val1": "Italy",
        }
    }
    result = geoDataManager.queryRadius(
        dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(36.874444, 10.241059),
            95, QueryRadiusInput, sort=True))
    AssertThat(len(result)).IsEqualTo(3)
    AssertThat(result[0]['rangeKey']).IsEqualTo("1")
    AssertThat(result[1]['rangeKey']).IsEqualTo("2")
    AssertThat(result[2]['rangeKey']).IsEqualTo("3")
