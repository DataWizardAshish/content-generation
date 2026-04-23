from src.llm_client import call_llm
from src.parser import parse_questions
from src.prompts import SYSTEM_PROMPT, build_generation_prompt
from src import database as db
from src.logger import get_logger

logger = get_logger("generation_service")


def generate_questions(
    chapter_text: str,
    num_questions: int = 10,
    chapter_title: str = "",
) -> dict:
    """Full pipeline: text → LLM → parse → save drafts."""
    logger.info("Starting generation: title='%s', num=%d", chapter_title, num_questions)

    run_id = db.insert_generation_run(chapter_title, chapter_text, num_questions)
    prompt = build_generation_prompt(chapter_text, num_questions, chapter_title)

    try:
        raw = call_llm(prompt, system=SYSTEM_PROMPT)
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return {"run_id": run_id, "questions": [], "error": f"LLM call failed: {e}"}

    try:
        questions = parse_questions(raw)
    except ValueError as e:
        logger.error("Parse failed, retrying once: %s", e)
        retry_prompt = prompt + '\n\nCRITICAL: Return ONLY a JSON object {"questions": [...]}. No other text.'
        try:
            raw = call_llm(retry_prompt, system=SYSTEM_PROMPT)
            questions = parse_questions(raw)
        except Exception as e2:
            logger.error("Retry also failed: %s", e2)
            return {"run_id": run_id, "questions": [], "error": f"Parse failed after retry: {e2}"}

    draft_ids = db.insert_draft_questions(run_id, questions)
    logger.info("Generation complete: run_id=%d, %d questions saved", run_id, len(questions))

    return {
        "run_id": run_id,
        "questions": questions,
        "draft_ids": draft_ids,
        "error": None,
    }
