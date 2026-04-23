import json
import re
from pydantic import BaseModel, field_validator, ValidationError
from src.logger import get_logger

logger = get_logger("parser")

VALID_ANSWERS = {"A", "B", "C", "D"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


class QuestionSchema(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str = ""

    @field_validator("correct_answer")
    @classmethod
    def validate_answer(cls, v):
        v = v.strip().upper()
        if v not in VALID_ANSWERS:
            raise ValueError(f"correct_answer must be one of {VALID_ANSWERS}, got '{v}'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        v = v.strip().lower()
        if v not in VALID_DIFFICULTIES:
            raise ValueError(f"difficulty must be one of {VALID_DIFFICULTIES}, got '{v}'")
        return v

    @field_validator("question", "option_a", "option_b", "option_c", "option_d", "explanation")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


def _strip_markdown(raw: str) -> str:
    raw = re.sub(r"```(?:json)?", "", raw)
    return raw.strip()


def _extract_array(raw: str) -> list:
    """
    Handles three response shapes:
      1. {"questions": [...]}   — OpenAI json_object mode
      2. [...]                  — bare array
      3. {...single object...}  — single question object
    """
    raw = _strip_markdown(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("JSON decode failed: %s\nRaw snippet: %s", e, raw[:300])
        raise ValueError(f"Invalid JSON: {e}") from e

    if isinstance(data, dict):
        # OpenAI json_object wrapper
        for key in ("questions", "items", "results", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # Single question dict
        return [data]

    if isinstance(data, list):
        return data

    raise ValueError(f"Unexpected JSON shape: {type(data)}")


def parse_questions(raw: str) -> list[dict]:
    logger.info("Parsing LLM response, length=%d", len(raw))

    items = _extract_array(raw)

    parsed = []
    for i, item in enumerate(items):
        try:
            q = QuestionSchema(**item)
            parsed.append(q.model_dump())
            logger.info("Question %d validated OK", i + 1)
        except (ValidationError, TypeError) as e:
            logger.warning("Question %d failed validation, skipping: %s", i + 1, e)

    logger.info("Parsed %d/%d questions successfully", len(parsed), len(items))

    if not parsed:
        raise ValueError("All questions failed validation")

    return parsed
