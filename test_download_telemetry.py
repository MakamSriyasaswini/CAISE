from gateway.services.telemetry_service import (
    record_object_download,
    redis_client
)


def test_download_telemetry():
    object_name = "javaLikeNames.txt"
    key = f"caise:object:{object_name}:download_count"

    initial_count = redis_client.get(key)

    if initial_count is None:
        initial_count = 0
    else:
        initial_count = int(initial_count)

    record_object_download(object_name)

    after_first = int(redis_client.get(key))

    assert after_first == initial_count + 1

    record_object_download(object_name)

    after_second = int(redis_client.get(key))

    assert after_second == initial_count + 2