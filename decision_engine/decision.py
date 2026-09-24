# CAISE Storage Decision Engine


def make_storage_decision(classification, potential_savings):
    """
    Makes a storage decision based on policy classification
    and potential cost savings.

    Returns both the storage decision and the reason.

    This function only recommends a decision.
    It does not perform migration.
    """

    if classification == "HOT":

        decision = "KEEP HOT"
        reason = (
            "Object has at least 5 downloads and was accessed "
            "within the last 7 days."
        )

    elif classification == "WARM":

        decision = "KEEP WARM"
        reason = (
            "Object has been accessed recently and does not "
            "meet HOT criteria."
        )

    elif classification == "COLD":

        decision = "KEEP COLD"
        reason = (
            "Object has not been accessed for more than 30 days."
        )

    else:

        decision = "NO DECISION"
        reason = "Invalid or unknown storage classification."

    return decision, reason