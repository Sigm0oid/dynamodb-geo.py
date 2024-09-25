import uuid

import dynamodbgeo
from dynamodbgeo.util import GeoTableUtil
from truth.truth import AssertThat
from vars import dynamodbResource


def test_query_radius_noissuearoundEurope():
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

    # "lat": "32.8007718436974",
    # "lng": "10.107633337736274",
    # "radius": "5836769.2553483695",

    result = geoDataManager.queryRadius(
        dynamodbgeo.QueryRadiusRequest(
            dynamodbgeo.GeoPoint(32.8007718436974, 10.107633337736274),
            5836769.2553483695, {}))
    AssertThat(result).IsEmpty()


def test_query_radius():
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
            dynamodbgeo.GeoPoint(36.541567, 9.662921),
            "inside",
            PutItemInput))
        geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(36.495996, 9.672407),
            "outside",
            PutItemInput)
        )
        QueryRadiusInput = {
            "FilterExpression": "Country = :val1",
            "ExpressionAttributeValues": {
                ":val1": "Italy",
            }
        }
        result = geoDataManager.queryRadius(
            dynamodbgeo.QueryRadiusRequest(
                dynamodbgeo.GeoPoint(36.542840, 9.662671),
                200, QueryRadiusInput))
        if len(result) != 1 or result[0]["rangeKey"] != "inside":
            assert False
        assert True
    except:
        assert False
