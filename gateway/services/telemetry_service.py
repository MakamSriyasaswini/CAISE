import time

import redis

from gateway.config.settings import (
    REDIS_URL,
    REDIS_HOST,
    REDIS_PORT
)


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



def test_redis_connection():
    return redis_client.ping()


def record_upload():
    redis_client.incr(
        "caise:upload_count"
    )


def get_upload_count():
    count = redis_client.get(
        "caise:upload_count"
    )

    if count is None:
        return 0

    return int(count)


def record_object_upload(object_name):
    redis_client.incr(
        f"caise:object:{object_name}:upload_count"
    )


def record_object_download(object_name):
    redis_client.incr(
        f"caise:object:{object_name}:download_count"
    )


def record_object_access(object_name):
    redis_client.set(
        f"caise:object:{object_name}:last_access",
        int(time.time())
    )


def record_storage_usage(total_size):
    redis_client.set(
        "caise:storage:usage_bytes",
        total_size
    )
