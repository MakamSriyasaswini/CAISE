from cost import calculate_monthly_cost, calculate_potential_savings


def test_hot_monthly_cost():
    cost = calculate_monthly_cost(
        file_size=1 * 1024 * 1024 * 1024,
        classification="HOT"
    )

    assert cost == 3.00


def test_warm_monthly_cost():
    cost = calculate_monthly_cost(
        file_size=1 * 1024 * 1024 * 1024,
        classification="WARM"
    )

    assert cost == 2.00


def test_cold_monthly_cost():
    cost = calculate_monthly_cost(
        file_size=1 * 1024 * 1024 * 1024,
        classification="COLD"
    )

    assert cost == 1.00


def test_hot_to_warm_savings():
    result = calculate_potential_savings(
        file_size=1 * 1024 * 1024 * 1024,
        current_classification="HOT"
    )

    assert result["cheaper_classification"] == "WARM"
    assert result["potential_savings"] == 1.00


def test_warm_to_cold_savings():
    result = calculate_potential_savings(
        file_size=1 * 1024 * 1024 * 1024,
        current_classification="WARM"
    )

    assert result["cheaper_classification"] == "COLD"
    assert result["potential_savings"] == 1.00


def test_cold_no_savings():
    result = calculate_potential_savings(
        file_size=1 * 1024 * 1024 * 1024,
        current_classification="COLD"
    )

    assert result["potential_savings"] == 0.00


def test_invalid_classification():
    try:
        calculate_monthly_cost(
            file_size=1 * 1024 * 1024 * 1024,
            classification="INVALID"
        )
        assert False
    except ValueError:
        assert True