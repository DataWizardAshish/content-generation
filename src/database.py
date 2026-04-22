import sqlite3
import contextlib
from src.config import DB_PATH
from src.logger import get_logger

logger = get_logger("database")

SCHEMA = """
CREATE TABLE IF NOT EXISTS generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_title TEXT,
    chapter_text TEXT NOT NULL,
    num_requested INTEGER NOT NULL,
    num_generated INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions_draft (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES generation_runs(id),
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy','medium','hard')),
    topic TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions_approved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id INTEGER REFERENCES questions_draft(id),
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy','medium','hard')),
    topic TEXT,
    chapter_title TEXT,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextlib.contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with transaction() as conn:
        conn.executescript(SCHEMA)
    logger.info("Database initialized at %s", DB_PATH)


def insert_generation_run(chapter_title: str, chapter_text: str, num_requested: int) -> int:
    with transaction() as conn:
        cur = conn.execute(
            "INSERT INTO generation_runs (chapter_title, chapter_text, num_requested) VALUES (?, ?, ?)",
            (chapter_title, chapter_text, num_requested),
        )
        run_id = cur.lastrowid
    logger.info("Created generation run id=%d", run_id)
    return run_id


def insert_draft_questions(run_id: int, questions: list[dict]) -> list[int]:
    ids = []
    with transaction() as conn:
        for q in questions:
            cur = conn.execute(
                """INSERT INTO questions_draft
                   (run_id, question, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, difficulty, topic)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    q["question"],
                    q["option_a"],
                    q["option_b"],
                    q["option_c"],
                    q["option_d"],
                    q["correct_answer"],
                    q["explanation"],
                    q["difficulty"],
                    q.get("topic", ""),
                ),
            )
            ids.append(cur.lastrowid)
        conn.execute(
            "UPDATE generation_runs SET num_generated=? WHERE id=?",
            (len(ids), run_id),
        )
    logger.info("Inserted %d draft questions for run_id=%d", len(ids), run_id)
    return ids


def get_pending_drafts() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT d.*, r.chapter_title FROM questions_draft d
               LEFT JOIN generation_runs r ON d.run_id = r.id
               WHERE d.status = 'pending'
               ORDER BY d.created_at ASC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def approve_question(draft_id: int, edited: dict | None = None):
    with transaction() as conn:
        row = dict(conn.execute(
            """SELECT d.*, r.chapter_title FROM questions_draft d
               LEFT JOIN generation_runs r ON d.run_id = r.id
               WHERE d.id = ?""",
            (draft_id,),
        ).fetchone())

        data = {**row, **(edited or {})}

        conn.execute(
            """INSERT INTO questions_approved
               (draft_id, question, option_a, option_b, option_c, option_d,
                correct_answer, explanation, difficulty, topic, chapter_title)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                draft_id,
                data["question"],
                data["option_a"],
                data["option_b"],
                data["option_c"],
                data["option_d"],
                data["correct_answer"],
                data["explanation"],
                data["difficulty"],
                data.get("topic", ""),
                data.get("chapter_title", ""),
            ),
        )
        conn.execute(
            "UPDATE questions_draft SET status='approved' WHERE id=?", (draft_id,)
        )
    logger.info("Approved draft_id=%d", draft_id)


def reject_question(draft_id: int):
    with transaction() as conn:
        conn.execute(
            "UPDATE questions_draft SET status='rejected' WHERE id=?", (draft_id,)
        )
    logger.info("Rejected draft_id=%d", draft_id)


def get_approved_questions(topic: str = "", difficulty: str = "") -> list[dict]:
    conn = get_connection()
    try:
        query = "SELECT * FROM questions_approved WHERE 1=1"
        params = []
        if topic:
            query += " AND topic LIKE ?"
            params.append(f"%{topic}%")
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        query += " ORDER BY approved_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_stats() -> dict:
    conn = get_connection()
    try:
        pending = conn.execute(
            "SELECT COUNT(*) FROM questions_draft WHERE status='pending'"
        ).fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM questions_approved"
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM questions_draft WHERE status='rejected'"
        ).fetchone()[0]
        runs = conn.execute(
            "SELECT COUNT(*) FROM generation_runs"
        ).fetchone()[0]
        return {"pending": pending, "approved": approved, "rejected": rejected, "runs": runs}
    finally:
        conn.close()
