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


class ProgressPercentage(object):

    def __init__(self, filename: str) -> None:
        
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._uploaded = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount: int) -> None:

        with self._lock:
            self._uploaded += bytes_amount
            percentage = (self._uploaded / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._uploaded, self._size,
                    percentage))
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


class FileUploader:

    def upload_file(self, file_path: str):
        pass


class S3FileUploader(FileUploader):

    def __init__(self):
        self.access_key = AwsConfig.AWS_ACCESS_KEY
        self.secret_access_key = AwsConfig.AWS_SECRET_ACCESS_KEY
        self.bucket_name = AwsConfig.AWS_BUCKET_NAME
        self.region = AwsConfig.AWS_DEFAULT_REGION
        self.endpoint_url = AwsConfig.AWS_ENDPOINT_URL
        self.root_folder = AwsConfig.DEFAULT_ROOT_FOLDER

    def upload_file(self, file_path: str, key_path: str, region: str=None) -> int:

        logger.info(f"Uploading {file_path} to AWS S3 Storage")

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

class GoogleCloudFileUploader(FileUploader):

    def __init__(self):
        self.bucket_name = GoogleConfig.GGL_BUCKET_NAME
        self.credentials_path = GoogleConfig.GGL_CREDENTIALS_PATH
        self.root_folder = GoogleConfig.DEFAULT_ROOT_FOLDER

    def upload_file(self, file_path: str, key_path: str) -> int:

        logger.info(f"Uploading {file_path} to Google Cloud Storage")
        
        try:
            storage_client = storage.Client.from_service_account_json(self.credentials_path)
            bucket = storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(key_path)
            blob.upload_from_filename(file_path, predefined_acl="publicRead")
            return 200
        except Exception as e:
            logger.critical(f"Upload Error: {e}")
            return 500

    def get_shareable_link(self, key_path: str) -> str:

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


class AzureFileUploader(FileUploader):

    def upload_file(self, file_path: str) -> int:
        # Upload file to Azure
        pass

    def get_shareable_link(self, key_path: str) -> str:
        # Get shareable link from Azure
        pass


if __name__ == '__main__':

    # # We can test file upload by running this file directly
    # provider = "AWS"
    # file_path = "upload_tests/testfile.txt"
    # file_basename = os.path.basename(file_path)

    # f = FileUploaderClass()
    # uploader = f.create_file_uploader(provider)
    # uploader.upload_file(file_path, f"testfolder/{file_basename}")

    # link = uploader.get_shareable_link(f"testfolder/{file_basename}")
    # print(link)

    # We can test file upload by running this file directly
    provider = "Google"
    file_path = "upload_tests/testfile6.txt"
    file_basename = os.path.basename(file_path)

    f = FileUploaderClass()
    uploader = f.create_file_uploader(provider)
    uploader.upload_file(file_path, f"testfolder/{file_basename}")

    link = uploader.get_shareable_link(f"testfolder/{file_basename}")
    print(link)