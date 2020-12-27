import uuid

import boto3
import dynamodbgeo
from dynamodbgeo.util import GeoTableUtil
from truth.truth import AssertThat

from vars import dynamodbResource


def test_create_table():
    table_name = str(uuid.uuid4())
    config = dynamodbgeo.GeoDataManagerConfiguration(
        table_name, dynamodbResource)
    table_util = GeoTableUtil(config)
    create_table_input = table_util.getCreateTableRequest()
    # tweaking the base table parameters
    create_table_input["ProvisionedThroughput"]['ReadCapacityUnits'] = 5
    # pass the input to create_table method
    table_util.create_table(create_table_input)
    dynamodb = boto3.client('dynamodb', endpoint_url="http://localhost:8000",
                            region_name='local')

    response = dynamodb.list_tables()
    AssertThat(response['TableNames']).Contains(table_name)
