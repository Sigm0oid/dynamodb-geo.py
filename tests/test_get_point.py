import dynamodbgeo
from vars import dynamodb
import uuid


def test_get_point():
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
        range_key = "b385bbf9-581b-4df4-b5ad-4c0e3a0794b6"
        cords = (36.879163, 10.243120)
        response = geoDataManager.put_Point(dynamodbgeo.PutPointInput(
            dynamodbgeo.GeoPoint(cords[0], cords[1]),
            range_key,
            PutItemInput
        ))
        response = geoDataManager.get_Point(
            dynamodbgeo.GetPointInput(
                dynamodbgeo.GeoPoint(cords[0], cords[1]),
                range_key
            ))
        assert response != "Error"
    except:
        assert False
