from fastapi import APIRouter, HTTPException
from src import database as db

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/daily")
def get_daily_insight():
    try:
        from src.insight_generation import generate_insight_via_llm
        insight = db.get_or_create_todays_insight(generate_insight_via_llm)
    except Exception:
        import datetime
        day_index = datetime.date.today().timetuple().tm_yday
        insight = db.get_insight_by_index(day_index)

    if not insight:
        raise HTTPException(status_code=404, detail="No story insights available yet.")
    return {
        "id": insight["id"],
        "title": insight["title"],
        "narrative": insight["narrative"],
        "lesson": insight["lesson"],
        "story_phase": insight.get("story_phase"),
        "character": insight.get("character"),
    }
