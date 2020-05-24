"""
Purpose: This class contains all the operation to perform on the DynamoDB table

"""
from s2 import S2Manager
from boto3.dynamodb.conditions import Key, Attr


class DynamoDBManager:

    def __init__(self, config):
        self.config = config

    # for now we're not taking params passed into queryInput in consideration
    def queryGeohash(self, queryInput, hashKey: int, range: int):
        """
        Given a hash key and a min to max GeoHashrange it query the GSI to select the appropriate items to return
        """
        params=queryInput

        params['TableName']=self.config.tableName
        params['IndexName']=self.config.geohashIndexName
        
        # As eyConditionExpressions must only contain one condition per key, customer passing KeyConditionExpression will be replaced automatically
        params['KeyConditionExpression']='hashKey = :hashKey and ' + str(self.config.geohashAttributeName) +' between :geohashMin and :geohashMax'

        if 'ExpressionAttributeValues' in queryInput.keys():
            params['ExpressionAttributeValues'].update(  
                {':hashKey': {'N': str(hashKey)}, ':geohashMax': {
                    'N': str(range.rangeMax)}, ':geohashMin': {'N': str(range.rangeMin)}}
            )
        else:
            params['ExpressionAttributeValues']={':hashKey': {'N': str(hashKey)}, ':geohashMax': {
                    'N': str(range.rangeMax)}, ':geohashMin': {'N': str(range.rangeMin)}}
            

        response = self.config.dynamoDBClient.query(**params)
        data = response['Items']

        while 'LastEvaluatedKey' in response: 
            params['ExclusiveStartKey']=response['LastEvaluatedKey']
            response = self.config.dynamoDBClient.query(**params)
            data.extend(response['Items'])
        return data

    def put_Point(self, putPointInput: 'PutPointInput'):
        """
        The dict in Item put_item call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(putPointInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params=putPointInput.ExtraFields.copy()   

        params['TableName']=self.config.tableName
        
        if('Item' not in putPointInput.ExtraFields.keys()):
            params['Item']={}

        params['Item'][self.config.hashKeyAttributeName] ={"N": str(hashKey)}
        params['Item'][self.config.rangeKeyAttributeName] ={"S": putPointInput.RangeKeyValue}
        params['Item'][self.config.geohashAttributeName] ={'N': str(geohash)}
        params['Item'][self.config.geoJsonAttributeName] ={"S": "{},{}".format(putPointInput.GeoPoint.latitude,putPointInput.GeoPoint.longitude)}
        
        try:
            response = self.config.dynamoDBClient.put_item(**params)
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
            response = self.config.dynamoDBClient.get_item(
                TableName=self.config.tableName,
                Key={
                    self.config.hashKeyAttributeName: {"N": str(hashKey)},
                    self.config.rangeKeyAttributeName: {
                        "S": getPointInput.RangeKeyValue}
                }
            )
        except Exception as e:
            print("The following error occured during the item retrieval :{}".format(e))
            response = "Error"
        return response
    
    def update_Point(self,UpdateItemInput : 'UpdateItemInput'):
        """
        The dict in Item Update call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(UpdateItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params=UpdateItemInput.ExtraFields.copy()   

        params['TableName']=self.config.tableName
        
        if('Key' not in UpdateItemInput.ExtraFields.keys()):
            params['Key']={}

        params['Key'][self.config.hashKeyAttributeName] ={"N": str(hashKey)}
        params['Key'][self.config.rangeKeyAttributeName] ={"S": UpdateItemInput.RangeKeyValue}
        
        #TODO Geohash and geoJson cannot be updated. For now no control over that need to be added        
        try:
            response = self.config.dynamoDBClient.update_item(**params)
        except Exception as e:
            print("The following error occured during the item update :{}".format(e))
            response = "Error"
        return response

    def delete_Point(self,DeleteItemInput : 'DeleteItemInput'):
        """
        The dict in Item Update call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(DeleteItemInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response = ""
        params=DeleteItemInput.ExtraFields.copy()   

        params['TableName']=self.config.tableName
        
        if('Key' not in DeleteItemInput.ExtraFields.keys()):
            params['Key']={}

        params['Key'][self.config.hashKeyAttributeName] ={"N": str(hashKey)}
        params['Key'][self.config.rangeKeyAttributeName] ={"S": DeleteItemInput.RangeKeyValue}
        try:
            response = self.config.dynamoDBClient.delete_item(**params)
        except Exception as e:
            print("The following error occured during the item delete :{}".format(e))
            response = "Error"
        return response

