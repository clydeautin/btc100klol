""" 
S3 Singleton Factory

Keeps overhead low by keeping at most one S3 client alive, refreshing
the client if credentials are invalid or expire.

Get client when needed; don't hold onto it too long or we won't be able 
to guarantee a valid connection.
 """

import boto3  # type: ignore
from botocore.exceptions import (  # type: ignore
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
)

from const import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
)

_s3_client = None


def _create_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def is_s3_session_valid():
    global _s3_client
    try:
        _s3_client.list_buckets()
        return True
    except (NoCredentialsError, PartialCredentialsError):
        print("Invalid or missing credentials.")
        return False
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["ExpiredToken", "InvalidToken"]:
            print("Session credentials are expired or invalid.")
            return False
        print(f"An unexpected error occurred: {e}")
        return False


def get_s3_client():
    global _s3_client

    if _s3_client is None or not is_s3_session_valid():
        _s3_client = _create_s3_client()

    return _s3_client
