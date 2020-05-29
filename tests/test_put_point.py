import dynamodbgeo
from vars import dynamodb
import uuid


def test_put_point():
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
        # define a dict of the item to input
        PutItemInput = {
            'Item': {
                'Country': {'S': "Italy"},
                'Capital': {'S': "Tunis"},
                'year': {'S': '2020'}
            },
            # ... Anything else to pass through to `putItem`, eg ConditionExpression
            'ConditionExpression': "attribute_not_exists(hashKey)"

        }
        response = geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            # latitude then latitude longitude
            dynamodbgeo.GeoPoint(36.879163, 10.243120),
            # Use this to ensure uniqueness of the hash/range pairs.
            str(uuid.uuid4()),
            PutItemInput
        ))
        assert response != "Error"
    except:
        assert False
