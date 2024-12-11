""" 
S3 Singleton Factory

Keeps overhead low by keeping at most one S3 client alive, refreshing
the client if credentials are invalid or expire.

Get client when needed; don't hold onto it too long or we won't be able 
to guarantee a valid connection.
"""

import io
import requests  # type: ignore

import boto3  # type: ignore
from botocore.config import Config  # type: ignore
from botocore.exceptions import (  # type: ignore
    NoCredentialsError,
    PartialCredentialsError,
    ClientError,
)

from const import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_BUCKET,
    AWS_SECRET_ACCESS_KEY,
)


class S3ClientFactory:
    _s3_client = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(S3ClientFactory, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def _create_s3_client(self) -> boto3:
        config = Config(connect_timeout=10, read_timeout=30)
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
            config=config,
        )

    def is_s3_session_valid(self) -> bool:
        try:
            if self._s3_client is None:
                return False
            self._s3_client.list_buckets()
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

    def save_image_to_s3(self, image_url: str, unique_file_name: str) -> str:
        response = requests.get(image_url)
        if response.status_code == 200:
            s3 = self.get_s3_client()
            image_data = response.content
            s3.upload_fileobj(
                io.BytesIO(image_data),
                AWS_S3_BUCKET,
                unique_file_name,
                ExtraArgs={"ContentType": "image/png"},
            )

            s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_file_name}"

            return s3_url
        else:
            raise Exception(
                f"Failed to retrieve image. Status code: {response.status_code}"
            )

    def fetch_presigned_url(
        self,
        unique_file_name: str,
        expiration: int = 3600,
    ) -> str:
        s3 = self.get_s3_client()
        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": AWS_S3_BUCKET, "Key": unique_file_name},
                ExpiresIn=expiration,
            )

            return url
        except Exception as e:
            print(f"Error generating pre-signed URL: {e}")
            raise

    def get_s3_client(self) -> boto3:
        if self._s3_client is None or not self.is_s3_session_valid():
            self._s3_client = self._create_s3_client()

        return self._s3_client
