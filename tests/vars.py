import boto3
from botocore.config import Config

dynamodb = boto3.client('dynamodb', endpoint_url="http://localhost:8000",
                        config=Config(connect_timeout=1, read_timeout=1, retries={'max_attempts': 1}))
