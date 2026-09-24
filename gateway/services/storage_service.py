from gateway.services.provider_factory import get_storage_provider

from gateway.config.settings import MINIO_BUCKET

from gateway.services.metadata_service import save_metadata

from gateway.services.telemetry_service import (
    record_upload,
    record_object_upload,
    record_storage_usage
)


storage_provider = get_storage_provider()


def upload_file(file, filename, content_type):

    file_size = storage_provider.upload_file(
        file,
        filename,
        content_type
    )

    save_metadata(
        object_name=filename,
        bucket_name=MINIO_BUCKET,
        object_key=filename,
        file_size=file_size,
        content_type=content_type,
        storage_provider="MinIO-A"
    )

    record_upload()
    record_object_upload(filename)

    total_storage = get_storage_usage()
    record_storage_usage(total_storage)

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "size": file_size,
        "storage_provider": "MinIO-A"
    }


def list_files():

    return storage_provider.list_files()


def download_file(filename):

    return storage_provider.download_file(filename)


def get_storage_usage():

    return storage_provider.get_storage_usage()