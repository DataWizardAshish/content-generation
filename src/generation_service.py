import json
from src.llm_client import call_llm, call_llm_text
from src.parser import parse_questions
from src.prompts import (
    SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
    SELF_CRITIQUE_SYSTEM_PROMPT,
    build_generation_prompt,
    build_validation_prompt,
    build_self_critique_prompt,
)
from src import database as db
from src.logger import get_logger

logger = get_logger("generation_service")


def _parse_json_array(raw: str) -> list:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _validate_questions(chapter_text: str, questions: list) -> list:
    questions_json = json.dumps(questions, indent=2)
    prompt = build_validation_prompt(chapter_text, questions_json)
    try:
        raw = call_llm_text(prompt, system=VALIDATION_SYSTEM_PROMPT)
        results = _parse_json_array(raw)
        logger.info("Grounding validation: %d results", len(results))
        return results
    except Exception as e:
        logger.error("Grounding validation failed (skipping): %s", e)
        return []


def _self_critique(questions: list) -> list:
    questions_json = json.dumps(questions, indent=2)
    prompt = build_self_critique_prompt(questions_json)
    try:
        raw = call_llm_text(prompt, system=SELF_CRITIQUE_SYSTEM_PROMPT)
        results = _parse_json_array(raw)
        logger.info("Self-critique: %d results", len(results))
        return results
    except Exception as e:
        logger.error("Self-critique failed (skipping): %s", e)
        return []


def _merge_validation(questions: list, validation_results: list) -> list:
    val_map = {v["question"]: v for v in validation_results}
    for q in questions:
        val = val_map.get(q.get("question", ""), {})
        q["validation_status"] = val.get("status", "unvalidated")
        q["validation_reason"] = val.get("reason", "")
        q["validation_supporting_text"] = val.get("supporting_text", "")
        q["confidence_score"] = val.get("confidence_score")
    return questions


def _merge_critique(questions: list, critique_results: list) -> list:
    crit_map = {v["question"]: v for v in critique_results}
    for q in questions:
        crit = crit_map.get(q.get("question", ""), {})
        q["engagement_score"] = crit.get("engagement_score")
        q["engagement_reason"] = crit.get("engagement_reason", "")
        q["is_daily_insight"] = crit.get("is_daily_insight_candidate", False)
        q["improvement_suggestion"] = crit.get("improvement_suggestion", "")
    return questions


def generate_questions(
    chapter_text: str,
    num_questions: int = 10,
    chapter_title: str = "",
) -> dict:
    """Full pipeline: text → generate → validate → self-critique → save drafts."""
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

    # Step 2: grounding validation
    validation_results = _validate_questions(chapter_text, questions)
    if validation_results:
        questions = _merge_validation(questions, validation_results)
        approved_count = sum(1 for v in validation_results if v.get("status") == "approved")
        logger.info("Grounding: %d/%d passed", approved_count, len(questions))

    # Step 3: self-critique (engagement + daily insight)
    critique_results = _self_critique(questions)
    if critique_results:
        questions = _merge_critique(questions, critique_results)
        insight_count = sum(1 for q in questions if q.get("is_daily_insight"))
        logger.info("Self-critique: %d daily insight candidates", insight_count)

    draft_ids = db.insert_draft_questions(run_id, questions)
    logger.info("Generation complete: run_id=%d, %d questions saved", run_id, len(questions))

    return {
        "run_id": run_id,
        "questions": questions,
        "draft_ids": draft_ids,
        "error": None,
    }
