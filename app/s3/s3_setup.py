from .s3_manager import S3Manager
s3_manager = None
bucket_name=None

import os
from dotenv import load_dotenv

load_dotenv()

endpoint_url = os.getenv('ENDPOINT_URL')
region_name = os.getenv('REGION_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = os.getenv('BUCKET_NAME')

def init_s3_manager():
    global s3_manager, bucket_name
    s3_manager = S3Manager(endpoint_url, region_name, aws_access_key_id, aws_secret_access_key)



def get_s3_manager():
    global s3_manager
    if s3_manager is None:
        raise Exception("S3 Manager is not initialized")
    return s3_manager

def get_bucket_name():
    if bucket_name is None:
        raise Exception("Bucket name is not initialized")
    return bucket_name