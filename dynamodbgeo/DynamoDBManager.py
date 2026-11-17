import copy

from boto3.dynamodb.conditions import Attr, Key

from s2 import S2Manager


class DynamoDBManager:

    def __init__(self, config):
        self.config = config

    def queryGeohash(self, queryInput, hashKey: int, range: int):
        """
        Given a hash key and a min to max GeoHashrange it query the GSI to select the appropriate items to return
        """
        params = copy.deepcopy(queryInput)

        params['IndexName'] = self.config.geohashIndexName
        params.pop('ExclusiveStartKey', None)
        params['KeyConditionExpression'] = str(self.config.hashKeyAttributeName) + ' = :hashKey and ' + str(
            self.config.geohashAttributeName) + ' between :geohashMin and :geohashMax'

        if 'ExpressionAttributeValues' in params:
            params['ExpressionAttributeValues'] = dict(params['ExpressionAttributeValues'])
            params['ExpressionAttributeValues'].update(
                {':hashKey': hashKey, ':geohashMax': int(range.rangeMax), ':geohashMin': int(range.rangeMin)}
            )
        else:
            params['ExpressionAttributeValues'] = {':hashKey': hashKey, ':geohashMax': int(range.rangeMax), ':geohashMin': int(range.rangeMin)}

        response = self.config.table.query(**params)
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = self.config.table.query(**params)
            data.extend(response['Items'])
        return data
