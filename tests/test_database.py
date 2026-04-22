import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use a temp DB for tests
TEST_DB = tempfile.mktemp(suffix=".db")
os.environ["DB_PATH"] = TEST_DB
os.environ["ANTHROPIC_API_KEY"] = "test-key-placeholder"

from src import database as db
db.DB_PATH = TEST_DB


def setup_function():
    db.DB_PATH = TEST_DB
    db.init_db()


def teardown_function():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


SAMPLE_QUESTION = {
    "question": "Who is the protagonist of Mahabharata?",
    "option_a": "Arjuna",
    "option_b": "Karna",
    "option_c": "Duryodhana",
    "option_d": "Bhishma",
    "correct_answer": "A",
    "explanation": "Arjuna is the central hero.",
    "difficulty": "easy",
    "topic": "Characters",
}


def test_insert_and_get_draft():
    run_id = db.insert_generation_run("Test Chapter", "Sample text", 1)
    assert run_id > 0

    ids = db.insert_draft_questions(run_id, [SAMPLE_QUESTION])
    assert len(ids) == 1

    pending = db.get_pending_drafts()
    assert len(pending) == 1
    assert pending[0]["question"] == SAMPLE_QUESTION["question"]


def test_approve_question():
    run_id = db.insert_generation_run("Test Chapter", "Sample text", 1)
    ids = db.insert_draft_questions(run_id, [SAMPLE_QUESTION])
    draft_id = ids[0]

    db.approve_question(draft_id)

    pending = db.get_pending_drafts()
    assert len(pending) == 0

    approved = db.get_approved_questions()
    assert len(approved) == 1
    assert approved[0]["draft_id"] == draft_id


def test_reject_question():
    run_id = db.insert_generation_run("Test Chapter", "Sample text", 1)
    ids = db.insert_draft_questions(run_id, [SAMPLE_QUESTION])
    draft_id = ids[0]

    db.reject_question(draft_id)

    pending = db.get_pending_drafts()
    assert len(pending) == 0

    approved = db.get_approved_questions()
    assert len(approved) == 0


def test_approve_with_edit():
    run_id = db.insert_generation_run("Test Chapter", "Sample text", 1)
    ids = db.insert_draft_questions(run_id, [SAMPLE_QUESTION])
    draft_id = ids[0]

    edited = {"question": "EDITED QUESTION", "correct_answer": "B"}
    db.approve_question(draft_id, edited)

    approved = db.get_approved_questions()
    assert approved[0]["question"] == "EDITED QUESTION"
    assert approved[0]["correct_answer"] == "B"


def test_stats():
    run_id = db.insert_generation_run("Test Chapter", "Sample text", 2)
    q1 = {**SAMPLE_QUESTION}
    q2 = {**SAMPLE_QUESTION, "question": "Second question?"}
    ids = db.insert_draft_questions(run_id, [q1, q2])

    db.approve_question(ids[0])
    db.reject_question(ids[1])

    stats = db.get_stats()
    assert stats["approved"] == 1
    assert stats["rejected"] == 1
    assert stats["pending"] == 0


def test_filter_approved_by_difficulty():
    run_id = db.insert_generation_run("Test", "Text", 2)
    easy_q = {**SAMPLE_QUESTION, "difficulty": "easy"}
    hard_q = {**SAMPLE_QUESTION, "question": "Hard question?", "difficulty": "hard"}
    ids = db.insert_draft_questions(run_id, [easy_q, hard_q])
    db.approve_question(ids[0])
    db.approve_question(ids[1])

    easy = db.get_approved_questions(difficulty="easy")
    hard = db.get_approved_questions(difficulty="hard")
    assert len(easy) == 1
    assert len(hard) == 1
