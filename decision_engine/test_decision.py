from decision import make_storage_decision


def test_hot_decision():
    decision, reason = make_storage_decision(
        classification="HOT",
        potential_savings=1.00
    )

    assert decision == "KEEP HOT"
    assert "5 downloads" in reason


def test_warm_decision():
    decision, reason = make_storage_decision(
        classification="WARM",
        potential_savings=1.00
    )

    assert decision == "KEEP WARM"
    assert "accessed recently" in reason


def test_cold_decision():
    decision, reason = make_storage_decision(
        classification="COLD",
        potential_savings=0.00
    )

    assert decision == "KEEP COLD"
    assert "30 days" in reason


def test_invalid_classification():
    decision, reason = make_storage_decision(
        classification="INVALID",
        potential_savings=1.00
    )

    assert decision == "NO DECISION"
    assert "Invalid" in reason