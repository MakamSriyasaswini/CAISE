from datetime import datetime, timedelta
from io import BytesIO

import redis

from decision_engine.decision import make_storage_decision
from decision_engine.migration_planner import plan_migration
from gateway.services.metadata_service import (
    get_db_connection,
    save_metadata
)
from gateway.services.minio_b_provider import MinIOBProvider
from gateway.services.minio_provider import MinIOProvider
from gateway.services.storage_action_service import execute_storage_action
from policy_engine.policy import classify_object


HOT_FILE = "stage13_hot.txt"
WARM_FILE = "stage13_warm.txt"
COLD_FILE = "stage13_cold.txt"

OBJECTS = {
    HOT_FILE: b"CAISE HOT storage tier object.",
    WARM_FILE: b"CAISE WARM storage tier object.",
    COLD_FILE: b"CAISE COLD storage tier object."
}

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

minio_a = MinIOProvider()
minio_b = MinIOBProvider()

now = datetime.now()


def remove_metadata(filename):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM object_metadata
                WHERE object_key = %s
                """,
                (filename,)
            )
        connection.commit()
    finally:
        connection.close()


def remove_test_data(filename):
    for provider in (minio_a, minio_b):
        try:
            provider.delete_file(filename)
        except Exception:
            pass

    remove_metadata(
        filename
    )

    redis_client.delete(
        f"caise:object:{filename}:download_count"
    )

    redis_client.delete(
        f"caise:object:{filename}:last_access"
    )


def set_telemetry(filename, downloads, last_access):
    redis_client.set(
        f"caise:object:{filename}:download_count",
        downloads
    )

    redis_client.set(
        f"caise:object:{filename}:last_access",
        int(last_access.timestamp())
    )


def set_upload_time(filename, uploaded_at):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE object_metadata
                SET uploaded_at = %s
                WHERE object_key = %s
                """,
                (uploaded_at, filename)
            )
        connection.commit()
    finally:
        connection.close()


def get_metadata(filename):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    object_name,
                    file_size,
                    storage_provider,
                    uploaded_at
                FROM object_metadata
                WHERE object_key = %s
                """,
                (filename,)
            )
            return cursor.fetchone()
    finally:
        connection.close()


def find_object(provider, filename):
    return next(
        (
            obj
            for obj in provider.list_files()
            if obj["filename"] == filename
        ),
        None
    )


def print_status(label, value, success=True):
    status = "PASS" if success else "FAIL"
    print(f"{label:<30} {value:<18} [{status}]")


print()
print("=" * 72)
print("CAISE | CONTROLLED STORAGE TIER EVALUATION")
print("=" * 72)

print("\n[INITIALIZATION]")

for filename in OBJECTS:
    remove_test_data(filename)

print_status("Environment", "Ready")

print("\n[OBJECT CREATION]")

for filename, content in OBJECTS.items():
    size = minio_a.upload_file(
        BytesIO(content),
        filename,
        "text/plain"
    )

    save_metadata(
        object_name=filename,
        bucket_name=minio_a.bucket,
        object_key=filename,
        file_size=size,
        content_type="text/plain",
        storage_provider="MinIO-A"
    )

    print_status(
        filename,
        f"{size} bytes",
        True
    )

print("\n[ACCESS PROFILE]")

profiles = {
    HOT_FILE: (5, 2, 2),
    WARM_FILE: (2, 10, 10),
    COLD_FILE: (0, 40, 45)
}

for filename, (downloads, access_days, upload_days) in profiles.items():
    set_telemetry(
        filename,
        downloads,
        now - timedelta(days=access_days)
    )

    set_upload_time(
        filename,
        now - timedelta(days=upload_days)
    )

    print(
        f"{filename:<30}"
        f"downloads={downloads:<3} "
        f"last_access={access_days}d "
        f"uploaded={upload_days}d"
    )

print("\n[POLICY EVALUATION]")

classifications = {}

for filename in OBJECTS:
    metadata = get_metadata(filename)

    downloads = int(
        redis_client.get(
            f"caise:object:{filename}:download_count"
        )
    )

    access_timestamp = int(
        redis_client.get(
            f"caise:object:{filename}:last_access"
        )
    )

    classification = classify_object(
        download_count=downloads,
        last_access=datetime.fromtimestamp(access_timestamp),
        uploaded_at=metadata[3]
    )

    classifications[filename] = classification

    print_status(
        filename,
        classification,
        classification in {"HOT", "WARM", "COLD"}
    )

print("\n[DECISION AND MIGRATION PLAN]")

plans = {}

for filename in OBJECTS:
    classification = classifications[filename]

    decision, reason = make_storage_decision(
        classification,
        0
    )

    plan = plan_migration(
        filename=filename,
        current_classification=classification,
        decision=decision,
        current_provider="MinIO-A"
    )

    plans[filename] = plan

    print()
    print(f"Object                 {filename}")
    print(f"Classification          {classification}")
    print(f"Decision                {decision}")
    print(f"Target provider         {plan['target_provider']}")
    print(f"Action                  {plan['action']}")

print("\n[STORAGE EXECUTION]")

results = {}

for filename, plan in plans.items():
    result = execute_storage_action(
        filename=filename,
        current_provider=plan["current_provider"],
        target_provider=plan["target_provider"],
        action=plan["action"]
    )

    results[filename] = result

    print_status(
        filename,
        result["status"],
        result["status"] in {"VERIFIED", "SKIPPED"}
    )

print("\n[FINAL STORAGE STATE]")

for filename in OBJECTS:
    classification = classifications[filename]

    object_a = find_object(
        minio_a,
        filename
    )

    object_b = find_object(
        minio_b,
        filename
    )

    metadata = get_metadata(filename)

    expected_provider = (
        "MinIO-B"
        if classification == "COLD"
        else "MinIO-A"
    )

    actual_provider = (
        metadata[2]
        if metadata
        else None
    )

    location_valid = (
        (classification == "COLD" and object_b and not object_a)
        or
        (classification in {"HOT", "WARM"} and object_a and not object_b)
    )

    metadata_valid = (
        actual_provider == expected_provider
    )

    print()
    print(f"Object                   {filename}")
    print(f"Tier                     {classification}")
    print(
        f"MinIO-A                  "
        f"{'PRESENT' if object_a else 'ABSENT'}"
    )
    print(
        f"MinIO-B                  "
        f"{'PRESENT' if object_b else 'ABSENT'}"
    )
    print_status(
        "PostgreSQL provider",
        actual_provider or "Missing",
        metadata_valid
    )
    print_status(
        "Physical placement",
        "Correct" if location_valid else "Incorrect",
        location_valid
    )

overall_success = all(
    results[filename]["status"] in {"VERIFIED", "SKIPPED"}
    for filename in OBJECTS
)

overall_success = overall_success and all(
    (
        (
            classifications[filename] == "COLD"
            and find_object(minio_b, filename)
            and not find_object(minio_a, filename)
        )
        or
        (
            classifications[filename] in {"HOT", "WARM"}
            and find_object(minio_a, filename)
            and not find_object(minio_b, filename)
        )
    )
    for filename in OBJECTS
)

print()
print("=" * 72)
print(
    "RESULT : "
    + (
        "TIERING DEMONSTRATION VERIFIED"
        if overall_success
        else "TIERING DEMONSTRATION FAILED"
    )
)
print("=" * 72)
print()