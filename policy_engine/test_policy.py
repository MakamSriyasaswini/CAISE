from datetime import datetime, timedelta

from policy import classify_object


def test_hot_object():
    now = datetime.now()

    result = classify_object(
        download_count=8,
        last_access=now - timedelta(days=2),
        uploaded_at=now - timedelta(days=60)
    )

    assert result == "HOT"


def test_warm_object():
    now = datetime.now()

    result = classify_object(
        download_count=2,
        last_access=now - timedelta(days=15),
        uploaded_at=now - timedelta(days=20)
    )

    assert result == "WARM"


def test_cold_object():
    now = datetime.now()

    result = classify_object(
        download_count=1,
        last_access=now - timedelta(days=45),
        uploaded_at=now - timedelta(days=60)
    )

    assert result == "COLD"


def test_never_accessed_old_object():
    now = datetime.now()

    result = classify_object(
        download_count=0,
        last_access=None,
        uploaded_at=now - timedelta(days=60)
    )

    assert result == "COLD"


def test_never_accessed_recent_object():
    now = datetime.now()

    result = classify_object(
        download_count=0,
        last_access=None,
        uploaded_at=now - timedelta(days=5)
    )

    assert result == "WARM"


def test_hot_threshold():
    now = datetime.now()

    result = classify_object(
        download_count=5,
        last_access=now - timedelta(days=2),
        uploaded_at=now - timedelta(days=60)
    )

    assert result == "HOT"