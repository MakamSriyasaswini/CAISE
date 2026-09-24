from gateway.services.storage_service import get_storage_usage


def test_storage_usage():
    total_size = get_storage_usage()

    assert total_size >= 0