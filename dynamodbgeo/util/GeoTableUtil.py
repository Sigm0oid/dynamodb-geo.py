#!/usr/bin/env python

"""
Purpose: Create and manage the DynamoDB table for geo data based on the GeoDataManagerConfiguration.

NOTE: Default capacity is set to 10 RCU and 10 WCU; customize the dict returned by getCreateTableRequest() before calling create_table().

01-create-table.py - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.client.run-application-python.01-create-table.html


Author(s): Hamza Rhibi, Brandon Sneider
"""


class GeoTableUtil:

    def __init__(self, config):
        self.config = config

    def getCreateTableRequest(self):
        """
        Prepare dict with default parameter to create the base
        """
        params = {
            'TableName': self.config.tableName,
            'KeySchema': [
                {'AttributeName': self.config.hashKeyAttributeName,
                    'KeyType': "HASH"},    # Partition key
                {'AttributeName': self.config.rangeKeyAttributeName,
                    'KeyType': "RANGE"}   # Sort key
            ],
            'AttributeDefinitions': [
                {'AttributeName': self.config.hashKeyAttributeName,
                    'AttributeType': 'N'},
                {'AttributeName': self.config.rangeKeyAttributeName,
                    'AttributeType': 'S'},
                {'AttributeName': self.config.geohashAttributeName, 'AttributeType': 'N'}

            ],
            'LocalSecondaryIndexes': [
                {
                    'IndexName': self.config.geohashIndexName,
                    'KeySchema': [
                        {
                            'KeyType': 'HASH',
                            'AttributeName': self.config.hashKeyAttributeName
                        },
                        {
                            'KeyType': 'RANGE',
                            'AttributeName': self.config.geohashAttributeName
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        }
        return params

    def create_table(self, CreateTableInput: "Dict with parameters to create the table" = None):
        if CreateTableInput is None:
            CreateTableInput = self.getCreateTableRequest()
        table_name = CreateTableInput.get('TableName', self.config.tableName)

        # skip if table already exists
        try:
            self.config.dynamodbResource.meta.client.describe_table(
                TableName=table_name)
            print("Table [{}] already exists. Skipping table creation.".format(
                table_name))
            return
        except Exception as exc:
            error_code = getattr(exc, 'response', {}).get('Error', {}).get('Code')
            if error_code != 'ResourceNotFoundException':
                raise

        print("Creating table [{}]".format(table_name))

        table = self.config.dynamodbResource.create_table(**CreateTableInput)

        print("Waiting for table [{}] to be created".format(table_name))
        table.wait_until_exists()
        print("Table created")
        return table

    def delete_table(self, table_name: str = None):
        target_name = table_name or self.config.tableName
        table = (
            self.config.table
            if target_name == self.config.tableName
            else self.config.dynamodbResource.Table(target_name)
        )
        try:
            self.config.dynamodbResource.meta.client.describe_table(
                TableName=target_name)
        except Exception as exc:
            error_code = getattr(exc, 'response', {}).get('Error', {}).get('Code')
            if error_code == 'ResourceNotFoundException':
                print("Table [{}] does not exist. Skipping table deletion.".format(
                    target_name))
                return
            raise

        print("Deleting table [{}]".format(target_name))
        table.delete()
        print("Waiting for table [{}] to be deleted".format(target_name))
        table.wait_until_not_exists()
        print("Table deleted")
