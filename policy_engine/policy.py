from datetime import datetime, timedelta


# Policy thresholds
HOT_DOWNLOAD_COUNT = 5
HOT_ACCESS_DAYS = 7
COLD_ACCESS_DAYS = 30


def classify_object(download_count, last_access, uploaded_at):
    """
    Classifies an object as HOT, WARM, or COLD.

    HOT:
        - At least 5 downloads
        - Accessed within the last 7 days

    WARM:
        - Not HOT
        - Accessed within the last 30 days

    COLD:
        - Not accessed for more than 30 days
        - Or never accessed and uploaded more than 30 days ago
    """

    now = datetime.now()

    hot_cutoff = now - timedelta(days=HOT_ACCESS_DAYS)
    cold_cutoff = now - timedelta(days=COLD_ACCESS_DAYS)

    # Case 1: Object has been accessed
    if last_access is not None:

        if download_count >= HOT_DOWNLOAD_COUNT and last_access >= hot_cutoff:
            return "HOT"

        if last_access >= cold_cutoff:
            return "WARM"

        return "COLD"

    # Case 2: Object has never been accessed
    if uploaded_at <= cold_cutoff:
        return "COLD"

    return "WARM"