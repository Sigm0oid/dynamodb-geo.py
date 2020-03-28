
"""
Purpose: A wrapper on the top of DynamoDBManager for performing CRUD operation on our DynamoBD table
"""
import GeoDataManagerConfiguration
from DynamoDBManager import DynamoDBManager
from model import PutPointInput


class GeoDataManager:

    def __init__(self, config):
        self.config=config
        self.dynamoDBManager=DynamoDBManager(config)
    
    def put_Point(self,putPointInput):
        return self.dynamoDBManager.put_Point(putPointInput)
        
    
    def batch_write_points(lat,lng):
        pass
    
    def update_point(lat,lng):
        pass
    
    def delete_point(lat,lng):
        pass


