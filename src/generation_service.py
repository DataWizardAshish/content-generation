import json
from src.llm_client import call_llm, call_responses
from src.schemas import VALIDATION_SCHEMA, CRITIQUE_SCHEMA
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


def _parse_results(raw: str) -> list:
    """Parse JSON that may be a bare array or wrapped in {"results": [...]}."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    data = json.loads(raw.strip())
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return []


def _normalize_fields(questions: list) -> list:
    """Map model output field names to DB-compatible keys."""
    for q in questions:
        # source_quote → explanation fallback + validation_supporting_text seed
        source_quote = q.get("source_quote", "")
        q["supporting_text"] = source_quote
        q["validation_supporting_text"] = source_quote
        # narrative_continuation doubles as explanation for legacy UI
        if "narrative_continuation" in q:
            q["explanation"] = q["narrative_continuation"]
        elif not q.get("explanation"):
            q["explanation"] = ""
    return questions


def _validate_questions(chapter_text: str, questions: list) -> list:
    prompt = build_validation_prompt(chapter_text, json.dumps(questions, indent=2))
    try:
        raw = call_responses(prompt, system=VALIDATION_SYSTEM_PROMPT, schema=VALIDATION_SCHEMA)
        results = _parse_results(raw)
        logger.info("Grounding validation: %d results", len(results))
        return results
    except Exception as e:
        logger.error("Grounding validation failed (skipping): %s", e)
        return []


def _self_critique(questions: list) -> list:
    prompt = build_self_critique_prompt(json.dumps(questions, indent=2))
    try:
        raw = call_responses(prompt, system=SELF_CRITIQUE_SYSTEM_PROMPT, schema=CRITIQUE_SCHEMA)
        results = _parse_results(raw)
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
        q["validation_supporting_text"] = val.get("supporting_text") or q.get("validation_supporting_text", "")
        q["confidence_score"] = val.get("confidence_score")
    return questions


def _merge_critique(questions: list, critique_results: list) -> list:
    crit_map = {v["question"]: v for v in critique_results}
    for q in questions:
        crit = crit_map.get(q.get("question", ""), {})
        q["engagement_score"] = crit.get("engagement_score")
        q["enrichment_score"] = crit.get("enrichment_score")
        q["narrative_flow_score"] = crit.get("narrative_flow_score")
        q["engagement_reason"] = crit.get("engagement_reason", "")
        q["is_daily_insight"] = crit.get("is_daily_insight_candidate", False)
        q["improvement_suggestion"] = crit.get("improvement_suggestion", "")
    return questions


def generate_questions(
    chapter_text: str,
    num_questions: int = 10,
    chapter_title: str = "",
    episode_id: int | None = None,
) -> dict:
    """Full pipeline: text → generate → validate → self-critique → save drafts."""
    logger.info("Starting generation: title='%s', num=%d, episode_id=%s", chapter_title, num_questions, episode_id)

    run_id = db.insert_generation_run(chapter_title, chapter_text, num_questions, episode_id)

    episode_metadata = None
    if episode_id:
        ep = db.get_episode(episode_id)
        if ep:
            episode_metadata = {
                "episode_name": ep.get("episode_name"),
                "emotional_tone": ep.get("emotional_tone"),
                "narrative_arc": ep.get("narrative_arc"),
            }

    prompt = build_generation_prompt(chapter_text, num_questions, chapter_title, episode_metadata)

    try:
        raw = call_llm(prompt, system=SYSTEM_PROMPT)
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return {"run_id": run_id, "questions": [], "error": f"LLM call failed: {e}"}

    try:
        questions = parse_questions(raw)
    except ValueError as e:
        logger.error("Parse failed, retrying once: %s", e)
        retry_prompt = prompt + "\n\nCRITICAL: Return ONLY {\"questions\": [...]}. No other text."
        try:
            raw = call_llm(retry_prompt, system=SYSTEM_PROMPT)
            questions = parse_questions(raw)
        except Exception as e2:
            logger.error("Retry also failed: %s", e2)
            return {"run_id": run_id, "questions": [], "error": f"Parse failed after retry: {e2}"}

    questions = _normalize_fields(questions)

    validation_results = _validate_questions(chapter_text, questions)
    if validation_results:
        questions = _merge_validation(questions, validation_results)
        approved_count = sum(1 for v in validation_results if v.get("status") == "approved")
        logger.info("Grounding: %d/%d passed", approved_count, len(questions))

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
