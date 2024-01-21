
import s3fs
import boto3
import os

from dotenv import load_dotenv, find_dotenv
from fsspec.asyn import AsyncFileSystem

load_dotenv(find_dotenv())

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]


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
