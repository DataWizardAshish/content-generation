import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src import database as db
from src.logger import get_logger
from routers import episodes, saved, shlokas, progress, journey, home, insights, phases

logger = get_logger("api")

app = FastAPI(title="SHRUTI — Epic Quiz API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.include_router(episodes.router)
app.include_router(saved.router)
app.include_router(shlokas.router)
app.include_router(progress.router)
app.include_router(journey.router)
app.include_router(home.router)
app.include_router(insights.router)
app.include_router(phases.router)

STORY_PHASES = [
    "Early Life of Rama",
    "Exile Phase",
    "Sita Haran",
    "Search for Sita",
    "Lanka War",
    "Return and Reunion",
    "Other",
]


@app.get("/health")
def health():
    stats = db.get_stats()
    return {"status": "ok", "approved_questions": stats["approved"]}


@app.get("/questions")
def get_questions(
    difficulty: str = Query(default="", description="easy|medium|hard"),
    story_phase: str = Query(default="", description="Story phase filter"),
    chapter: str = Query(default="", description="Chapter title filter"),
    episode_id: int = Query(default=None, description="Filter by episode ID"),
    limit: int = Query(default=20, ge=1, le=200),
):
    if difficulty and difficulty not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=400, detail="difficulty must be easy|medium|hard")
    if story_phase and story_phase not in STORY_PHASES:
        raise HTTPException(status_code=400, detail=f"story_phase must be one of: {STORY_PHASES}")

    questions = db.get_approved_questions(difficulty=difficulty, chapter=chapter, episode_id=episode_id)

    if story_phase:
        questions = [q for q in questions if q.get("story_phase") == story_phase]

    questions = questions[:limit]
    logger.info(
        "GET /questions → %d results (difficulty=%r, phase=%r, episode_id=%r)",
        len(questions), difficulty, story_phase, episode_id,
    )
    return {"count": len(questions), "questions": questions}


@app.get("/questions/daily-insight")
def get_daily_insight():
    all_questions = db.get_approved_questions()
    candidates = [q for q in all_questions if q.get("is_daily_insight")]

    if not candidates:
        candidates = sorted(all_questions, key=lambda q: q.get("engagement_score") or 0, reverse=True)
        if not candidates:
            raise HTTPException(status_code=404, detail="No approved questions found")

    day_index = datetime.date.today().timetuple().tm_yday
    question = candidates[day_index % len(candidates)]
    logger.info("GET /questions/daily-insight → id=%d", question["id"])
    return question


@app.get("/questions/{question_id}")
def get_question(question_id: int):
    all_questions = db.get_approved_questions()
    for q in all_questions:
        if q["id"] == question_id:
            return q
    raise HTTPException(status_code=404, detail=f"Question {question_id} not found")


@app.get("/story-phases")
def get_story_phases():
    return {"story_phases": STORY_PHASES}


@app.get("/stats")
def get_stats():
    return db.get_stats()
