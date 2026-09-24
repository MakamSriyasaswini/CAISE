import boto3

from gateway.config.settings import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET
)

from gateway.services.storage_provider import StorageProvider


class MinIOProvider(StorageProvider):

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name="us-east-1"
        )

        self.bucket = MINIO_BUCKET

    def upload_file(self, file, filename, content_type):

        self.client.upload_fileobj(
            file,
            self.bucket,
            filename
        )

        response = self.client.head_object(
            Bucket=self.bucket,
            Key=filename
        )

        return response["ContentLength"]

    def list_files(self):

        response = self.client.list_objects_v2(
            Bucket=self.bucket
        )

        files = []

        for obj in response.get("Contents", []):
            files.append({
                "filename": obj["Key"],
                "size": obj["Size"]
            })

        return files

    def download_file(self, filename):

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=filename
        )

        return response["Body"].read()

    def delete_file(self, filename):

        self.client.delete_object(
            Bucket=self.bucket,
            Key=filename
        )

        return {
            "filename": filename,
            "provider": "MinIO-A",
            "status": "DELETED"
        }

    def migrate_object_to(self, filename, target_provider):

        file_data = self.download_file(filename)

        from io import BytesIO

        target_provider.upload_file(
            BytesIO(file_data),
            filename,
            "application/octet-stream"
        )

        return {
            "filename": filename,
            "source_provider": "MinIO-A",
            "target_provider": type(target_provider).__name__,
            "status": "COPIED"
        }

    def get_storage_usage(self):

        response = self.client.list_objects_v2(
            Bucket=self.bucket
        )

        total_size = 0

        for obj in response.get("Contents", []):
            total_size += obj["Size"]

        return total_size
