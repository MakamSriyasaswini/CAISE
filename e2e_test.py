from datetime import datetime, timedelta
from io import BytesIO

import redis

from cost_engine.cost_service import calculate_cost_for_all_objects
from decision_engine.decision import make_storage_decision
from decision_engine.migration_planner import plan_migration
from gateway.services.metadata_service import get_db_connection
from gateway.services.minio_b_provider import MinIOBProvider
from gateway.services.minio_provider import MinIOProvider
from gateway.services.storage_action_service import execute_storage_action
from gateway.services.storage_service import upload_file
from policy_engine.policy_service import classify_all_objects


FILES = {
    "e2e_hot.txt": b"CAISE end-to-end HOT object.",
    "e2e_warm.txt": b"CAISE end-to-end WARM object.",
    "e2e_cold.txt": b"CAISE end-to-end COLD object."
}

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

minio_a = MinIOProvider()
minio_b = MinIOBProvider()


def status(label, value, passed=True):
    result = "PASS" if passed else "FAIL"
    print(f"{label:<30} {value:<20} [{result}]")


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


def remove_test_object(filename):
    for provider in (minio_a, minio_b):
        try:
            provider.delete_file(filename)
        except Exception:
            pass

    remove_metadata(filename)

    redis_client.delete(
        f"caise:object:{filename}:download_count"
    )

    redis_client.delete(
        f"caise:object:{filename}:last_access"
    )


def set_upload_date(filename, days):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE object_metadata
                SET uploaded_at = %s
                WHERE object_key = %s
                """,
                (datetime.now() - timedelta(days=days), filename)
            )
        connection.commit()
    finally:
        connection.close()


def set_access_profile(filename, downloads, days):
    redis_client.set(
        f"caise:object:{filename}:download_count",
        downloads
    )

    redis_client.set(
        f"caise:object:{filename}:last_access",
        int(
            (datetime.now() - timedelta(days=days)).timestamp()
        )
    )


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


print()
print("=" * 72)
print("CAISE | END-TO-END SYSTEM VALIDATION")
print("=" * 72)

print("\n[INITIALIZATION]")

for filename in FILES:
    remove_test_object(filename)

status("Test environment", "Ready")

print("\n[OBJECT INGESTION]")

for filename, content in FILES.items():
    result = upload_file(
        BytesIO(content),
        filename,
        "text/plain"
    )

    status(
        filename,
        f"{result['size']} bytes",
        result["storage_provider"] == "MinIO-A"
    )

print("\n[TELEMETRY CONFIGURATION]")

profiles = {
    "e2e_hot.txt": (5, 2, 2),
    "e2e_warm.txt": (2, 10, 10),
    "e2e_cold.txt": (0, 40, 45)
}

for filename, profile in profiles.items():
    downloads, access_days, upload_days = profile

    set_access_profile(
        filename,
        downloads,
        access_days
    )

    set_upload_date(
        filename,
        upload_days
    )

    telemetry_valid = (
        int(
            redis_client.get(
                f"caise:object:{filename}:download_count"
            )
        ) == downloads
    )

    status(
        filename,
        f"{downloads} downloads / {access_days}d access",
        telemetry_valid
    )

print("\n[POLICY ENGINE]")

policy_results = classify_all_objects()

policy_map = {
    result["object_name"]: result
    for result in policy_results
    if result["object_name"] in FILES
}

for filename in FILES:

    result = policy_map.get(filename)

    classification_valid = (
        result is not None
        and result["classification"] in {
            "HOT",
            "WARM",
            "COLD"
        }
    )

    if result:
        print(
            f"{filename:<30}"
            f"{result['classification']:<20}"
            f"[{'PASS' if classification_valid else 'FAIL'}]"
        )
    else:
        status(
            filename,
            "Not classified",
            False
        )

print("\n[COST ENGINE]")

cost_results = calculate_cost_for_all_objects()

cost_map = {
    result["object_name"]: result
    for result in cost_results
    if result["object_name"] in FILES
}

for filename in FILES:

    result = cost_map.get(filename)

    cost_valid = result is not None

    if cost_valid:
        print(
            f"{filename:<30}"
            f"{result['classification']:<10}"
            f"${result['monthly_cost']:.6f}"
        )
    else:
        status(
            filename,
            "Cost evaluation failed",
            False
        )

print("\n[DECISION ENGINE]")

plans = {}

for filename in FILES:

    cost_result = cost_map.get(filename)

    if cost_result is None:
        continue

    decision, reason = make_storage_decision(
        classification=cost_result["classification"],
        potential_savings=cost_result["potential_savings"]
    )

    plan = plan_migration(
        filename=filename,
        current_classification=cost_result["classification"],
        decision=decision,
        current_provider="MinIO-A"
    )

    plans[filename] = plan

    print(
        f"{filename:<30}"
        f"{decision:<15}"
        f"{plan['action']:<15}"
        f"{plan['target_provider']}"
    )

print("\n[STORAGE ACTION]")

actions = {}

for filename, plan in plans.items():

    result = execute_storage_action(
        filename=filename,
        current_provider=plan["current_provider"],
        target_provider=plan["target_provider"],
        action=plan["action"]
    )

    actions[filename] = result

    status(
        filename,
        result["status"],
        result["status"] in {
            "VERIFIED",
            "SKIPPED"
        }
    )

print("\n[FINAL VERIFICATION]")

overall = True

for filename in FILES:

    classification = plans[filename]["current_classification"]

    expected_provider = (
        "MinIO-B"
        if classification == "COLD"
        else "MinIO-A"
    )

    object_a = find_object(
        minio_a,
        filename
    )

    object_b = find_object(
        minio_b,
        filename
    )

    metadata = get_metadata(filename)

    actual_provider = (
        metadata[2]
        if metadata
        else None
    )

    physical_valid = (
        classification == "COLD"
        and object_b is not None
        and object_a is None
    ) or (
        classification in {"HOT", "WARM"}
        and object_a is not None
        and object_b is None
    )

    metadata_valid = (
        actual_provider == expected_provider
    )

    action_valid = actions[filename]["status"] in {
        "VERIFIED",
        "SKIPPED"
    }

    object_valid = (
        (object_b is not None)
        if classification == "COLD"
        else (object_a is not None)
    )

    valid = (
        physical_valid
        and metadata_valid
        and action_valid
        and object_valid
    )

    overall = overall and valid

    print()
    print(f"Object                   {filename}")
    print(f"Classification            {classification}")
    print(
        f"MinIO-A                  "
        f"{'PRESENT' if object_a else 'ABSENT'}"
    )
    print(
        f"MinIO-B                  "
        f"{'PRESENT' if object_b else 'ABSENT'}"
    )

    status(
        "Storage placement",
        "Correct",
        physical_valid
    )

    status(
        "PostgreSQL metadata",
        actual_provider or "Missing",
        metadata_valid
    )

print()
print("=" * 72)
print(
    "RESULT : "
    + (
        "END-TO-END VALIDATION VERIFIED"
        if overall
        else "END-TO-END VALIDATION FAILED"
    )
)
print("=" * 72)
print()