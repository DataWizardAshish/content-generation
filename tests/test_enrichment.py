"""
Tests for enrichment features: saved questions, shloka rotation, streak, journey, home.
All DB tests use a temporary in-memory SQLite DB.
"""
import datetime
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Streak ────────────────────────────────────────────────────────────────────

from services.streak import calculate_streak, calculate_weekly_active, week_summary_copy


class TestStreak:
    def test_first_activity_returns_1(self):
        assert calculate_streak(None, 0) == 1

    def test_active_today_no_change(self):
        today = datetime.date.today()
        assert calculate_streak(today, 5) == 5

    def test_active_yesterday_increments(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        assert calculate_streak(yesterday, 3) == 4

    def test_grace_day_one_missed_holds(self):
        two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
        assert calculate_streak(two_days_ago, 5) == 5

    def test_two_missed_days_resets(self):
        three_days_ago = datetime.date.today() - datetime.timedelta(days=3)
        assert calculate_streak(three_days_ago, 10) == 1

    def test_week_summary_copy(self):
        assert week_summary_copy(4) == "4 of 7 days this week"
        assert week_summary_copy(0) == "0 of 7 days this week"

    def test_weekly_active_counts_unique_days(self):
        today = datetime.date.today()
        dates = [today, today - datetime.timedelta(days=1), today - datetime.timedelta(days=1)]
        assert calculate_weekly_active(dates) == 2

    def test_weekly_active_excludes_old_dates(self):
        today = datetime.date.today()
        dates = [today, today - datetime.timedelta(days=8)]
        assert calculate_weekly_active(dates) == 1


# ── Shloka rotation ───────────────────────────────────────────────────────────

from services.shloka_rotation import get_todays_shloka_index


class TestShlokaRotation:
    def test_same_device_same_day_same_index(self):
        idx1 = get_todays_shloka_index("device_abc", 20)
        idx2 = get_todays_shloka_index("device_abc", 20)
        assert idx1 == idx2

    def test_index_within_bounds(self):
        idx = get_todays_shloka_index("device_xyz", 10)
        assert 0 <= idx < 10

    def test_different_devices_may_differ(self):
        # Not guaranteed but very likely with 20 shlokas
        idxs = {get_todays_shloka_index(f"device_{i}", 20) for i in range(10)}
        assert len(idxs) > 1

    def test_zero_total_returns_zero(self):
        assert get_todays_shloka_index("any", 0) == 0

    def test_total_one_always_zero(self):
        assert get_todays_shloka_index("any_device", 1) == 0


# ── Journey calculator ────────────────────────────────────────────────────────

from services.journey_calculator import get_milestones_reached, get_next_milestone, get_current_position


MOCK_EPISODES = [
    {"id": 1, "sequence_number": 1, "episode_name": "Birth of Rama", "kanda": "Bala",
     "story_phase": "Early Life of Rama", "emotional_tone": "wonder", "question_count": 5},
    {"id": 8, "sequence_number": 8, "episode_name": "Kaikeyi's Demands", "kanda": "Ayodhya",
     "story_phase": "Exile Phase", "emotional_tone": "tension", "question_count": 4},
    {"id": 17, "sequence_number": 17, "episode_name": "Sita Haran", "kanda": "Aranya",
     "story_phase": "Sita Haran", "emotional_tone": "grief", "question_count": 6},
]


class TestJourney:
    def test_no_milestones_when_no_progress(self):
        result = get_milestones_reached({}, MOCK_EPISODES)
        assert result == []

    def test_milestone_reached_after_episode_attempted(self):
        ep_map = {1: {"questions_attempted": 3, "questions_correct": 2}}
        result = get_milestones_reached(ep_map, MOCK_EPISODES)
        assert any("born" in m.lower() or "begins" in m.lower() or "Rama" in m for m in result)

    def test_next_milestone_advances_correctly(self):
        next_ms = get_next_milestone(1, MOCK_EPISODES)
        assert isinstance(next_ms, str)
        assert len(next_ms) > 0

    def test_current_position_defaults_episode_1(self):
        progress = {"current_episode_id": 1, "_episode_progress": {}}
        pos = get_current_position(progress, MOCK_EPISODES)
        assert pos["episode_sequence"] == 1
        assert pos["progress_within_episode_percent"] == 0.0


# ── Saved questions (DB) ──────────────────────────────────────────────────────

import sqlite3
import contextlib


def make_test_db():
    """Create in-memory DB with full schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    schema = open(os.path.join(os.path.dirname(__file__), "..", "src", "database.py")).read()
    # extract SCHEMA string and run it
    import re
    match = re.search(r'SCHEMA = """(.*?)"""', schema, re.DOTALL)
    assert match, "Could not find SCHEMA in database.py"
    conn.executescript(match.group(1))
    conn.commit()
    # seed a question
    conn.execute(
        """INSERT INTO questions_approved
           (question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty)
           VALUES ('Test Q?', 'A', 'B', 'C', 'D', 'A', 'Because A', 'easy')"""
    )
    conn.commit()
    return conn


class TestSavedQuestions:
    def setup_method(self):
        self.conn = make_test_db()

    def teardown_method(self):
        self.conn.close()

    def _save(self, device, qid, note=None):
        self.conn.execute(
            """INSERT INTO saved_questions (device_id, question_id, user_note)
               VALUES (?, ?, ?)
               ON CONFLICT(device_id, question_id) DO UPDATE SET user_note=excluded.user_note, saved_at=CURRENT_TIMESTAMP""",
            (device, qid, note),
        )
        self.conn.commit()

    def _list(self, device):
        rows = self.conn.execute(
            "SELECT * FROM saved_questions WHERE device_id=?", (device,)
        ).fetchall()
        return [dict(r) for r in rows]

    def _unsave(self, device, qid):
        self.conn.execute(
            "DELETE FROM saved_questions WHERE device_id=? AND question_id=?", (device, qid)
        )
        self.conn.commit()

    def test_save_question(self):
        self._save("dev1", 1)
        saved = self._list("dev1")
        assert len(saved) == 1
        assert saved[0]["question_id"] == 1

    def test_resave_updates_note(self):
        self._save("dev1", 1, "first note")
        self._save("dev1", 1, "updated note")
        saved = self._list("dev1")
        assert len(saved) == 1
        assert saved[0]["user_note"] == "updated note"

    def test_unsave_removes_entry(self):
        self._save("dev1", 1)
        self._unsave("dev1", 1)
        saved = self._list("dev1")
        assert len(saved) == 0

    def test_different_devices_isolated(self):
        self._save("dev1", 1)
        self._save("dev2", 1, "dev2 note")
        assert len(self._list("dev1")) == 1
        assert len(self._list("dev2")) == 1
        assert self._list("dev1")[0].get("user_note") is None
        assert self._list("dev2")[0]["user_note"] == "dev2 note"


# ── Home endpoint keys ────────────────────────────────────────────────────────

class TestHomeResponseKeys:
    REQUIRED_KEYS = {"greeting", "daily_shloka", "daily_insight", "continue_journey", "recent_wisdom", "week_summary"}

    def test_home_keys_present(self, monkeypatch):
        """Home endpoint must return all 6 required keys even for a new device."""
        import routers.home as home_router

        monkeypatch.setattr("src.database.get_user_progress", lambda d: {
            "device_id": d, "questions_answered": 0, "questions_correct": 0,
            "current_streak_days": 0, "longest_streak_days": 0, "weekly_active_days": 0,
            "last_active_date": None, "current_episode_id": 1, "farthest_episode_id": 1,
        })
        monkeypatch.setattr("src.database.get_episodes", lambda: [])
        monkeypatch.setattr("src.database.get_active_shlokas", lambda: [])
        monkeypatch.setattr("src.database.get_insight_by_index", lambda i: None)
        monkeypatch.setattr("src.database.get_episode_questions", lambda ep_id: [])
        monkeypatch.setattr("src.database.get_user_episode_progress", lambda d: [])
        monkeypatch.setattr("src.database.get_saved_questions", lambda d: [])

        result = home_router.get_home(device_id="new_device")
        assert isinstance(result, dict)
        for key in self.REQUIRED_KEYS:
            assert key in result, f"Missing key: {key}"
