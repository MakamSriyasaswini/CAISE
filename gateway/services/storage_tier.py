STORAGE_TIER_MAPPING = {
    "HOT": "MinIO-A",
    "WARM": "MinIO-A",
    "COLD": "MinIO-B"
}


def get_storage_provider_for_tier(tier):

    if tier not in STORAGE_TIER_MAPPING:
        raise ValueError(
            f"Unsupported storage tier: {tier}"
        )

    return STORAGE_TIER_MAPPING[tier]