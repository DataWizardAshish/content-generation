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
    episode_id INTEGER REFERENCES episodes(id),
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
    story_phase TEXT,
    narrative_arc TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    validation_status TEXT DEFAULT 'unvalidated',
    validation_reason TEXT,
    validation_supporting_text TEXT,
    confidence_score INTEGER,
    engagement_score INTEGER,
    engagement_reason TEXT,
    is_daily_insight INTEGER DEFAULT 0,
    improvement_suggestion TEXT,
    episode_id INTEGER REFERENCES episodes(id),
    sequence_in_episode INTEGER,
    scene_setup TEXT,
    narrative_continuation TEXT,
    deep_context TEXT,
    forward_hook TEXT,
    enrichment_score INTEGER,
    narrative_flow_score INTEGER,
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
    story_phase TEXT,
    narrative_arc TEXT,
    chapter_title TEXT,
    engagement_score INTEGER,
    is_daily_insight INTEGER DEFAULT 0,
    episode_id INTEGER REFERENCES episodes(id),
    sequence_in_episode INTEGER,
    scene_setup TEXT,
    narrative_continuation TEXT,
    deep_context TEXT,
    forward_hook TEXT,
    enrichment_score INTEGER,
    narrative_flow_score INTEGER,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY,
    sequence_number INTEGER NOT NULL UNIQUE,
    episode_name TEXT NOT NULL,
    kanda TEXT NOT NULL,
    sarga_start INTEGER NOT NULL,
    sarga_end INTEGER NOT NULL,
    story_phase TEXT NOT NULL,
    episode_subtitle TEXT,
    narrative_arc TEXT,
    emotional_tone TEXT,
    key_characters TEXT,
    opening_text TEXT,
    closing_text TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS saved_questions (
    id INTEGER PRIMARY KEY,
    device_id TEXT NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions_approved(id),
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_note TEXT,
    UNIQUE(device_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_saved_device ON saved_questions(device_id);

CREATE TABLE IF NOT EXISTS daily_shlokas (
    id INTEGER PRIMARY KEY,
    sequence_number INTEGER UNIQUE NOT NULL,
    sanskrit_devanagari TEXT NOT NULL,
    sanskrit_transliteration TEXT NOT NULL,
    translation_en TEXT NOT NULL,
    translation_hi TEXT,
    meaning_context TEXT NOT NULL,
    source_kanda TEXT,
    source_sarga INTEGER,
    source_verse TEXT,
    theme TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY,
    device_id TEXT UNIQUE NOT NULL,
    questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    weekly_active_days INTEGER DEFAULT 0,
    last_active_date DATE,
    current_episode_id INTEGER REFERENCES episodes(id),
    farthest_episode_id INTEGER REFERENCES episodes(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_episode_progress (
    id INTEGER PRIMARY KEY,
    device_id TEXT NOT NULL,
    episode_id INTEGER NOT NULL REFERENCES episodes(id),
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    UNIQUE(device_id, episode_id)
);
CREATE INDEX IF NOT EXISTS idx_episode_progress_device ON user_episode_progress(device_id);

CREATE TABLE IF NOT EXISTS story_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    narrative TEXT NOT NULL,
    lesson TEXT NOT NULL,
    story_phase TEXT,
    character TEXT,
    sequence_number INTEGER UNIQUE NOT NULL,
    insight_date DATE,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS phase_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_phase TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    narrative TEXT NOT NULL,
    key_events TEXT NOT NULL,
    key_characters TEXT NOT NULL,
    mood TEXT NOT NULL,
    shloka_watermark TEXT,
    is_active INTEGER DEFAULT 1
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
        _migrate(conn)
    from src.episodes_data import EPISODES
    seed_episodes(EPISODES)
    from src.insights_data import INSIGHTS, PHASE_STORIES
    seed_insights(INSIGHTS)
    seed_phase_stories(PHASE_STORIES)
    logger.info("Database initialized at %s", DB_PATH)


def _migrate(conn: sqlite3.Connection):
    draft_cols = {row[1] for row in conn.execute("PRAGMA table_info(questions_draft)")}
    for col, definition in [
        ("validation_status", "TEXT DEFAULT 'unvalidated'"),
        ("validation_reason", "TEXT"),
        ("validation_supporting_text", "TEXT"),
        ("confidence_score", "INTEGER"),
        ("story_phase", "TEXT"),
        ("narrative_arc", "TEXT"),
        ("engagement_score", "INTEGER"),
        ("engagement_reason", "TEXT"),
        ("is_daily_insight", "INTEGER DEFAULT 0"),
        ("improvement_suggestion", "TEXT"),
        ("episode_id", "INTEGER"),
        ("sequence_in_episode", "INTEGER"),
        ("scene_setup", "TEXT"),
        ("narrative_continuation", "TEXT"),
        ("deep_context", "TEXT"),
        ("forward_hook", "TEXT"),
        ("enrichment_score", "INTEGER"),
        ("narrative_flow_score", "INTEGER"),
    ]:
        if col not in draft_cols:
            conn.execute(f"ALTER TABLE questions_draft ADD COLUMN {col} {definition}")
            logger.info("Migration: added questions_draft.%s", col)

    approved_cols = {row[1] for row in conn.execute("PRAGMA table_info(questions_approved)")}
    for col, definition in [
        ("story_phase", "TEXT"),
        ("narrative_arc", "TEXT"),
        ("engagement_score", "INTEGER"),
        ("is_daily_insight", "INTEGER DEFAULT 0"),
        ("episode_id", "INTEGER"),
        ("sequence_in_episode", "INTEGER"),
        ("scene_setup", "TEXT"),
        ("narrative_continuation", "TEXT"),
        ("deep_context", "TEXT"),
        ("forward_hook", "TEXT"),
        ("enrichment_score", "INTEGER"),
        ("narrative_flow_score", "INTEGER"),
    ]:
        if col not in approved_cols:
            conn.execute(f"ALTER TABLE questions_approved ADD COLUMN {col} {definition}")
            logger.info("Migration: added questions_approved.%s", col)

    runs_cols = {row[1] for row in conn.execute("PRAGMA table_info(generation_runs)")}
    if "episode_id" not in runs_cols:
        conn.execute("ALTER TABLE generation_runs ADD COLUMN episode_id INTEGER")
        logger.info("Migration: added generation_runs.episode_id")

    conn.execute("""CREATE TABLE IF NOT EXISTS story_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        narrative TEXT NOT NULL,
        lesson TEXT NOT NULL,
        story_phase TEXT,
        character TEXT,
        sequence_number INTEGER UNIQUE NOT NULL,
        insight_date DATE,
        is_active INTEGER DEFAULT 1
    )""")
    insight_cols = {row[1] for row in conn.execute("PRAGMA table_info(story_insights)")}
    if "insight_date" not in insight_cols:
        conn.execute("ALTER TABLE story_insights ADD COLUMN insight_date DATE")
        logger.info("Migration: added story_insights.insight_date")

    conn.execute("""CREATE TABLE IF NOT EXISTS phase_stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_phase TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        narrative TEXT NOT NULL,
        key_events TEXT NOT NULL,
        key_characters TEXT NOT NULL,
        mood TEXT NOT NULL,
        shloka_watermark TEXT,
        is_active INTEGER DEFAULT 1
    )""")
    phase_cols = {row[1] for row in conn.execute("PRAGMA table_info(phase_stories)")}
    if "shloka_watermark" not in phase_cols:
        conn.execute("ALTER TABLE phase_stories ADD COLUMN shloka_watermark TEXT")
        logger.info("Migration: added phase_stories.shloka_watermark")


# ── Episodes ──────────────────────────────────────────────────────────────────

def seed_episodes(episodes: list[dict]):
    with transaction() as conn:
        for ep in episodes:
            conn.execute(
                """INSERT OR IGNORE INTO episodes
                   (sequence_number, episode_name, kanda, sarga_start, sarga_end, story_phase)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (ep["sequence_number"], ep["episode_name"], ep["kanda"],
                 ep["sarga_start"], ep["sarga_end"], ep["story_phase"]),
            )
    logger.info("Episodes seeded: %d rows", len(episodes))


def get_episodes() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT e.*, COUNT(q.id) as question_count
               FROM episodes e
               LEFT JOIN questions_approved q ON q.episode_id = e.id
               WHERE e.is_active = 1
               GROUP BY e.id
               ORDER BY e.sequence_number"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_episode(episode_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT e.*, COUNT(q.id) as question_count
               FROM episodes e
               LEFT JOIN questions_approved q ON q.episode_id = e.id
               WHERE e.id = ?
               GROUP BY e.id""",
            (episode_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_episode_questions(episode_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM questions_approved
               WHERE episode_id = ?
               ORDER BY COALESCE(sequence_in_episode, id)""",
            (episode_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Generation ────────────────────────────────────────────────────────────────

def insert_generation_run(
    chapter_title: str,
    chapter_text: str,
    num_requested: int,
    episode_id: int | None = None,
) -> int:
    with transaction() as conn:
        cur = conn.execute(
            "INSERT INTO generation_runs (chapter_title, chapter_text, num_requested, episode_id) VALUES (?, ?, ?, ?)",
            (chapter_title, chapter_text, num_requested, episode_id),
        )
        run_id = cur.lastrowid
    logger.info("Created generation run id=%d episode_id=%s", run_id, episode_id)
    return run_id


def insert_draft_questions(run_id: int, questions: list[dict], episode_id: int | None = None) -> list[int]:
    ids = []
    with transaction() as conn:
        ep_id = episode_id
        if ep_id is None:
            row = conn.execute("SELECT episode_id FROM generation_runs WHERE id=?", (run_id,)).fetchone()
            if row:
                ep_id = row[0]
        for q in questions:
            cur = conn.execute(
                """INSERT INTO questions_draft
                   (run_id, question, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, difficulty, topic, story_phase, narrative_arc,
                    validation_status, validation_reason, validation_supporting_text, confidence_score,
                    engagement_score, engagement_reason, is_daily_insight, improvement_suggestion,
                    episode_id, scene_setup, narrative_continuation, deep_context, forward_hook,
                    enrichment_score, narrative_flow_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    q["question"], q["option_a"], q["option_b"], q["option_c"], q["option_d"],
                    q["correct_answer"], q.get("explanation", ""), q["difficulty"],
                    q.get("topic", ""), q.get("story_phase", ""), q.get("narrative_arc", ""),
                    q.get("validation_status", "unvalidated"), q.get("validation_reason", ""),
                    q.get("validation_supporting_text", ""), q.get("confidence_score"),
                    q.get("engagement_score"), q.get("engagement_reason", ""),
                    1 if q.get("is_daily_insight") else 0, q.get("improvement_suggestion", ""),
                    ep_id,
                    q.get("scene_setup"), q.get("narrative_continuation"),
                    q.get("deep_context"), q.get("forward_hook"),
                    q.get("enrichment_score"), q.get("narrative_flow_score"),
                ),
            )
            ids.append(cur.lastrowid)
        conn.execute("UPDATE generation_runs SET num_generated=? WHERE id=?", (len(ids), run_id))
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
                correct_answer, explanation, difficulty, topic, story_phase, narrative_arc,
                chapter_title, engagement_score, is_daily_insight, episode_id,
                scene_setup, narrative_continuation, deep_context, forward_hook,
                enrichment_score, narrative_flow_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                draft_id,
                data["question"], data["option_a"], data["option_b"],
                data["option_c"], data["option_d"], data["correct_answer"],
                data.get("explanation", ""), data["difficulty"],
                data.get("topic", ""), data.get("story_phase", ""), data.get("narrative_arc", ""),
                data.get("chapter_title", ""), data.get("engagement_score"),
                1 if data.get("is_daily_insight") else 0,
                data.get("episode_id"),
                data.get("scene_setup"), data.get("narrative_continuation"),
                data.get("deep_context"), data.get("forward_hook"),
                data.get("enrichment_score"), data.get("narrative_flow_score"),
            ),
        )
        conn.execute("UPDATE questions_draft SET status='approved' WHERE id=?", (draft_id,))
    logger.info("Approved draft_id=%d", draft_id)


def reject_question(draft_id: int):
    with transaction() as conn:
        conn.execute("UPDATE questions_draft SET status='rejected' WHERE id=?", (draft_id,))
    logger.info("Rejected draft_id=%d", draft_id)


def get_approved_questions(
    topic: str = "",
    difficulty: str = "",
    chapter: str = "",
    episode_id: int | None = None,
) -> list[dict]:
    conn = get_connection()
    try:
        query = "SELECT * FROM questions_approved WHERE 1=1"
        params: list = []
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if chapter:
            query += " AND chapter_title = ?"
            params.append(chapter)
        if episode_id is not None:
            query += " AND episode_id = ?"
            params.append(episode_id)
        query += " ORDER BY approved_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_approved_question(approved_id: int):
    with transaction() as conn:
        conn.execute("DELETE FROM questions_approved WHERE id=?", (approved_id,))
    logger.info("Deleted approved question id=%d", approved_id)


def get_library_filter_options() -> dict:
    conn = get_connection()
    try:
        topics = [r[0] for r in conn.execute(
            "SELECT DISTINCT topic FROM questions_approved WHERE topic IS NOT NULL AND topic != '' ORDER BY topic"
        ).fetchall()]
        chapters = [r[0] for r in conn.execute(
            "SELECT DISTINCT chapter_title FROM questions_approved WHERE chapter_title IS NOT NULL AND chapter_title != '' ORDER BY chapter_title"
        ).fetchall()]
        return {"topics": topics, "chapters": chapters}
    finally:
        conn.close()


def get_stats() -> dict:
    conn = get_connection()
    try:
        pending = conn.execute("SELECT COUNT(*) FROM questions_draft WHERE status='pending'").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM questions_approved").fetchone()[0]
        rejected = conn.execute("SELECT COUNT(*) FROM questions_draft WHERE status='rejected'").fetchone()[0]
        runs = conn.execute("SELECT COUNT(*) FROM generation_runs").fetchone()[0]
        return {"pending": pending, "approved": approved, "rejected": rejected, "runs": runs}
    finally:
        conn.close()


# ── Saved questions ───────────────────────────────────────────────────────────

def save_question(device_id: str, question_id: int, user_note: str | None = None) -> dict:
    with transaction() as conn:
        conn.execute(
            """INSERT INTO saved_questions (device_id, question_id, user_note)
               VALUES (?, ?, ?)
               ON CONFLICT(device_id, question_id) DO UPDATE SET user_note=excluded.user_note, saved_at=CURRENT_TIMESTAMP""",
            (device_id, question_id, user_note),
        )
        row = conn.execute(
            "SELECT * FROM saved_questions WHERE device_id=? AND question_id=?",
            (device_id, question_id),
        ).fetchone()
    return dict(row)


def unsave_question(device_id: str, question_id: int):
    with transaction() as conn:
        conn.execute(
            "DELETE FROM saved_questions WHERE device_id=? AND question_id=?",
            (device_id, question_id),
        )


def get_saved_questions(device_id: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT s.id as saved_id, s.saved_at, s.user_note, q.*
               FROM saved_questions s
               JOIN questions_approved q ON s.question_id = q.id
               WHERE s.device_id = ?
               ORDER BY s.saved_at DESC""",
            (device_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Daily shlokas ─────────────────────────────────────────────────────────────

def get_active_shlokas() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM daily_shlokas WHERE is_active=1 ORDER BY sequence_number"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_shloka_by_index(index: int) -> dict | None:
    shlokas = get_active_shlokas()
    if not shlokas:
        return None
    return shlokas[index % len(shlokas)]


# ── Story insights ────────────────────────────────────────────────────────────

def get_active_insights() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM story_insights WHERE is_active=1 ORDER BY sequence_number"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_insight_by_index(index: int) -> dict | None:
    insights = get_active_insights()
    if not insights:
        return None
    return insights[index % len(insights)]


def get_or_create_todays_insight(llm_generate_fn) -> dict | None:
    import datetime
    today = datetime.date.today()
    today_str = today.isoformat()

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM story_insights WHERE insight_date = ? AND is_active = 1 LIMIT 1",
            (today_str,),
        ).fetchone()
        if row:
            return dict(row)
    finally:
        conn.close()

    try:
        generated = llm_generate_fn()
        if generated:
            seq = today.year * 10000 + today.timetuple().tm_yday
            with transaction() as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO story_insights
                       (title, narrative, lesson, story_phase, character, sequence_number, insight_date, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                    (
                        generated["title"], generated["narrative"], generated["lesson"],
                        generated.get("story_phase"), generated.get("character"),
                        seq, today_str,
                    ),
                )
            conn2 = get_connection()
            try:
                row = conn2.execute(
                    "SELECT * FROM story_insights WHERE insight_date = ? AND is_active = 1 LIMIT 1",
                    (today_str,),
                ).fetchone()
                if row:
                    return dict(row)
            finally:
                conn2.close()
    except Exception as e:
        logger.error("LLM insight generation failed, falling back to seeds: %s", e)

    day_index = today.timetuple().tm_yday
    return get_insight_by_index(day_index)


def seed_insights(insights: list[dict]):
    with transaction() as conn:
        for row in insights:
            conn.execute(
                """INSERT OR IGNORE INTO story_insights
                   (sequence_number, title, narrative, lesson, story_phase, character)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (row["sequence_number"], row["title"], row["narrative"],
                 row["lesson"], row.get("story_phase"), row.get("character")),
            )
    logger.info("Story insights seeded: %d rows", len(insights))


# ── Phase stories ─────────────────────────────────────────────────────────────

def get_phase_stories() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM phase_stories WHERE is_active=1 ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_phase_story(story_phase: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM phase_stories WHERE story_phase=?", (story_phase,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def seed_phase_stories(stories: list[dict]):
    with transaction() as conn:
        for row in stories:
            conn.execute(
                """INSERT OR IGNORE INTO phase_stories
                   (story_phase, title, narrative, key_events, key_characters, mood, shloka_watermark)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (row["story_phase"], row["title"], row["narrative"],
                 row["key_events"], row["key_characters"], row["mood"],
                 row.get("shloka_watermark")),
            )
            if row.get("shloka_watermark"):
                conn.execute(
                    "UPDATE phase_stories SET shloka_watermark=? WHERE story_phase=? AND shloka_watermark IS NULL",
                    (row["shloka_watermark"], row["story_phase"]),
                )
    logger.info("Phase stories seeded: %d rows", len(stories))


# ── User progress ─────────────────────────────────────────────────────────────

def get_user_progress(device_id: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM user_progress WHERE device_id=?", (device_id,)
        ).fetchone()
        if row:
            return dict(row)
        return {
            "device_id": device_id, "questions_answered": 0, "questions_correct": 0,
            "current_streak_days": 0, "longest_streak_days": 0, "weekly_active_days": 0,
            "last_active_date": None, "current_episode_id": 1, "farthest_episode_id": 1,
        }
    finally:
        conn.close()


def upsert_user_progress(device_id: str, **fields) -> dict:
    with transaction() as conn:
        existing = conn.execute(
            "SELECT * FROM user_progress WHERE device_id=?", (device_id,)
        ).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in fields)
            set_clause += ", updated_at=CURRENT_TIMESTAMP"
            conn.execute(
                f"UPDATE user_progress SET {set_clause} WHERE device_id=?",
                [*fields.values(), device_id],
            )
        else:
            conn.execute(
                "INSERT INTO user_progress (device_id) VALUES (?)", (device_id,)
            )
            if fields:
                set_clause = ", ".join(f"{k}=?" for k in fields)
                set_clause += ", updated_at=CURRENT_TIMESTAMP"
                conn.execute(
                    f"UPDATE user_progress SET {set_clause} WHERE device_id=?",
                    [*fields.values(), device_id],
                )
        row = conn.execute("SELECT * FROM user_progress WHERE device_id=?", (device_id,)).fetchone()
    return dict(row)


def record_answer(device_id: str, question_id: int, was_correct: bool, time_taken_seconds: int | None = None) -> dict:
    conn = get_connection()
    try:
        q_row = conn.execute(
            "SELECT episode_id FROM questions_approved WHERE id=?", (question_id,)
        ).fetchone()
        ep_id = q_row["episode_id"] if q_row else None
    finally:
        conn.close()

    progress = get_user_progress(device_id)

    import datetime
    from services.streak import calculate_streak, calculate_weekly_active
    today = datetime.date.today()
    last_active = progress.get("last_active_date")
    if isinstance(last_active, str):
        try:
            last_active = datetime.date.fromisoformat(last_active)
        except ValueError:
            last_active = None

    new_streak = calculate_streak(last_active, progress["current_streak_days"])
    new_longest = max(new_streak, progress["longest_streak_days"])

    updates = {
        "questions_answered": progress["questions_answered"] + 1,
        "questions_correct": progress["questions_correct"] + (1 if was_correct else 0),
        "current_streak_days": new_streak,
        "longest_streak_days": new_longest,
        "last_active_date": today.isoformat(),
    }
    if ep_id:
        updates["current_episode_id"] = ep_id
        farthest = progress.get("farthest_episode_id") or 1
        if ep_id >= farthest:
            updates["farthest_episode_id"] = ep_id

    upsert_user_progress(device_id, **updates)

    # update per-episode progress
    if ep_id:
        with transaction() as conn:
            conn.execute(
                """INSERT INTO user_episode_progress (device_id, episode_id, questions_attempted, questions_correct)
                   VALUES (?, ?, 1, ?)
                   ON CONFLICT(device_id, episode_id) DO UPDATE SET
                     questions_attempted=questions_attempted+1,
                     questions_correct=questions_correct+?""",
                (device_id, ep_id, 1 if was_correct else 0, 1 if was_correct else 0),
            )

    return get_user_progress(device_id)


def get_user_episode_progress(device_id: str) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM user_episode_progress WHERE device_id=? ORDER BY episode_id",
            (device_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
