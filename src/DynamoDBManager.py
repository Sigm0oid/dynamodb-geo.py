"""
Purpose: This class contains all the operation to perform on the DynamoDB table

"""
from s2.S2Manager import S2Manager
from model.PutPointInput import PutPointInput
from boto3.dynamodb.conditions import Key, Attr



class DynamoDBManager:
    

    def __init__(self, config):
        self.config = config
    

    def queryGeohash(self,queryInput, hashKey ,range): # for now we're not taking params passed into queryInput in consideration
        """
        Given a hash key and a min to max GeoHashrange it query the GSI to select the appropriate items to return
        """
        response = self.config.dynamoDBClient.query(
            TableName=self.config.tableName,
            IndexName= self.config.geohashIndexName,
            KeyConditionExpression = 'hashKey = :hashKey and '+str(self.config.geohashAttributeName)+' between :geohashMin and :geohashMax',
            ExpressionAttributeValues = {':hashKey': {'N': str(hashKey)},':geohashMax':{'N': str(range.rangeMax)},':geohashMin':{'N': str(range.rangeMin)}}
                        )
        data = response['Items']

        while 'LastEvaluatedKey' in response:
            response = self.config.dynamoDBClient.query(
                TableName=self.config.tableName,
                IndexName= self.config.geohashIndexName,
            KeyConditionExpression = 'hashKey = :hashKey and '+str(self.config.geohashAttributeName)+' between :geohashMin and :geohashMax',
            ExpressionAttributeValues = {':hashKey': {'N': str(hashKey)},':geohashMax':{'N': str(range.rangeMax)},':geohashMin':{'N': str(range.rangeMin)}}
            )
            data.extend(response['Items'])
        return data


      



    def put_Point(self, putPointInput):
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

    def get_Point(self, getPointInput):
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
