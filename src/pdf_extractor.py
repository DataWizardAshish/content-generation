from pathlib import Path
from src.logger import get_logger

logger = get_logger("pdf_extractor")

KANDA_TO_BOOK_DIR = {
    "Bala": "Book_I",
    "Ayodhya": "Book_II",
    "Aranya": "Book_III",
    "Kishkindha": "Book_IV",
    "Sundara": "Book_V",
    "Yuddha": "Book_VI",
}
CACHE_DIR = Path("canto_cache")


def fetch_episode_text(kanda: str, sarga_start: int, sarga_end: int) -> tuple[str, list[str]]:
    """Read cached canto files for an episode sarga range. Returns (combined_text, titles)."""
    book_dir = CACHE_DIR / KANDA_TO_BOOK_DIR[kanda]
    parts, titles = [], []
    missing = []
    for n in range(sarga_start, sarga_end + 1):
        path = book_dir / f"Canto_{n}.txt"
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
            titles.append(f"{KANDA_TO_BOOK_DIR[kanda]} Canto {n}")
        else:
            missing.append(n)
    if missing:
        logger.warning("Missing canto files for %s: %s", kanda, missing)
    return "\n\n---\n\n".join(parts), titles


def is_cache_ready() -> bool:
    return (CACHE_DIR / "Book_I").exists() and any((CACHE_DIR / "Book_I").iterdir())


def get_episode_char_count(kanda: str, sarga_start: int, sarga_end: int) -> int:
    text, _ = fetch_episode_text(kanda, sarga_start, sarga_end)
    return len(text)
