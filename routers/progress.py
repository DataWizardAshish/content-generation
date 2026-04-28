from fastapi import APIRouter, Query
from models.enrichment import AnswerRequest
from src import database as db

router = APIRouter(prefix="/user-progress", tags=["progress"])


@router.get("")
def get_progress(device_id: str = Query(..., description="Device identifier")):
    progress = db.get_user_progress(device_id)
    ep_progress = db.get_user_episode_progress(device_id)

    answered = progress.get("questions_answered", 0)
    correct = progress.get("questions_correct", 0)
    accuracy = round(correct / answered * 100, 1) if answered > 0 else 0.0

    ep_completion_map = {
        str(r["episode_id"]): {
            "attempted": r["questions_attempted"],
            "correct": r["questions_correct"],
            "completed_at": r.get("completed_at"),
        }
        for r in ep_progress
    }

    return {
        **progress,
        "accuracy_percent": accuracy,
        "episode_completion_map": ep_completion_map,
    }


@router.post("/answer")
def record_answer(body: AnswerRequest):
    updated = db.record_answer(
        body.device_id, body.question_id, body.was_correct, body.time_taken_seconds
    )
    answered = updated.get("questions_answered", 0)
    correct = updated.get("questions_correct", 0)
    return {
        **updated,
        "accuracy_percent": round(correct / answered * 100, 1) if answered > 0 else 0.0,
    }
