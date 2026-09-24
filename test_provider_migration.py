from io import BytesIO

from gateway.services.minio_provider import MinIOProvider
from gateway.services.minio_b_provider import MinIOBProvider


TEST_FILENAME = "stage12_provider_migration_test.txt"

TEST_CONTENT = (
    b"CAISE provider migration test. "
    b"This verifies MinIO-A download and MinIO-B upload."
)


def find_object(provider, filename):

    for obj in provider.list_files():

        if obj["filename"] == filename:
            return obj

    return None


print("=" * 70)
print("CAISE STAGE 12 - PROVIDER MIGRATION TEST")
print("=" * 70)


minio_a = MinIOProvider()
minio_b = MinIOBProvider()


# --------------------------------------------------
# 1. Clean previous test object
# --------------------------------------------------

print("\n[1] Cleaning old test objects...")

try:
    minio_a.delete_file(TEST_FILENAME)
except Exception:
    pass

try:
    minio_b.delete_file(TEST_FILENAME)
except Exception:
    pass

print("Cleanup completed.")


# --------------------------------------------------
# 2. Upload known object to MinIO-A
# --------------------------------------------------

print("\n[2] Uploading known object to MinIO-A...")

uploaded_size = minio_a.upload_file(
    BytesIO(TEST_CONTENT),
    TEST_FILENAME,
    "text/plain"
)

print(
    "MinIO-A upload returned:",
    uploaded_size,
    "bytes"
)


# --------------------------------------------------
# 3. Verify MinIO-A object
# --------------------------------------------------

print("\n[3] Checking MinIO-A...")

source_object = find_object(
    minio_a,
    TEST_FILENAME
)

if source_object is None:

    print("❌ FAIL: Object not found on MinIO-A.")
    raise SystemExit(1)

print("✅ Object exists on MinIO-A")
print(
    "MinIO-A listed size:",
    source_object["size"],
    "bytes"
)


# --------------------------------------------------
# 4. Directly download from MinIO-A
# --------------------------------------------------

print("\n[4] Downloading object directly from MinIO-A...")

source_data = minio_a.download_file(
    TEST_FILENAME
)

print(
    "Downloaded from MinIO-A:",
    len(source_data),
    "bytes"
)

if source_data == TEST_CONTENT:

    print("✅ MinIO-A downloaded content matches.")

else:

    print("❌ MinIO-A downloaded content DOES NOT match.")

    print(
        "Expected:",
        len(TEST_CONTENT),
        "bytes"
    )

    print(
        "Received:",
        len(source_data),
        "bytes"
    )


# --------------------------------------------------
# 5. Test migrate_object_to()
# --------------------------------------------------

print("\n[5] Calling MinIO-A.migrate_object_to()...")

migration_result = minio_a.migrate_object_to(
    TEST_FILENAME,
    minio_b
)

print("Migration method returned:")
print(migration_result)


# --------------------------------------------------
# 6. Check MinIO-B
# --------------------------------------------------

print("\n[6] Checking MinIO-B...")

target_object = find_object(
    minio_b,
    TEST_FILENAME
)

if target_object is None:

    print("❌ FAIL: Object not found on MinIO-B.")

else:

    print("✅ Object exists on MinIO-B")

    print(
        "MinIO-B listed size:",
        target_object["size"],
        "bytes"
    )


# --------------------------------------------------
# 7. Download from MinIO-B
# --------------------------------------------------

print("\n[7] Downloading object from MinIO-B...")

target_data = minio_b.download_file(
    TEST_FILENAME
)

print(
    "Downloaded from MinIO-B:",
    len(target_data),
    "bytes"
)

if target_data == TEST_CONTENT:

    print("✅ MinIO-B content matches exactly.")

else:

    print("❌ MinIO-B content DOES NOT match.")


# --------------------------------------------------
# 8. Final result
# --------------------------------------------------

print("\n" + "=" * 70)
print("PROVIDER MIGRATION TEST RESULT")
print("=" * 70)

print(
    "Source upload size:",
    uploaded_size,
    "bytes"
)

print(
    "Source listed size:",
    source_object["size"],
    "bytes"
)

print(
    "Source downloaded size:",
    len(source_data),
    "bytes"
)

print(
    "Target exists:",
    "YES" if target_object else "NO"
)

if target_object:

    print(
        "Target listed size:",
        target_object["size"],
        "bytes"
    )

print(
    "Target downloaded size:",
    len(target_data),
    "bytes"
)

print(
    "Content identical:",
    "YES" if target_data == TEST_CONTENT else "NO"
)

print("=" * 70)