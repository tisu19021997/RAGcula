
import s3fs
import boto3

from fsspec.asyn import AsyncFileSystem

AWS_ACCESS_KEY_ID = "AKIA4K2DFL33MSKWN6V2"
AWS_SECRET_ACCESS_KEY = "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"


def get_s3_fs() -> AsyncFileSystem:
    s3 = s3fs.S3FileSystem(
        key=AWS_ACCESS_KEY_ID,
        secret=AWS_SECRET_ACCESS_KEY,
    )
    return s3


def get_s3_boto_client():
    client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    return client
