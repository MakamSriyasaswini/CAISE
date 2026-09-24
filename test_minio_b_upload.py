from io import BytesIO

from gateway.services.minio_b_provider import MinIOBProvider
from gateway.config.settings import MINIO_B_ENDPOINT, MINIO_B_BUCKET


TEST_FILENAME = "stage12_minio_b_direct_test.txt"

TEST_CONTENT = (
    b"Direct MinIO-B upload test for CAISE Stage 12."
)


print("=" * 70)
print("DIRECT MINIO-B UPLOAD TEST")
print("=" * 70)

print("\nEndpoint:", MINIO_B_ENDPOINT)
print("Bucket:", MINIO_B_BUCKET)

provider = MinIOBProvider()


# --------------------------------------------------
# 1. Remove old test object if it exists
# --------------------------------------------------

print("\n[1] Cleaning old test object...")

try:
    provider.delete_file(TEST_FILENAME)
    print("Old object deleted.")
except Exception:
    print("No old object found. Continuing.")


# --------------------------------------------------
# 2. Upload directly to MinIO-B
# --------------------------------------------------

print("\n[2] Uploading directly to MinIO-B...")

uploaded_size = provider.upload_file(
    BytesIO(TEST_CONTENT),
    TEST_FILENAME,
    "text/plain"
)

print("upload_file() returned size:", uploaded_size)


# --------------------------------------------------
# 3. Check object through list_files()
# --------------------------------------------------

print("\n[3] Checking MinIO-B object...")

objects = provider.list_files()

target = None

for obj in objects:

    if obj["filename"] == TEST_FILENAME:
        target = obj
        break


if target is None:

    print("❌ FAIL: Object not found on MinIO-B.")

else:

    print("✅ Object exists on MinIO-B.")
    print("Listed size:", target["size"], "bytes")


# --------------------------------------------------
# 4. Download and verify content
# --------------------------------------------------

print("\n[4] Downloading object from MinIO-B...")

try:

    downloaded = provider.download_file(
        TEST_FILENAME
    )

    print("Downloaded size:", len(downloaded), "bytes")

    if downloaded == TEST_CONTENT:

        print("✅ Content matches exactly.")

    else:

        print("❌ Content does NOT match.")

except Exception as e:

    print("❌ Download failed:", str(e))


# --------------------------------------------------
# 5. Final result
# --------------------------------------------------

print("\n" + "=" * 70)
print("DIRECT MINIO-B TEST RESULT")
print("=" * 70)

print(
    "Upload returned:",
    uploaded_size,
    "bytes"
)

print(
    "Listed object:",
    "YES" if target else "NO"
)

if target:
    print(
        "Listed size:",
        target["size"],
        "bytes"
    )

print("=" * 70)