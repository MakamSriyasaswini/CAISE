from gateway.services.minio_provider import MinIOProvider
from gateway.services.minio_b_provider import MinIOBProvider

from gateway.config.settings import STORAGE_PROVIDER


def get_storage_provider():

    if STORAGE_PROVIDER == "MinIO-A":
        return MinIOProvider()

    elif STORAGE_PROVIDER == "MinIO-B":
        return MinIOBProvider()

    raise ValueError(
        f"Unsupported storage provider: {STORAGE_PROVIDER}"
    )