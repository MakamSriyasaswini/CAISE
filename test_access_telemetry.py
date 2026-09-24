from gateway.services.telemetry_service import (
    record_object_access,
    redis_client
)


def test_access_telemetry():
    object_name = "javaLikeNames.txt"
    key = f"caise:object:{object_name}:last_access"

    record_object_access(object_name)

    last_access = redis_client.get(key)

    assert last_access is not None