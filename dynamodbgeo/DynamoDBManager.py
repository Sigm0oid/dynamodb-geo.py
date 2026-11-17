"""
Purpose: This class contains all the operation to perform on the DynamoDB table

"""
import copy

from boto3.dynamodb.conditions import Attr, Key

from s2 import S2Manager


class DynamoDBManager:

    def __init__(self, config):
        self.config = config

    def _buildQueryParams(self, queryInput, hashKey: int, range: int, exclusiveStartKey=None):
        params = copy.deepcopy(queryInput) if queryInput else {}
        params['IndexName'] = self.config.geohashIndexName

        if exclusiveStartKey is not None:
            params['ExclusiveStartKey'] = copy.deepcopy(exclusiveStartKey)
        else:
            params.pop('ExclusiveStartKey', None)

        # KeyConditionExpressions must only contain one condition per key; any caller KeyConditionExpression is replaced automatically
        params['KeyConditionExpression'] = (
            str(self.config.hashKeyAttributeName) + ' = :hashKey and ' +
            str(self.config.geohashAttributeName) + ' between :geohashMin and :geohashMax'
        )

        expr_values = dict(params.get('ExpressionAttributeValues') or {})
        expr_values.update({
            ':hashKey': hashKey,
            ':geohashMax': int(range.rangeMax),
            ':geohashMin': int(range.rangeMin),
        })
        params['ExpressionAttributeValues'] = expr_values
        return params

    def queryGeohashPage(self, queryInput, hashKey: int, range: int, exclusiveStartKey=None):
        """
        Query a single DynamoDB page for a geohash range, returning (items, last_evaluated_key).
        """
        params = self._buildQueryParams(
            queryInput, hashKey, range, exclusiveStartKey=exclusiveStartKey
        )
        response = self.config.table.query(**params)
        return list(response.get('Items', [])), response.get('LastEvaluatedKey')

    def queryGeohash(self, queryInput, hashKey: int, range: int):
        """
        Given a hash key and a min to max GeoHashrange it query the GSI to select the appropriate items to return
        """
        data, last_evaluated_key = self.queryGeohashPage(queryInput, hashKey, range)

        while last_evaluated_key is not None:
            items, last_evaluated_key = self.queryGeohashPage(
                queryInput, hashKey, range, exclusiveStartKey=last_evaluated_key
            )
            data.extend(items)
        return data

    def put_Point(self, putPointInput: 'PutPointInput'):
        """
        Put a point item into the DynamoDB table, forwarding any additional put_item parameters (e.g. ConditionExpression).
        """
        geohash = S2Manager().generateGeohash(putPointInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = copy.deepcopy(putPointInput.ExtraFields) if putPointInput.ExtraFields else {}

        if 'Item' not in params:
            params['Item'] = {}

        params['Item'][self.config.hashKeyAttributeName] = hashKey
        params['Item'][self.config.rangeKeyAttributeName] = putPointInput.RangeKeyValue
        params['Item'][self.config.geohashAttributeName] = geohash
        params['Item'][self.config.geoJsonAttributeName] = "{},{}".format(
            putPointInput.GeoPoint.latitude, putPointInput.GeoPoint.longitude)
        try:
            response = self.config.table.put_item(**params)
        except Exception as e:
            print("The following error occured during the item insertion :{}".format(e))
            response = "Error"
        return response

    def get_Point(self, getPointInput: 'GetPointInput'):
        """
        Retrieve a point item by GeoPoint and RangeKeyValue.
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
        Update an existing point item in the DynamoDB table.
        """
        geohash = S2Manager().generateGeohash(UpdateItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = copy.deepcopy(UpdateItemInput.ExtraFields) if UpdateItemInput.ExtraFields else {}

        if 'Key' not in params:
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
        Delete a point item from the DynamoDB table.
        """
        geohash = S2Manager().generateGeohash(DeleteItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params = copy.deepcopy(DeleteItemInput.ExtraFields) if DeleteItemInput.ExtraFields else {}

        if 'Key' not in params:
            params['Key'] = {}

        params['Key'][self.config.hashKeyAttributeName] = hashKey
        params['Key'][self.config.rangeKeyAttributeName] = DeleteItemInput.RangeKeyValue
        try:
            response = self.config.table.delete_item(**params)
        except Exception as e:
            print("The following error occured during the item delete :{}".format(e))
            response = "Error"
        return response
