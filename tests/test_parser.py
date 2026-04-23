import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.parser import parse_questions

# OpenAI json_object wrapper shape
WRAPPED_JSON = """{
  "questions": [
    {
      "question": "Who was Arjuna's charioteer at Kurukshetra?",
      "option_a": "Bhima",
      "option_b": "Krishna",
      "option_c": "Drona",
      "option_d": "Karna",
      "correct_answer": "B",
      "explanation": "Krishna served as Arjuna's charioteer at Kurukshetra.",
      "difficulty": "easy",
      "topic": "Mahabharata"
    }
  ]
}"""

# Bare array (fallback shape)
BARE_ARRAY = """[
  {
    "question": "What was Arjuna's bow called?",
    "option_a": "Sharanga",
    "option_b": "Pinaka",
    "option_c": "Gandiva",
    "option_d": "Vijaya",
    "correct_answer": "C",
    "explanation": "Arjuna's bow was named Gandiva.",
    "difficulty": "medium",
    "topic": "Weapons"
  }
]"""

# Markdown fenced
MARKDOWN_WRAPPED = """```json
{
  "questions": [
    {
      "question": "What weapon did Arjuna use?",
      "option_a": "Sudarshana",
      "option_b": "Pashupatastra",
      "option_c": "Gandiva",
      "option_d": "Brahmastra",
      "correct_answer": "C",
      "explanation": "Arjuna wielded the Gandiva bow.",
      "difficulty": "medium",
      "topic": "Weapons"
    }
  ]
}
```"""

INVALID_JSON = "Here are some questions: blah blah blah"

BAD_ANSWER = """{
  "questions": [
    {
      "question": "Test?",
      "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
      "correct_answer": "E",
      "explanation": "Bad answer key.",
      "difficulty": "easy",
      "topic": "Test"
    }
  ]
}"""

MIXED = """{
  "questions": [
    {
      "question": "Valid question?",
      "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
      "correct_answer": "A",
      "explanation": "Valid explanation.",
      "difficulty": "hard",
      "topic": "Test"
    },
    {
      "question": "Invalid difficulty?",
      "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D",
      "correct_answer": "A",
      "explanation": "Bad difficulty.",
      "difficulty": "super-hard",
      "topic": "Test"
    }
  ]
}"""


def test_wrapped_json():
    result = parse_questions(WRAPPED_JSON)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "B"


def test_bare_array():
    result = parse_questions(BARE_ARRAY)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "C"


def test_markdown_stripped():
    result = parse_questions(MARKDOWN_WRAPPED)
    assert len(result) == 1
    assert result[0]["correct_answer"] == "C"


def test_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_questions(INVALID_JSON)


def test_bad_answer_raises():
    with pytest.raises(ValueError, match="All questions failed validation"):
        parse_questions(BAD_ANSWER)


def test_mixed_skips_invalid():
    result = parse_questions(MIXED)
    assert len(result) == 1
    assert result[0]["difficulty"] == "hard"


def test_difficulty_case_normalized():
    data = """{
      "questions": [{
        "question": "Q?", "option_a": "A", "option_b": "B",
        "option_c": "C", "option_d": "D", "correct_answer": "A",
        "explanation": "E.", "difficulty": "EASY", "topic": "T"
      }]
    }"""
    result = parse_questions(data)
    assert result[0]["difficulty"] == "easy"


def test_correct_answer_case_normalized():
    data = """{
      "questions": [{
        "question": "Q?", "option_a": "A", "option_b": "B",
        "option_c": "C", "option_d": "D", "correct_answer": "b",
        "explanation": "E.", "difficulty": "easy", "topic": "T"
      }]
    }"""
    result = parse_questions(data)
    assert result[0]["correct_answer"] == "B"
