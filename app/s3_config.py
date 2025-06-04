import boto3
from botocore.client import Config

from app.config import settings

bucket_name = "ggv-api-bucket"

# local_file_path = "images/upload_test.txt"
# object_name = "my-directory/uploaded_file.txt"

# Initialize the S3 client for MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    config=Config(signature_version="s3v4"),  # Use S3v4 signature
)
