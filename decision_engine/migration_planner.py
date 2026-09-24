from gateway.services.storage_tier import get_storage_provider_for_tier

def plan_migration(
    filename,
    current_classification,
    decision,
    current_provider
):

    target_provider = get_storage_provider_for_tier(
        current_classification
    )

    if current_provider == target_provider:

        action = "NO MIGRATION"
        reason = (
            f"Object is already on the required "
            f"{current_classification} provider."
        )

    else:

        action = "MIGRATE"
        reason = (
            f"Object must move from {current_provider} "
            f"to {target_provider}."
        )

    return {
        "filename": filename,
        "current_classification": current_classification,
        "decision": decision,
        "current_provider": current_provider,
        "target_provider": target_provider,
        "action": action,
        "reason": reason
    }