import datetime
from fastapi import APIRouter, Query
from src import database as db
from services.shloka_rotation import get_todays_shloka_index

router = APIRouter(prefix="/home", tags=["home"])


def _greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 6:
        return "The night is still. A good time for reflection, traveler."
    elif hour < 12:
        return "Good morning, traveler. The story awaits."
    elif hour < 17:
        return "The afternoon sun is high. Walk a few steps with Rama today."
    elif hour < 21:
        return "As dusk falls, the epic calls you back."
    else:
        return "The stars are out. Even Valmiki composed by night."


def _get_daily_insight():
    try:
        from src.insight_generation import generate_insight_via_llm
        return db.get_or_create_todays_insight(generate_insight_via_llm)
    except Exception:
        day_index = datetime.date.today().timetuple().tm_yday
        return db.get_insight_by_index(day_index)


@router.get("")
def get_home(device_id: str = Query(default="anonymous")):
    progress = db.get_user_progress(device_id)
    episodes = db.get_episodes()

    # daily shloka
    shlokas = db.get_active_shlokas()
    shloka = None
    if shlokas:
        idx = get_todays_shloka_index(device_id, len(shlokas))
        shloka = shlokas[idx]

    # daily story insight
    raw_insight = _get_daily_insight()
    daily_insight = None
    if raw_insight:
        daily_insight = {
            "id": raw_insight["id"],
            "title": raw_insight["title"],
            "narrative": raw_insight["narrative"],
            "lesson": raw_insight["lesson"],
            "story_phase": raw_insight.get("story_phase"),
            "character": raw_insight.get("character"),
        }

    # continue journey — determine current episode
    ep_progress_rows = db.get_user_episode_progress(device_id)
    current_ep_id = progress.get("current_episode_id")

    if not current_ep_id and ep_progress_rows:
        # infer from episode progress rows (Flutter saves locally, not to backend)
        incomplete = [
            r for r in ep_progress_rows
            if r.get("completed_at") is None and r.get("questions_attempted", 0) > 0
        ]
        if incomplete:
            current_ep_id = max(incomplete, key=lambda r: r["episode_id"])["episode_id"]
        else:
            last_ep_id = max(r["episode_id"] for r in ep_progress_rows)
            next_ep = next((e for e in episodes if e["id"] > last_ep_id), None)
            current_ep_id = next_ep["id"] if next_ep else last_ep_id

    current_ep_id = current_ep_id or 1
    current_ep = next((e for e in episodes if e["id"] == current_ep_id), episodes[0] if episodes else None)

    continue_journey = None
    if current_ep:
        ep_questions = db.get_episode_questions(current_ep_id)
        ep_data = next((r for r in ep_progress_rows if r["episode_id"] == current_ep_id), {})
        attempted = ep_data.get("questions_attempted", 0)
        remaining = max(0, len(ep_questions) - attempted)
        continue_journey = {
            "current_episode_id": current_ep_id,
            "episode_name": current_ep["episode_name"],
            "questions_remaining": remaining,
            "scene_glimpse": current_ep.get("opening_text"),
        }

    # recent wisdom
    saved = db.get_saved_questions(device_id)[:3]

    weekly = progress.get("weekly_active_days", 0)
    from services.streak import week_summary_copy
    week_summary = week_summary_copy(weekly)

    return {
        "greeting": _greeting(),
        "daily_shloka": shloka,
        "daily_insight": daily_insight,
        "continue_journey": continue_journey,
        "recent_wisdom": saved,
        "week_summary": week_summary,
    }
