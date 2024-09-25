import boto3
from botocore.config import Config

dynamodbResource = boto3.resource('dynamodb', endpoint_url="http://localhost:8000",
                                  region_name='local',
                                  config=Config(connect_timeout=1, read_timeout=1, retries={'max_attempts': 1}))
