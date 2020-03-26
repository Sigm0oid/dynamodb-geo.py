import GeoDataManagerConfiguration
from DynamoDBManager import DynamoDBManager

class GeoDataManager:

    def __init__(self, config):
        self.config=config
        self.dynamoDBManager=DynamoDBManager()

    def create_table(table_name):
        pass
    
    def put_Point(lat,lng):
        pass
    
    def batch_write_points(putPointInputs):
        pass
    
    def update_point(lat,lng):
        pass
    
    def delete_point(lat,lng):
        pass


