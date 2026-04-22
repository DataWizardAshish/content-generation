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


def _extract_json(raw: str) -> str:
    # Try to find JSON array in the response
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        return match.group(0)
    # Try JSON object wrapped in array
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return f"[{match.group(0)}]"
    raise ValueError("No JSON array found in LLM response")


def parse_questions(raw: str) -> list[dict]:
    logger.info("Parsing LLM response, length=%d", len(raw))

    try:
        json_str = _extract_json(raw)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("JSON extraction failed: %s\nRaw: %s", e, raw[:500])
        raise ValueError(f"Failed to parse JSON from LLM response: {e}") from e

    if not isinstance(data, list):
        data = [data]

    parsed = []
    for i, item in enumerate(data):
        try:
            q = QuestionSchema(**item)
            parsed.append(q.model_dump())
            logger.info("Question %d validated OK", i + 1)
        except (ValidationError, TypeError) as e:
            logger.warning("Question %d failed validation, skipping: %s", i + 1, e)

    logger.info("Parsed %d/%d questions successfully", len(parsed), len(data))

    if not parsed:
        raise ValueError("All questions failed validation")

    return parsed
