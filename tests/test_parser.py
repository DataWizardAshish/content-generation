import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.parser import parse_questions


VALID_JSON = """[
  {
    "question": "Who was Arjuna's charioteer?",
    "option_a": "Bhima",
    "option_b": "Krishna",
    "option_c": "Drona",
    "option_d": "Karna",
    "correct_answer": "B",
    "explanation": "Krishna served as Arjuna's charioteer at Kurukshetra.",
    "difficulty": "easy",
    "topic": "Mahabharata"
  }
]"""

MARKDOWN_WRAPPED = """```json
[
  {
    "question": "What was the name of Arjuna's bow?",
    "option_a": "Sharanga",
    "option_b": "Pinaka",
    "option_c": "Gandiva",
    "option_d": "Vijaya",
    "correct_answer": "C",
    "explanation": "Arjuna's bow was called Gandiva.",
    "difficulty": "medium",
    "topic": "Weapons"
  }
]
```"""

INVALID_JSON = "Here are some questions: blah blah blah no json here"

BAD_ANSWER = """[
  {
    "question": "Test?",
    "option_a": "A",
    "option_b": "B",
    "option_c": "C",
    "option_d": "D",
    "correct_answer": "E",
    "explanation": "Test.",
    "difficulty": "easy",
    "topic": "Test"
  }
]"""


def test_valid_json():
    result = parse_questions(VALID_JSON)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "B"
    assert result[0]["difficulty"] == "easy"


def test_markdown_wrapped_json():
    result = parse_questions(MARKDOWN_WRAPPED)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "C"


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_questions(INVALID_JSON)


def test_bad_answer_skipped():
    with pytest.raises(ValueError, match="All questions failed validation"):
        parse_questions(BAD_ANSWER)


def test_mixed_valid_invalid():
    mixed = """[
      {
        "question": "Valid question?",
        "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
        "correct_answer": "A",
        "explanation": "Valid.",
        "difficulty": "hard",
        "topic": "Test"
      },
      {
        "question": "Invalid - bad difficulty",
        "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
        "correct_answer": "A",
        "explanation": "Bad.",
        "difficulty": "super-hard",
        "topic": "Test"
      }
    ]"""
    result = parse_questions(mixed)
    assert len(result) == 1
    assert result[0]["difficulty"] == "hard"
