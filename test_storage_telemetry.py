from gateway.services.storage_service import get_storage_usage
from gateway.services.telemetry_service import (
    record_storage_usage,
    redis_client
)


def test_storage_telemetry():
    total_size = get_storage_usage()

    record_storage_usage(total_size)

    stored_value = redis_client.get(
        "caise:storage:usage_bytes"
    )

    assert stored_value is not None
    assert int(stored_value) == total_size