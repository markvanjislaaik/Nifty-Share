import threading
import sys
import os
import datetime
import boto3
from boto3.s3.transfer import TransferConfig
import logging
from google.cloud import storage

from settings import AwsConfig, GoogleConfig

logger = logging.getLogger(__name__)


class ProgressPercentage:

    def __init__(self, filename: str) -> None:
        
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._uploaded = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount: int) -> None:

        with self._lock:
            self._uploaded += bytes_amount
            percentage = (self._uploaded / self._size) * 100
            sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._uploaded, self._size, percentage))
            sys.stdout.flush()


class FileUploaderClass:

    def create_file_uploader(self, provider: str) -> None:
        if provider == "AWS":
            return S3FileUploader()
        elif provider == "Google":
            return GoogleCloudFileUploader()
        elif provider == "Azure":
            return AzureFileUploader()
        else:
            raise ValueError("Invalid provider")


class S3FileUploader:

    def __init__(self):
        self.access_key = AwsConfig.AWS_ACCESS_KEY
        self.secret_access_key = AwsConfig.AWS_SECRET_ACCESS_KEY
        self.bucket_name = AwsConfig.AWS_BUCKET_NAME
        self.region = AwsConfig.AWS_DEFAULT_REGION
        self.endpoint_url = AwsConfig.AWS_ENDPOINT_URL
        self.root_folder = AwsConfig.DEFAULT_ROOT_FOLDER

    def upload_file(self, file_path: str, key_path: str, region: str=None) -> int:

        logger.info(f"Uploading {file_path} to AWS S3 Storage")

        if not os.access(file_path, os.F_OK):
            raise FileNotFoundError(f"File {file_path} not found")

        if not region:
            region = self.region

        s3 = boto3.resource(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_access_key,
            region_name=region
        )

        config = TransferConfig(
            multipart_threshold=1024 * 25,
            max_concurrency=10,
            multipart_chunksize=1024 * 25,
            use_threads=True
        )

        try:
            s3.meta.client.upload_file(file_path, self.bucket_name, key_path, \
                Config=config, Callback=ProgressPercentage(file_path))
            return 200
        except Exception as e:
            logger.critical(f"Upload Error: {e}")
            return 500

    def get_shareable_link(self, key_path: str, region: str=None) -> str:

        logger.info(f"Retrieving AWS S3 Shareable Link")

        if not region:
            region = self.region

        try:
            s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                endpoint_url=self.endpoint_url
            )
        except Exception as e:
            logger.critical(f"s3 Connection Error: {e}")

        result = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key_path,
                'ResponseContentDisposition': 'attachment'
            },
            ExpiresIn=604800
        )

        return result


class GoogleCloudFileUploader:

    def __init__(self):
        self.bucket_name = GoogleConfig.GGL_BUCKET_NAME
        self.credentials_path = GoogleConfig.GGL_CREDENTIALS_PATH
        self.root_folder = GoogleConfig.DEFAULT_ROOT_FOLDER

    def upload_file(self, file_path: str, key_path: str) -> int:

        logger.info(f"Uploading {file_path} to Google Cloud Storage")

        if not os.access(file_path, os.F_OK):
            raise FileNotFoundError(f"File {file_path} not found")

        try:
            storage_client = storage.Client.from_service_account_json(self.credentials_path)
            bucket = storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(key_path)
            try:
                blob.upload_from_filename(file_path, predefined_acl="publicRead")
            except FileNotFoundError as e:
                logger.critical(f"File Not Found: {e}")
                return 500
            except Exception as e:
                logger.critical(f"Upload Error: {e}")
                return 500
            return 200
        except Exception as e:
            logger.critical(f"Upload Error: {e}")
            return 500
            

    def get_shareable_link(self, key_path: str) -> str | None:

        logger.info(f"Retrieving Google Storage Shareable Link")
        
        try:
            storage_client = storage.Client.from_service_account_json(self.credentials_path)
            bucket = storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(key_path)

            download_url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(days=7),
                method="GET",
                response_disposition="attachment"
            )

            return download_url
        except Exception as e:
            logger.critical(f"Get Shareable Link Error: {e}")
            return None


class AzureFileUploader:

    def upload_file(self, file_path: str) -> int:
        # Upload file to Azure
        pass

    def get_shareable_link(self, key_path: str) -> str:
        # Get shareable link from Azure
        pass