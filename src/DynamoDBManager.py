"""
Purpose: This class contains all the operation to perform on the DynamoDB table

"""
from s2.S2Manager import S2Manager
from model.PutPointInput import PutPointInput
class DynamoDBManager:
        
    def __init__(self,config):
        self.config=config
    
    def put_Point(self,putPointInput):
        """
        The dict in Item put_item call, should contains a dict with string as a key and a string as a value: {"N": "123"}
        """
        geohash = S2Manager().generateGeohash(putPointInput.GeoPoint)
        hashKey = S2Manager().generateHashKey(geohash, self.config.hashKeyLength)
        response=""
        try:
            response=self.config.dynamoDBClient.put_item(
                TableName=self.config.tableName, 
                Item={
                    self.config.hashKeyAttributeName:{"N":str(hashKey)},
                    self.config.rangeKeyAttributeName:{"S":putPointInput.RangeKeyValue},
                    self.config.geohashAttributeName:{'N':str(geohash)},
                    self.config.geoJsonAttributeName:{"S":str(putPointInput.ExtraFields)}
                }
            )
        except Exception as e:
            print("The following error occured during the item insertion :{}".format(e))
            response= "Error"
        return response