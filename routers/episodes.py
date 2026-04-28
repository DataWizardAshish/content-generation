from fastapi import APIRouter, HTTPException, Query
from src import database as db

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("")
def list_episodes():
    episodes = db.get_episodes()
    return {"episodes": episodes}


@router.get("/{episode_id}")
def get_episode(episode_id: int, device_id: str = Query(default="")):
    ep = db.get_episode(episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    if device_id:
        ep_progress_rows = db.get_user_episode_progress(device_id)
        ep_data = next((r for r in ep_progress_rows if r["episode_id"] == episode_id), None)
        ep["user_progress"] = ep_data
    return ep


@router.get("/{episode_id}/questions")
def get_episode_questions(episode_id: int, device_id: str = Query(default="")):
    ep = db.get_episode(episode_id)
    if not ep:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")

    questions = db.get_episode_questions(episode_id)

    if device_id:
        ep_progress_rows = db.get_user_episode_progress(device_id)
        ep_data = next((r for r in ep_progress_rows if r["episode_id"] == episode_id), {})
    else:
        ep_data = {}

    return {
        "episode": ep,
        "questions": questions,
        "user_progress": ep_data,
    }
