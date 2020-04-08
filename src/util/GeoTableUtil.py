#!/usr/bin/env python

"""
Purpose: Create the DynamoDB table for geo data based on the GeoDataManagerConfiguration. 

NOTE: for now the capacity is set to 10 RCU and 5 WCU to avoid high cost of batch writing.

TODO: Make the table configuration parametric.

01-create-table.py - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.client.run-application-python.01-create-table.html


Author: Hamza Rhibi
"""

class GeoTableUtil:

    def __init__(self,config):
        self.config=config
    
    def getCreateTableRequest(self):
        """
        Prepare dict with default parameter to create the base
        """
        params = {
            'TableName' : self.config.tableName,
            'KeySchema': [       
                { 'AttributeName': self.config.hashKeyAttributeName, 'KeyType': "HASH"},    # Partition key
                { 'AttributeName': self.config.rangeKeyAttributeName, 'KeyType': "RANGE" }   # Sort key
            ],
            'AttributeDefinitions':[
                { 'AttributeName': self.config.hashKeyAttributeName, 'AttributeType': 'N' },
                { 'AttributeName': self.config.rangeKeyAttributeName, 'AttributeType': 'S' },
                { 'AttributeName': self.config.geohashAttributeName, 'AttributeType': 'N' }

            ],
            'LocalSecondaryIndexes':[
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


    def create_table(self,CreateTableInput :"Dict with parameters to create the table"):
        # skip if table already exists
        try:
            response = self.config.dynamoDBClient.describe_table(TableName=self.config.tableName)
            # table exists...bail
            print ("Table [{}] already exists. Skipping table creation.".format(self.config.tableName))
            return
        except:
            pass # no table... good
        print ("Creating table [{}]".format(self.config.tableName))

        table = self.config.dynamoDBClient.create_table(**CreateTableInput)

        print ("Waiting for table [{}] to be created".format(self.config.tableName))
        self.config.dynamoDBClient.get_waiter('table_exists').wait(TableName=self.config.tableName)
        # if no exception, continue
        print ("Table created")
        return

      