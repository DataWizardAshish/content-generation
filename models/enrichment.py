from pydantic import BaseModel
from typing import Optional


class EpisodeSummary(BaseModel):
    id: int
    sequence_number: int
    episode_name: str
    episode_subtitle: Optional[str] = None
    kanda: str
    story_phase: str
    narrative_arc: Optional[str] = None
    emotional_tone: Optional[str] = None
    key_characters: Optional[str] = None
    question_count: int = 0


class EpisodeDetail(EpisodeSummary):
    sarga_start: int
    sarga_end: int
    opening_text: Optional[str] = None
    closing_text: Optional[str] = None
    user_progress: Optional[dict] = None


class QuestionWithContext(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: str
    difficulty: str
    topic: Optional[str] = None
    story_phase: Optional[str] = None
    narrative_arc: Optional[str] = None
    chapter_title: Optional[str] = None
    engagement_score: Optional[int] = None
    is_daily_insight: int = 0
    episode_id: Optional[int] = None
    sequence_in_episode: Optional[int] = None
    scene_setup: Optional[str] = None
    narrative_continuation: Optional[str] = None
    deep_context: Optional[str] = None
    forward_hook: Optional[str] = None


class SaveQuestionRequest(BaseModel):
    device_id: str
    question_id: int
    user_note: Optional[str] = None


class SavedQuestion(BaseModel):
    saved_id: int
    saved_at: str
    user_note: Optional[str] = None
    question: QuestionWithContext


class DailyShloka(BaseModel):
    id: int
    sequence_number: int
    sanskrit_devanagari: str
    sanskrit_transliteration: str
    translation_en: str
    translation_hi: Optional[str] = None
    meaning_context: str
    source_kanda: Optional[str] = None
    source_sarga: Optional[int] = None
    source_verse: Optional[str] = None
    theme: Optional[str] = None


class AnswerRequest(BaseModel):
    device_id: str
    question_id: int
    was_correct: bool
    time_taken_seconds: Optional[int] = None


class ProgressSummary(BaseModel):
    device_id: str
    questions_answered: int
    questions_correct: int
    accuracy_percent: float
    current_streak_days: int
    longest_streak_days: int
    weekly_active_days: int
    last_active_date: Optional[str] = None
    current_episode_id: Optional[int] = None
    farthest_episode_id: Optional[int] = None
    episode_completion_map: dict = {}


class JourneyPosition(BaseModel):
    kanda: str
    episode_name: str
    episode_sequence: int
    progress_within_episode_percent: float


class JourneyResponse(BaseModel):
    current_position: JourneyPosition
    milestones_reached: list[str]
    next_milestone: str
    week_summary: str
    mood: str


class ContinueJourney(BaseModel):
    current_episode_id: int
    episode_name: str
    questions_remaining: int
    scene_glimpse: Optional[str] = None


class HomeResponse(BaseModel):
    greeting: str
    daily_shloka: Optional[DailyShloka] = None
    todays_quest: Optional[dict] = None
    continue_journey: Optional[ContinueJourney] = None
    recent_wisdom: list[dict] = []
    week_summary: str
