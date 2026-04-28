import json
import re
import datetime
from src.llm_client import call_responses
from src.logger import get_logger

logger = get_logger("insight_generation")

_SYSTEM = (
    "You are Valmiki — the first poet, the composer of the Ramayana. "
    "Each day you offer a single moment of insight from the epic: a character, a decision, a turning point."
)

_VALID_PHASES = {
    "Early Life of Rama", "Exile Phase", "Sita Haran",
    "Search for Sita", "Lanka War", "Return and Reunion",
}


def _recent_titles(n: int = 7) -> list[str]:
    from src import database as db
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT title FROM story_insights WHERE is_active=1 ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


def generate_insight_via_llm() -> dict | None:
    today = datetime.date.today().isoformat()
    recent = _recent_titles(7)
    recent_str = ", ".join(f'"{t}"' for t in recent) if recent else "none"

    prompt = (
        f"Write today's story insight.\n\n"
        f"Requirements:\n"
        f"- A specific moment or decision from the Ramayana (not generic wisdom)\n"
        f"- Tied to one character and one story phase\n"
        f"- Narrative written in present tense, vivid (3-4 sentences, ~80-100 words)\n"
        f"- Lesson: one precise, poetic sentence (not a platitude)\n"
        f"- story_phase must be one of: Early Life of Rama, Exile Phase, Sita Haran, "
        f"Search for Sita, Lanka War, Return and Reunion\n\n"
        f"Today: {today}. Recent titles already written — do not repeat: {recent_str}\n\n"
        f"Return ONLY valid JSON, no markdown fences:\n"
        f'{{"title":"...","narrative":"...","lesson":"...","story_phase":"...","character":"..."}}'
    )

    try:
        raw = call_responses(prompt, system=_SYSTEM)
        raw = raw.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
        data = json.loads(raw)
        required = {"title", "narrative", "lesson", "story_phase", "character"}
        if not required.issubset(data.keys()):
            logger.error("Insight LLM response missing fields: %s", list(data.keys()))
            return None
        if data["story_phase"] not in _VALID_PHASES:
            logger.warning("LLM returned unknown story_phase %r — keeping anyway", data["story_phase"])
        logger.info("Generated insight: %r", data["title"])
        return data
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Insight LLM generation failed: %s", e)
        return None
