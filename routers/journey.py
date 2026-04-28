from fastapi import APIRouter, Query
from src import database as db
from services.journey_calculator import build_journey_response

router = APIRouter(prefix="/journey", tags=["journey"])


@router.get("")
def get_journey(device_id: str = Query(..., description="Device identifier")):
    progress = db.get_user_progress(device_id)
    ep_progress_rows = db.get_user_episode_progress(device_id)
    episodes = db.get_episodes()

    ep_progress_map = {r["episode_id"]: r for r in ep_progress_rows}
    progress["_episode_progress"] = ep_progress_map

    return build_journey_response(progress, episodes, progress.get("weekly_active_days", 0))
