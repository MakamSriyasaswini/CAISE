# CAISE Cost Engine


# Storage cost assumptions
# These are project/demo values and can be changed later.

HOT_COST_PER_GB = 3.00
WARM_COST_PER_GB = 2.00
COLD_COST_PER_GB = 1.00


BYTES_PER_GB = 1024 ** 3


def calculate_monthly_cost(file_size, classification):
    """
    Calculates estimated monthly storage cost
    based on object size and policy classification.
    """

    size_in_gb = file_size / BYTES_PER_GB

    if classification == "HOT":
        cost_per_gb = HOT_COST_PER_GB

    elif classification == "WARM":
        cost_per_gb = WARM_COST_PER_GB

    elif classification == "COLD":
        cost_per_gb = COLD_COST_PER_GB

    else:
        raise ValueError("Invalid storage classification")

    monthly_cost = size_in_gb * cost_per_gb

    return monthly_cost
def calculate_potential_savings(file_size, current_classification):
    """
    Calculates the potential monthly savings if the object
    is moved to the next cheaper storage class.
    """

    current_cost = calculate_monthly_cost(
        file_size,
        current_classification
    )

    if current_classification == "HOT":
        cheaper_classification = "WARM"

    elif current_classification == "WARM":
        cheaper_classification = "COLD"

    else:
        cheaper_classification = "COLD"

    cheaper_cost = calculate_monthly_cost(
        file_size,
        cheaper_classification
    )

    savings = current_cost - cheaper_cost

    return {
        "current_classification": current_classification,
        "cheaper_classification": cheaper_classification,
        "current_cost": current_cost,
        "cheaper_cost": cheaper_cost,
        "potential_savings": savings
    }