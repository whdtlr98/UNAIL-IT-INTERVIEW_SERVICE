import boto3
from botocore.exceptions import NoCredentialsError

# S3 클라이언트 초기화
s3 = boto3.client('s3', region_name='ap-northeast-2')

def upload_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        s3_path = f"s3://{bucket_name}/{object_name}"
        return s3_path
    except NoCredentialsError:
        raise Exception("S3 Credentials not available")

