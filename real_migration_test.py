from io import BytesIO

from gateway.config.settings import MINIO_BUCKET
from gateway.services.metadata_service import (
    get_db_connection,
    save_metadata
)
from gateway.services.minio_b_provider import MinIOBProvider
from gateway.services.minio_provider import MinIOProvider
from gateway.services.storage_action_service import execute_storage_action


FILENAME = "stage12_real_migration_test.txt"
CONTENT = (
    b"CAISE Stage 12 migration validation."
    b" Verifying object transfer, integrity and metadata."
)


def find_object(provider, filename):
    return next(
        (
            obj
            for obj in provider.list_files()
            if obj["filename"] == filename
        ),
        None
    )


def get_metadata_provider(filename):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT storage_provider
                FROM object_metadata
                WHERE object_key = %s
                """,
                (filename,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    finally:
        connection.close()


def print_status(label, value, success=True):
    status = "PASS" if success else "FAIL"
    print(f"{label:<30} {value:<20} [{status}]")


minio_a = MinIOProvider()
minio_b = MinIOBProvider()

print()
print("=" * 72)
print("CAISE | REAL MIGRATION VALIDATION")
print("=" * 72)

print("\n[SETUP]")
try:
    minio_a.delete_file(FILENAME)
except Exception:
    pass

try:
    minio_b.delete_file(FILENAME)
except Exception:
    pass

print_status("Test object", FILENAME)
print_status("Source provider", "MinIO-A")
print_status("Target provider", "MinIO-B")

print("\n[UPLOAD]")

source_size = minio_a.upload_file(
    BytesIO(CONTENT),
    FILENAME,
    "text/plain"
)

save_metadata(
    object_name=FILENAME,
    bucket_name=MINIO_BUCKET,
    object_key=FILENAME,
    file_size=source_size,
    content_type="text/plain",
    storage_provider="MinIO-A"
)

source_object = find_object(minio_a, FILENAME)

print_status(
    "Upload",
    f"{source_size} bytes",
    source_object is not None
)

print("\n[MIGRATION]")

result = execute_storage_action(
    filename=FILENAME,
    current_provider="MinIO-A",
    target_provider="MinIO-B",
    action="MIGRATE"
)

print_status("Action", result["action"])
print_status("Migration status", result["status"])
print(f"Message                        {result['message']}")

print("\n[VERIFICATION]")

target_object = find_object(minio_b, FILENAME)
source_object_after = find_object(minio_a, FILENAME)

target_content = (
    minio_b.download_file(FILENAME)
    if target_object
    else None
)

content_valid = target_content == CONTENT
size_valid = (
    target_object is not None
    and target_object["size"] == source_size
)
source_removed = source_object_after is None

metadata_provider = get_metadata_provider(FILENAME)
metadata_valid = metadata_provider == "MinIO-B"

print_status(
    "Target object",
    "Present" if target_object else "Missing",
    target_object is not None
)

print_status(
    "Target size",
    f"{target_object['size']} bytes"
    if target_object
    else "N/A",
    size_valid
)

print_status(
    "Content integrity",
    "Verified" if content_valid else "Mismatch",
    content_valid
)

print_status(
    "Source object",
    "Removed" if source_removed else "Still present",
    source_removed
)

print_status(
    "PostgreSQL provider",
    metadata_provider or "Missing",
    metadata_valid
)

passed = all(
    [
        result["status"] == "VERIFIED",
        target_object is not None,
        size_valid,
        content_valid,
        source_removed,
        metadata_valid,
    ]
)

print()
print("=" * 72)
print(
    "RESULT : "
    + ("MIGRATION VERIFIED" if passed else "MIGRATION FAILED")
)
print("=" * 72)
print()