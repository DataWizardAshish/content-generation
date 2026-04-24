import re
import time
import json
import hashlib
from pathlib import Path
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

from src.logger import get_logger

logger = get_logger("crawler")

BASE_URL = "https://en.wikisource.org"
INDEX_URL = "https://en.wikisource.org/wiki/The_Ramayana"
CACHE_DIR = Path("crawler_cache")
STATE_FILE = Path("crawler_state.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EpicQuizBot/1.0; educational use)"}
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2


# ── HTTP ──────────────────────────────────────────────────────────────────────

def _fetch(url: str) -> str | None:
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{cache_key}.html"
    CACHE_DIR.mkdir(exist_ok=True)

    if cache_path.exists():
        logger.info("Cache hit: %s", url)
        return cache_path.read_text(encoding="utf-8")

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                cache_path.write_text(r.text, encoding="utf-8")
                logger.info("Fetched: %s", url)
                return r.text
            logger.warning("HTTP %d for %s", r.status_code, url)
        except requests.RequestException as e:
            logger.warning("Attempt %d failed for %s: %s", attempt, url, e)
        if attempt < RETRY_ATTEMPTS:
            time.sleep(RETRY_DELAY)
    return None


# ── INDEX PARSER ──────────────────────────────────────────────────────────────

def build_nav_map() -> list[dict]:
    """Parse index page → ordered list of {book, canto_title, url}."""
    html = _fetch(INDEX_URL)
    if not html:
        raise RuntimeError("Failed to fetch Ramayana index")

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    chapters = []
    seen_urls = set()

    for link in links:
        href = link["href"]
        if "/wiki/The_Ramayana/" not in href:
            continue
        full_url = BASE_URL + href if href.startswith("/") else href
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        path_parts = href.split("/wiki/The_Ramayana/")[1].split("/")
        if len(path_parts) == 1:
            book = "Invocation"
            canto_title = unquote(path_parts[0]).replace("_", " ")
        else:
            book = unquote(path_parts[0]).replace("_", " ")
            canto_title = unquote(path_parts[1]).replace("_", " ")

        chapters.append({
            "book": book,
            "canto_title": canto_title,
            "url": full_url,
        })

    logger.info("Nav map built: %d chapters", len(chapters))
    return chapters


# ── CONTENT PARSER ────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_chapter_text(url: str) -> str | None:
    html = _fetch(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    poem_div = soup.find("div", class_="ws-poem") or soup.find("div", class_="poem")
    if not poem_div:
        logger.warning("No poem div found at %s", url)
        return None

    stanzas = poem_div.find_all("div", class_="ws-poem-stanza")
    if stanzas:
        parts = [_clean_text(s.get_text(separator=" ")) for s in stanzas]
    else:
        paras = poem_div.find_all("p")
        parts = [_clean_text(p.get_text(separator=" ")) for p in paras] if paras else [_clean_text(poem_div.get_text(separator=" "))]

    text = "\n\n".join(p for p in parts if p)
    if not text:
        logger.warning("Empty content at %s", url)
        return None

    return text


# ── STATE MANAGER ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"current_index": 0, "nav_map": None}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_or_build_nav_map(state: dict) -> list[dict]:
    if state.get("nav_map"):
        return state["nav_map"]
    nav_map = build_nav_map()
    state["nav_map"] = nav_map
    save_state(state)
    return nav_map


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def crawl_next() -> dict | None:
    """Fetch next chapter with usable content. Auto-skips chapters with no extractable text.
    Returns {title, text, book, canto_title, url, index, total} or None if exhausted."""
    state = load_state()
    nav_map = get_or_build_nav_map(state)
    total = len(nav_map)

    idx = state.get("current_index", 0)
    attempts = 0

    while idx < total and attempts < total:
        chapter = nav_map[idx]
        text = extract_chapter_text(chapter["url"])
        idx += 1
        attempts += 1

        if text:
            state["current_index"] = idx
            save_state(state)
            book = chapter["book"]
            canto = chapter["canto_title"]
            title = f"{book} – {canto}" if book != "Invocation" else canto
            logger.info("Crawled: %s (%d chars)", title, len(text))
            return {
                "title": title,
                "text": text,
                "book": book,
                "canto_title": canto,
                "url": chapter["url"],
                "index": idx - 1,
                "total": total,
            }
        logger.warning("Skipping chapter with no content: %s", chapter["url"])

    state["current_index"] = idx
    save_state(state)
    logger.info("All chapters crawled or no content found")
    return None


def get_crawl_progress() -> dict:
    state = load_state()
    nav_map = state.get("nav_map")
    total = len(nav_map) if nav_map else "?"
    return {
        "current_index": state.get("current_index", 0),
        "total": total,
    }


def reset_crawl_state():
    state = load_state()
    state["current_index"] = 0
    save_state(state)
