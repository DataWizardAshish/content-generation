from fastapi import APIRouter, Query
from src import database as db
from services.shloka_rotation import get_todays_shloka_index

router = APIRouter(tags=["shlokas"])


@router.get("/daily-shloka")
def get_daily_shloka(device_id: str = Query(default="anonymous")):
    shlokas = db.get_active_shlokas()
    if not shlokas:
        return {"shloka": None, "message": "No shlokas available yet"}
    idx = get_todays_shloka_index(device_id, len(shlokas))
    return {"shloka": shlokas[idx]}


@router.get("/shlokas")
def browse_shlokas(
    theme: str = Query(default=""),
    kanda: str = Query(default=""),
):
    shlokas = db.get_active_shlokas()
    if theme:
        shlokas = [s for s in shlokas if s.get("theme") == theme]
    if kanda:
        shlokas = [s for s in shlokas if s.get("source_kanda") == kanda]
    return {"count": len(shlokas), "shlokas": shlokas}
