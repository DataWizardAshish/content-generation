from fastapi import APIRouter, HTTPException, Query
from models.enrichment import SaveQuestionRequest
from src import database as db

router = APIRouter(prefix="/saved-questions", tags=["saved"])


@router.get("")
def list_saved(device_id: str = Query(..., description="Device identifier")):
    rows = db.get_saved_questions(device_id)
    return {"count": len(rows), "saved_questions": rows}


@router.post("")
def save_question(body: SaveQuestionRequest):
    # verify question exists
    questions = db.get_approved_questions()
    if not any(q["id"] == body.question_id for q in questions):
        raise HTTPException(status_code=404, detail=f"Question {body.question_id} not found")
    saved = db.save_question(body.device_id, body.question_id, body.user_note)
    return saved


@router.delete("/{question_id}")
def unsave_question(question_id: int, device_id: str = Query(..., description="Device identifier")):
    db.unsave_question(device_id, question_id)
    return {"status": "removed", "question_id": question_id, "device_id": device_id}
