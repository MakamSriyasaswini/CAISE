import psycopg2

from gateway.config.settings import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD
)


def get_db_connection():
    return psycopg2.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD
    )


def save_metadata(
    object_name,
    bucket_name,
    object_key,
    file_size,
    content_type,
    storage_provider
):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO object_metadata
            (
                object_name,
                bucket_name,
                object_key,
                file_size,
                content_type,
                storage_provider
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (object_key)
            DO UPDATE SET
                object_name = EXCLUDED.object_name,
                bucket_name = EXCLUDED.bucket_name,
                file_size = EXCLUDED.file_size,
                content_type = EXCLUDED.content_type,
                storage_provider = EXCLUDED.storage_provider
            """,
            (
                object_name,
                bucket_name,
                object_key,
                file_size,
                content_type,
                storage_provider
            )
        )

        connection.commit()
        cursor.close()

    finally:
        connection.close()

def update_storage_provider(object_key, storage_provider):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE object_metadata
            SET storage_provider = %s
            WHERE object_key = %s
            """,
            (
                storage_provider,
                object_key
            )
        )

        connection.commit()
        cursor.close()

    finally:
        connection.close()