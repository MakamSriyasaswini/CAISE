import redis
import psycopg2

from datetime import datetime

from gateway.config.settings import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
    REDIS_URL,
    REDIS_HOST,
    REDIS_PORT
)

from policy_engine.policy import classify_object


if REDIS_URL:
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )
else:
if REDIS_URL:
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )
else:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )

def get_db_connection():
    return psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )


def get_object_metadata():

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                object_name,
                MAX(file_size) AS file_size,
                MAX(storage_provider) AS storage_provider,
                MAX(uploaded_at) AS uploaded_at
            FROM object_metadata
            GROUP BY object_name
            ORDER BY object_name
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_download_count(object_name):

    key = (
        f"caise:object:{object_name}:"
        f"download_count"
    )

    value = redis_client.get(key)

    if value is None:
        return 0

    return int(value)


def get_last_access(object_name):

    key = (
        f"caise:object:{object_name}:"
        f"last_access"
    )

    value = redis_client.get(key)

    if value is None:
        return None

    return datetime.fromtimestamp(
        int(value)
    )


def classify_all_objects():

    objects = get_object_metadata()

    results = []

    for (
        object_name,
        file_size,
        storage_provider,
        uploaded_at
    ) in objects:

        download_count = get_download_count(
            object_name
        )

        last_access = get_last_access(
            object_name
        )

        classification = classify_object(
            download_count=download_count,
            last_access=last_access,
            uploaded_at=uploaded_at
        )

        results.append({
            "object_name": object_name,
            "file_size": file_size,
            "storage_provider": storage_provider,
            "uploaded_at": uploaded_at,
            "download_count": download_count,
            "last_access": last_access,
            "classification": classification
        })

    return results


if __name__ == "__main__":

    print("=" * 70)
    print("CAISE STORAGE POLICY")
    print("=" * 70)

    for result in classify_all_objects():

        print()
        print("Object:", result["object_name"])
        print("Size:", result["file_size"], "bytes")
        print("Provider:", result["storage_provider"])
        print("Uploaded:", result["uploaded_at"])
        print("Downloads:", result["download_count"])
        print("Last Access:", result["last_access"])
        print("Classification:", result["classification"])
