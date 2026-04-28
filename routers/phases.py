import json
from fastapi import APIRouter, HTTPException, Path
from src import database as db

router = APIRouter(prefix="/phases", tags=["phases"])


@router.get("")
def get_phases():
    stories = db.get_phase_stories()
    return {
        "phases": [
            {
                "story_phase": s["story_phase"],
                "title": s["title"],
                "mood": s["mood"],
                "key_characters": json.loads(s["key_characters"]),
            }
            for s in stories
        ]
    }


@router.get("/{story_phase}/story")
def get_phase_story(story_phase: str = Path(...)):
    story = db.get_phase_story(story_phase)
    if not story:
        raise HTTPException(status_code=404, detail=f"No phase story found for '{story_phase}'.")
    return {
        "story_phase": story["story_phase"],
        "title": story["title"],
        "narrative": story["narrative"],
        "key_events": json.loads(story["key_events"]),
        "key_characters": json.loads(story["key_characters"]),
        "mood": story["mood"],
        "shloka_watermark": story.get("shloka_watermark"),
    }
