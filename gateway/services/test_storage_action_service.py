import pytest

from gateway.services.storage_action_service import (
    get_provider,
    execute_storage_action
)


def test_get_minio_a_provider():

    provider = get_provider("MinIO-A")

    assert provider is not None


def test_get_minio_b_provider():

    provider = get_provider("MinIO-B")

    assert provider is not None


def test_invalid_provider():

    with pytest.raises(ValueError):
        get_provider("INVALID")


def test_no_migration():

    result = execute_storage_action(
        filename="test.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-A",
        action="NO MIGRATION"
    )

    assert result["status"] == "SKIPPED"
    assert result["action"] == "NO MIGRATION"
    assert result["filename"] == "test.txt"


def test_unknown_action():

    result = execute_storage_action(
        filename="test.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-B",
        action="UNKNOWN"
    )

    assert result["status"] == "NOT_IMPLEMENTED"


def test_source_object_not_found(monkeypatch):

    class FakeProvider:

        def list_files(self):
            return []

    monkeypatch.setattr(
        "gateway.services.storage_action_service.get_provider",
        lambda name: FakeProvider()
    )

    result = execute_storage_action(
        filename="missing.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-B",
        action="MIGRATE"
    )

    assert result["status"] == "FAILED"
    assert result["message"] == "Source object was not found."


def test_successful_migration(monkeypatch):

    class FakeSource:

        def __init__(self):
            self.deleted = False

        def list_files(self):

            if self.deleted:
                return []

            return [
                {
                    "filename": "test.txt",
                    "size": 100
                }
            ]

        def migrate_object_to(self, filename, target):
            return True

        def delete_file(self, filename):

            self.deleted = True

            return {
                "filename": filename,
                "provider": "MinIO-A",
                "status": "DELETED"
            }

    class FakeTarget:

        def list_files(self):

            return [
                {
                    "filename": "test.txt",
                    "size": 100
                }
            ]

    def fake_provider(name):

        if name == "MinIO-A":
            return FakeSource()

        return FakeTarget()

    metadata_updated = {
        "called": False
    }

    def fake_update_storage_provider(
        object_key,
        storage_provider
    ):

        metadata_updated["called"] = True

    monkeypatch.setattr(
        "gateway.services.storage_action_service.get_provider",
        fake_provider
    )

    monkeypatch.setattr(
        "gateway.services.storage_action_service.update_storage_provider",
        fake_update_storage_provider
    )

    result = execute_storage_action(
        filename="test.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-B",
        action="MIGRATE"
    )

    assert result["status"] == "VERIFIED"
    assert result["action"] == "MIGRATE"
    assert metadata_updated["called"] is True


def test_target_object_not_found(monkeypatch):

    class FakeSource:

        def list_files(self):

            return [
                {
                    "filename": "test.txt",
                    "size": 100
                }
            ]

        def migrate_object_to(self, filename, target):
            return True

    class FakeTarget:

        def list_files(self):
            return []

    def fake_provider(name):

        if name == "MinIO-A":
            return FakeSource()

        return FakeTarget()

    monkeypatch.setattr(
        "gateway.services.storage_action_service.get_provider",
        fake_provider
    )

    result = execute_storage_action(
        filename="test.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-B",
        action="MIGRATE"
    )

    assert result["status"] == "FAILED"
    assert "could not be verified" in result["message"]


def test_size_mismatch(monkeypatch):

    class FakeSource:

        def __init__(self):
            self.deleted = False

        def list_files(self):

            if self.deleted:
                return []

            return [
                {
                    "filename": "test.txt",
                    "size": 100
                }
            ]

        def migrate_object_to(self, filename, target):
            return True

        def delete_file(self, filename):

            self.deleted = True

            return {
                "filename": filename,
                "provider": "MinIO-A",
                "status": "DELETED"
            }

    class FakeTarget:

        def list_files(self):

            return [
                {
                    "filename": "test.txt",
                    "size": 200
                }
            ]

    def fake_provider(name):

        if name == "MinIO-A":
            return FakeSource()

        return FakeTarget()

    monkeypatch.setattr(
        "gateway.services.storage_action_service.get_provider",
        fake_provider
    )

    result = execute_storage_action(
        filename="test.txt",
        current_provider="MinIO-A",
        target_provider="MinIO-B",
        action="MIGRATE"
    )

    assert result["status"] == "FAILED"
    assert "Verification failed" in result["message"]