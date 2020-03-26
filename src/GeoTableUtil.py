'''
for async call / waiter following this approach :https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html

'''
class GeoTableUtil:

    def __init__(self,config):
         self.config=config
    
    def create_table(self):
        # skip if table already exists
        try:
            response = self.config.dynamoDBClient.describe_table(TableName=self.config.tableName)
            # table exists...bail
            print ("Table [{}] already exists. Skipping table creation.".format(self.config.tableName))
            return
        except:
            pass # no table... good
        print ("Creating table [{}]".format(self.config.tableName))

        table = self.config.dynamoDBClient.create_table(
            TableName=self.config.tableName,
            KeySchema= [
                {
                    'KeyType': "HASH",
                    'AttributeName': self.config.hashKeyAttributeName
                },
                {
                    'KeyType': "RANGE",
                    'AttributeName': self.config.rangeKeyAttributeName
                }
            ],
            AttributeDefinitions=[
                { 'AttributeName': self.config.hashKeyAttributeName, 'AttributeType': 'N' },
                { 'AttributeName': self.config.rangeKeyAttributeName, 'AttributeType': 'S' },
                { 'AttributeName': self.config.geohashAttributeName, 'AttributeType': 'N' }
          ],
          LocalSecondaryIndexes=[
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
           ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 5
        }
        )

        print ("Waiting for table [{}] to be created".format(self.config.tableName))
        table.meta.client.get_waiter('table_exists').wait(TableName=self.config.tableName)
        # if no exception, continue
        print ("Table created")





      