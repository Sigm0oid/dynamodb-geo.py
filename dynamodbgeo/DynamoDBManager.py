"""
Purpose: This class contains all the operation to perform on the DynamoDB table

"""
from boto3.dynamodb.conditions import Attr, Key

from s2 import S2Manager


class DynamoDBManager:

    def __init__(self, config):
        self.config = config

    # for now we're not taking params passed into queryInput in consideration
    def queryGeohash(self, queryInput, hashKey: int, range: int):
        """
        Given a hash key and a min to max GeoHashrange it query the GSI to select the appropriate items to return
        """
        params = queryInput

        params['IndexName'] = self.config.geohashIndexName

        # As eyConditionExpressions must only contain one condition per key, customer passing KeyConditionExpression will be replaced automatically
        params['KeyConditionExpression'] = str(self.config.hashKeyAttributeName) + ' = :hashKey and ' + str(
            self.config.geohashAttributeName) + ' between :geohashMin and :geohashMax'

        if 'ExpressionAttributeValues' in queryInput.keys():
            params['ExpressionAttributeValues'].update(
                {':hashKey': hashKey, ':geohashMax':
                    range.rangeMax, ':geohashMin': range.rangeMin}
            )
        else:
            params['ExpressionAttributeValues'] = {':hashKey': hashKey, ':geohashMax':
                                                   range.rangeMax, ':geohashMin': range.rangeMin}

        response = self.config.table.query(**params)
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = self.config.table.query(**params)
            data.extend(response['Items'])
        return data

    def put_Point(self, putPointInput: 'PutPointInput'):
        """
        The dict in Item put_item call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(putPointInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = putPointInput.ExtraFields.copy()

        if('Item' not in putPointInput.ExtraFields.keys()):
            params['Item'] = {}

        params['Item'][self.config.hashKeyAttributeName] = hashKey
        params['Item'][self.config.rangeKeyAttributeName] = putPointInput.RangeKeyValue
        params['Item'][self.config.geohashAttributeName] = geohash
        params['Item'][self.config.geoJsonAttributeName] = "{},{}".format(
            putPointInput.GeoPoint.latitude, putPointInput.GeoPoint.longitude)
        try:
            response = self.config.table.put_item(Item=params['Item'])
        except Exception as e:
            print("The following error occured during the item insertion :{}".format(e))
            response = "Error"
        return response

    def get_Point(self, getPointInput: 'GetPointInput'):
        """
        The dict in Key get_item call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(getPointInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        try:
            response = self.config.table.get_item(
                Key={
                    self.config.hashKeyAttributeName: hashKey,
                    self.config.rangeKeyAttributeName: getPointInput.RangeKeyValue
                }
            )
        except Exception as e:
            print("The following error occured during the item retrieval :{}".format(e))
            response = "Error"
        return response

    def update_Point(self, UpdateItemInput: 'UpdateItemInput'):
        """
        The dict in Item Update call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(UpdateItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = UpdateItemInput.ExtraFields.copy()

        if('Key' not in UpdateItemInput.ExtraFields.keys()):
            params['Key'] = {}

        params['Key'][self.config.hashKeyAttributeName] = hashKey
        params['Key'][self.config.rangeKeyAttributeName] = UpdateItemInput.RangeKeyValue

        # TODO Geohash and geoJson cannot be updated. For now no control over that need to be added
        try:
            response = self.config.table.update_item(**params)
        except Exception as e:
            print("The following error occured during the item update :{}".format(e))
            response = "Error"
        return response

    def delete_Point(self, DeleteItemInput: 'DeleteItemInput'):
        """
        The dict in Item Update call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(DeleteItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = DeleteItemInput.ExtraFields.copy()

        if('Key' not in DeleteItemInput.ExtraFields.keys()):
            params['Key'] = {}

        params['Key'][self.config.hashKeyAttributeName] = hashKey
        params['Key'][self.config.rangeKeyAttributeName] = DeleteItemInput.RangeKeyValue
        try:
            response = self.config.table.delete_item(**params)
        except Exception as e:
            print("The following error occured during the item delete :{}".format(e))
            response = "Error"
        return response
