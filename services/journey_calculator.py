from services.streak import week_summary_copy

MILESTONES = {
    1: "The story begins — Rama is born in Ayodhya",
    7: "Parashuram's challenge overcome — ready for greater tests",
    8: "The palace turns — Kaikeyi speaks her demand",
    10: "Ayodhya left behind — the forest path begins",
    13: "Forest life deepens — the world of sages and shadow",
    17: "Sita taken — the wound at the heart of the story",
    20: "Hanuman found — hope arrives in disguise",
    24: "The sea crossed — Lanka within reach",
    25: "Sita found in the Ashoka grove",
    28: "Vibhishan crosses over — Lanka's own brother joins Rama",
    29: "The bridge is built — armies cross to Lanka",
    37: "Ravana falls — the long war ends",
    39: "Agni Pariksha — Sita's truth tested by fire",
    40: "Return and coronation — Rama ascends the throne",
}


def get_current_position(user_progress: dict, episodes: list[dict]) -> dict:
    episode_id = user_progress.get("current_episode_id") or 1
    ep = next((e for e in episodes if e["id"] == episode_id), None)
    if not ep:
        ep = episodes[0] if episodes else {}

    ep_progress = user_progress.get("_episode_progress", {})
    ep_data = ep_progress.get(episode_id, {})
    attempted = ep_data.get("questions_attempted", 0)

    conn_episode_questions = ep.get("question_count", 0)
    pct = (attempted / conn_episode_questions * 100) if conn_episode_questions > 0 else 0

    return {
        "kanda": ep.get("kanda", ""),
        "episode_name": ep.get("episode_name", ""),
        "episode_sequence": ep.get("sequence_number", 1),
        "progress_within_episode_percent": round(pct, 1),
    }


def get_milestones_reached(episode_progress_map: dict, episodes: list[dict]) -> list[str]:
    """Return story beat labels for all episodes the user has attempted."""
    reached = []
    attempted_ep_ids = {ep_id for ep_id, data in episode_progress_map.items()
                        if data.get("questions_attempted", 0) > 0}
    ep_seq_map = {e["id"]: e["sequence_number"] for e in episodes}
    for ep_id in sorted(attempted_ep_ids, key=lambda x: ep_seq_map.get(x, 999)):
        seq = ep_seq_map.get(ep_id, 0)
        label = MILESTONES.get(seq)
        if label:
            reached.append(label)
    return reached


def get_next_milestone(current_episode_id: int, episodes: list[dict]) -> str:
    ep_seq_map = {e["id"]: e["sequence_number"] for e in episodes}
    current_seq = ep_seq_map.get(current_episode_id, 0)
    for seq in sorted(MILESTONES.keys()):
        if seq > current_seq:
            return MILESTONES[seq]
    return "The journey is complete — Rama's story lives in you"


def build_journey_response(user_progress: dict, episodes: list[dict], weekly_active: int) -> dict:
    ep_progress = user_progress.get("_episode_progress", {})

    current_pos = get_current_position(user_progress, episodes)
    milestones = get_milestones_reached(ep_progress, episodes)
    current_ep_id = user_progress.get("current_episode_id") or 1
    next_ms = get_next_milestone(current_ep_id, episodes)
    current_ep = next((e for e in episodes if e["id"] == current_ep_id), {})
    mood = current_ep.get("emotional_tone") or "devotion"

    return {
        "current_position": current_pos,
        "milestones_reached": milestones,
        "next_milestone": next_ms,
        "week_summary": week_summary_copy(weekly_active),
        "mood": mood,
    }
