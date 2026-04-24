from src import database as db
from src.logger import get_logger

logger = get_logger("review_service")


def get_pending() -> list[dict]:
    return db.get_pending_drafts()


def approve(draft_id: int, edited: dict | None = None):
    db.approve_question(draft_id, edited)
    logger.info("Approved question draft_id=%d", draft_id)


def reject(draft_id: int):
    db.reject_question(draft_id)
    logger.info("Rejected question draft_id=%d", draft_id)


def get_library(topic: str = "", difficulty: str = "", chapter: str = "") -> list[dict]:
    return db.get_approved_questions(topic, difficulty, chapter)


def delete_from_library(approved_id: int):
    db.delete_approved_question(approved_id)
    logger.info("Deleted approved question id=%d", approved_id)


def get_filter_options() -> dict:
    return db.get_library_filter_options()


def export_to_json(questions: list[dict]) -> str:
    import json
    export_data = []
    for q in questions:
        export_data.append({
            "question": q["question"],
            "options": {
                "A": q["option_a"],
                "B": q["option_b"],
                "C": q["option_c"],
                "D": q["option_d"],
            },
            "correct_answer": q["correct_answer"],
            "explanation": q["explanation"],
            "difficulty": q["difficulty"],
            "topic": q.get("topic", ""),
            "chapter_title": q.get("chapter_title", ""),
        })
    return json.dumps(export_data, indent=2, ensure_ascii=False)
