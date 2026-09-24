import os

from dotenv import load_dotenv

load_dotenv()

STORAGE_PROVIDER = os.getenv(
    "STORAGE_PROVIDER",
    "MinIO-A"
)

MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT",
    "http://localhost:9000"
)

MINIO_ACCESS_KEY = os.getenv(
    "MINIO_ACCESS_KEY",
    "minioadmin"
)

MINIO_SECRET_KEY = os.getenv(
    "MINIO_SECRET_KEY",
    "minioadmin"
)

MINIO_BUCKET = os.getenv(
    "MINIO_BUCKET",
    "caise-storage"
)

MINIO_B_ENDPOINT = os.getenv(
    "MINIO_B_ENDPOINT",
    "http://localhost:9100"
)

MINIO_B_BUCKET = os.getenv(
    "MINIO_B_BUCKET",
    "caise-storage"
)

DATABASE_HOST = os.getenv(
    "DATABASE_HOST",
    "localhost"
)

DATABASE_PORT = os.getenv(
    "DATABASE_PORT",
    "5432"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "caise"
)

DATABASE_USER = os.getenv(
    "DATABASE_USER",
    "postgres"
)

DATABASE_PASSWORD = os.getenv(
    "DATABASE_PASSWORD",
    ""
)

REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "localhost"
)

REDIS_PORT = int(
    os.getenv(
        "REDIS_PORT",
        "6379"
    )
)