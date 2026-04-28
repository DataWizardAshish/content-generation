import datetime
import hashlib


def get_todays_shloka_index(device_id: str, total: int) -> int:
    """
    Returns a deterministic shloka index for a given device and today's date.
    - Same device + same day = same shloka (deterministic)
    - Different devices = different shlokas on same day
    - Different days = different shlokas for same device
    """
    if total == 0:
        return 0
    key = f"{device_id}{datetime.date.today().isoformat()}"
    hash_int = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return hash_int % total
