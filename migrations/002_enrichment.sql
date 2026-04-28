-- Migration 002: Enrichment features for SHRUTI
-- Run once: python -c "import sqlite3; conn=sqlite3.connect('questions.db'); conn.executescript(open('migrations/002_enrichment.sql').read())"
-- All statements are additive — no existing columns or tables are modified.

-- ── Enrichment columns on questions_approved ─────────────────────────────────
ALTER TABLE questions_approved ADD COLUMN episode_id INTEGER REFERENCES episodes(id);
ALTER TABLE questions_approved ADD COLUMN sequence_in_episode INTEGER;
ALTER TABLE questions_approved ADD COLUMN scene_setup TEXT;
ALTER TABLE questions_approved ADD COLUMN narrative_continuation TEXT;
ALTER TABLE questions_approved ADD COLUMN deep_context TEXT;
ALTER TABLE questions_approved ADD COLUMN forward_hook TEXT;

-- ── Mirror columns on questions_draft ────────────────────────────────────────
ALTER TABLE questions_draft ADD COLUMN episode_id INTEGER REFERENCES episodes(id);
ALTER TABLE questions_draft ADD COLUMN sequence_in_episode INTEGER;
ALTER TABLE questions_draft ADD COLUMN scene_setup TEXT;
ALTER TABLE questions_draft ADD COLUMN narrative_continuation TEXT;
ALTER TABLE questions_draft ADD COLUMN deep_context TEXT;
ALTER TABLE questions_draft ADD COLUMN forward_hook TEXT;

-- ── episode_id on generation_runs ────────────────────────────────────────────
ALTER TABLE generation_runs ADD COLUMN episode_id INTEGER REFERENCES episodes(id);

-- ── episodes table ────────────────────────────────────────────────────────────
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

-- ── Bookmark / saved wisdom ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS saved_questions (
    id INTEGER PRIMARY KEY,
    device_id TEXT NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions_approved(id),
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_note TEXT,
    UNIQUE(device_id, question_id)
);
CREATE INDEX IF NOT EXISTS idx_saved_device ON saved_questions(device_id);

-- ── Daily shlokas ─────────────────────────────────────────────────────────────
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

-- ── User progress (device-level) ──────────────────────────────────────────────
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

-- ── User progress per episode ─────────────────────────────────────────────────
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
