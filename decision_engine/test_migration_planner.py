from migration_planner import plan_migration


def test_no_migration_when_provider_is_correct():
    result = plan_migration(
        filename="hot_file.txt",
        current_classification="HOT",
        decision="KEEP HOT",
        current_provider="MinIO-A"
    )

    assert result["target_provider"] == "MinIO-A"
    assert result["action"] == "NO MIGRATION"
    assert result["filename"] == "hot_file.txt"
    assert result["current_classification"] == "HOT"
    assert result["decision"] == "KEEP HOT"


def test_migration_when_provider_is_wrong():
    result = plan_migration(
        filename="cold_file.txt",
        current_classification="COLD",
        decision="KEEP COLD",
        current_provider="MinIO-A"
    )

    assert result["target_provider"] == "MinIO-B"
    assert result["action"] == "MIGRATE"
    assert result["current_provider"] == "MinIO-A"


def test_warm_uses_minio_a():
    result = plan_migration(
        filename="warm_file.txt",
        current_classification="WARM",
        decision="KEEP WARM",
        current_provider="MinIO-B"
    )

    assert result["target_provider"] == "MinIO-A"
    assert result["action"] == "MIGRATE"


def test_cold_already_on_minio_b():
    result = plan_migration(
        filename="cold_file.txt",
        current_classification="COLD",
        decision="KEEP COLD",
        current_provider="MinIO-B"
    )

    assert result["target_provider"] == "MinIO-B"
    assert result["action"] == "NO MIGRATION"


def test_migration_reason():
    result = plan_migration(
        filename="document.pdf",
        current_classification="COLD",
        decision="KEEP COLD",
        current_provider="MinIO-A"
    )

    assert "MinIO-A" in result["reason"]
    assert "MinIO-B" in result["reason"]