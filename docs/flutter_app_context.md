# SHRUTI — Flutter App Backend Context

> **Load this file into every Flutter Claude Code session.**
> Do NOT read the backend repo code — everything needed is here.
> Last updated: 2026-04-27

---

## Project Overview

SHRUTI is a Ramayana quiz + learning app. Backend (`content_generation/` repo) runs FastAPI + SQLite. Flutter app consumes via REST API.

**Backend base URL (local dev):** `http://localhost:8000`  
**Auth:** None. All user state keyed by `device_id` (string, e.g. device UUID). Pass as query param.

---

## All Endpoints

### GET /health
```json
{ "status": "ok", "approved_questions": 142 }
```

---

### GET /questions
Filter approved questions.

**Query params:** `difficulty=easy|medium|hard`, `story_phase=<phase>`, `episode_id=<int>`, `limit=20`

**Response:**
```json
{
  "count": 5,
  "questions": [ <QuestionFull>, ... ]
}
```

---

### GET /questions/{id}
Single question by ID. Returns `<QuestionFull>` or 404.

---

### GET /questions/daily-insight
Legacy endpoint. Rotates daily by day-of-year. Returns `<QuestionFull>` with `is_daily_insight=1`.  
**Prefer `/insights/daily` instead** — richer narrative format.

---

### GET /story-phases
```json
{ "story_phases": ["Early Life of Rama", "Exile Phase", "Sita Haran", "Search for Sita", "Lanka War", "Return and Reunion", "Other"] }
```

---

### GET /episodes
List all 40 story episodes in sequence.

**Response:**
```json
{
  "episodes": [ <EpisodeSummary>, ... ]
}
```

---

### GET /episodes/{episode_id}?device_id=<id>
Full episode detail + optional user progress.

**Response:** `<EpisodeDetail>` with optional `user_progress` field.

---

### GET /episodes/{episode_id}/questions?device_id=<id>
All questions for an episode, plus episode metadata and user progress for that episode.

**Response:**
```json
{
  "episode": <EpisodeDetail>,
  "questions": [ <QuestionFull>, ... ],
  "user_progress": { "questions_attempted": 3, "questions_correct": 2, "completed_at": null }
}
```

---

### GET /user-progress?device_id=<id>
Full user progress summary.

**Response:**
```json
{
  "device_id": "abc123",
  "questions_answered": 42,
  "questions_correct": 35,
  "accuracy_percent": 83.3,
  "current_streak_days": 5,
  "longest_streak_days": 12,
  "weekly_active_days": 4,
  "last_active_date": "2026-04-27",
  "current_episode_id": 3,
  "farthest_episode_id": 5,
  "episode_completion_map": {
    "1": { "attempted": 5, "correct": 4, "completed_at": "2026-04-20T10:00:00" },
    "2": { "attempted": 3, "correct": 2, "completed_at": null }
  }
}
```

---

### POST /user-progress/answer
Record a question answer. Updates streak, score, episode progress.

**Body:**
```json
{ "device_id": "abc123", "question_id": 7, "was_correct": true, "time_taken_seconds": 12 }
```

**Response:** Updated `<ProgressSummary>` with `accuracy_percent`.

---

### GET /journey?device_id=<id>
User's narrative journey position and milestones.

**Response:**
```json
{
  "current_position": {
    "kanda": "Ayodhya",
    "episode_name": "Kaikeyi's Demands",
    "episode_sequence": 8,
    "progress_within_episode_percent": 50.0
  },
  "milestones_reached": ["Rama is born", "Vishwamitra's call begins"],
  "next_milestone": "Rama enters the forest",
  "week_summary": "4 of 7 days this week",
  "mood": "tension"
}
```

---

### GET /home?device_id=<id>
Home screen data. Single call returns everything needed.

**Response:**
```json
{
  "greeting": "Good morning, traveler. The story awaits.",
  "daily_shloka": <DailyShloka> | null,
  "daily_insight": <StoryInsight> | null,
  "continue_journey": {
    "current_episode_id": 3,
    "episode_name": "Kaikeyi's Demands",
    "questions_remaining": 2,
    "scene_glimpse": "The palace corridors fall silent..."
  },
  "recent_wisdom": [ <SavedQuestion>, ... ],
  "week_summary": "4 of 7 days this week"
}
```

> `daily_shloka` is null until shlokas are seeded in DB.
> `continue_journey.current_episode_id` infers from `user_episode_progress` rows if Flutter hasn't yet called `POST /user-progress/answer` (handles local-only progress). Falls back to episode 1 for new users.

---

### GET /insights/daily
Daily story insight — **LLM-generated fresh each day**, stored in DB. Falls back to 7 seeded entries if LLM fails.

**Response:**
```json
{
  "id": 15,
  "title": "Bharata Crowns the Sandals",
  "narrative": "Bharata reaches Chitrakuta with a kingdom weeping behind him...",
  "lesson": "True loyalty can make an empty throne brighter than a jeweled crown.",
  "story_phase": "Exile Phase",
  "character": "Bharata"
}
```

Returns 404 only if DB is completely empty.

---

### GET /phases
All 6 story phases — summary cards for Explore screen.

**Response:**
```json
{
  "phases": [
    {
      "story_phase": "Early Life of Rama",
      "title": "The Prince of Ayodhya",
      "mood": "wonder",
      "key_characters": ["Rama", "Lakshmana", "Vishwamitra", "Tataka"]
    },
    ...
  ]
}
```

---

### GET /phases/{story_phase}/story
Full narrative for one phase. Use for Explore → Phase Detail screen.

**URL encode the phase name** (e.g. `Exile%20Phase`).

**Response:**
```json
{
  "story_phase": "Exile Phase",
  "title": "The Forest Years",
  "narrative": "When Kaikeyi's long-dormant boon...",
  "key_events": ["Kaikeyi demands exile", "Bharata refuses the throne", "Chitrakoot settlement"],
  "key_characters": ["Rama", "Sita", "Lakshmana", "Kaikeyi", "Bharata"],
  "mood": "sacrifice",
  "shloka_watermark": "नहि कश्चित् क्षमां जेतुम् शक्तः"
}
```

`shloka_watermark` — Sanskrit verse to display as watermark text in the phase story screen background.

---

### GET /daily-shloka?device_id=<id>
Per-device rotating Sanskrit verse. Device + date → stable index.

**Response:**
```json
{ "shloka": <DailyShloka> | null }
```

---

### GET /shlokas?theme=<theme>&kanda=<kanda>
Browse all active shlokas. Both filters optional.

**Response:** `{ "count": N, "shlokas": [ <DailyShloka>, ... ] }`

---

### GET /saved-questions?device_id=<id>
User's bookmarked questions.

**Response:** `{ "count": N, "saved_questions": [ <SavedQuestion>, ... ] }`

---

### POST /saved-questions
Bookmark a question.

**Body:** `{ "device_id": "abc123", "question_id": 7, "user_note": "optional" }`

**Response:** saved record.

---

### DELETE /saved-questions/{question_id}?device_id=<id>
Remove bookmark.

**Response:** `{ "status": "removed", "question_id": 7, "device_id": "abc123" }`

---

## Data Models

### QuestionFull
```json
{
  "id": 1,
  "question": "Who granted Vishwamitra the boon he needed?",
  "option_a": "Brahma",
  "option_b": "Shiva",
  "option_c": "Vasishtha",
  "option_d": "Indra",
  "correct_answer": "A",
  "explanation": "same as narrative_continuation — legacy field",
  "difficulty": "easy | medium | hard",
  "topic": "string",
  "story_phase": "Early Life of Rama | Exile Phase | Sita Haran | Search for Sita | Lanka War | Return and Reunion | Other",
  "narrative_arc": "short phrase e.g. exile_begins",
  "chapter_title": "Book I – Canto I: Nárad",
  "engagement_score": 8,
  "enrichment_score": 7,
  "narrative_flow_score": 9,
  "is_daily_insight": 0,
  "episode_id": 3,
  "sequence_in_episode": 2,
  "scene_setup": "The palace corridors fall silent as the sage arrives...",
  "narrative_continuation": "Vishwamitra had come not for blessing but for Rama himself...",
  "deep_context": "In Vedic tradition, the relationship between kshatriya and brahmin...",
  "forward_hook": "But the sage has not yet revealed what danger awaits them in the forest.",
  "approved_at": "2026-04-23T10:00:00"
}
```

**5-field narrative system:**
| Field | Voice | Purpose |
|---|---|---|
| `scene_setup` | Present tense, cinematic | Sets context BEFORE the question; shown before options |
| `question` | Neutral, specific | The quiz question itself |
| `narrative_continuation` | Past tense prose | Confirms answer + story momentum; shown after answer |
| `deep_context` | Reflective, 10-15 sentences | Cultural/symbolic depth; shown in "Learn More" |
| `forward_hook` | 1 sentence, present/future | Creates pull toward next question; shown after answer |

**Display order in Quiz UI:**
1. Show `scene_setup` (context)
2. Show `question` + options
3. After answer: show `narrative_continuation`, then `forward_hook`
4. "Learn More" expands `deep_context`

---

### EpisodeSummary
```json
{
  "id": 8,
  "sequence_number": 8,
  "episode_name": "Kaikeyi's Demands",
  "episode_subtitle": "The Boon That Changed Everything",
  "kanda": "Ayodhya",
  "story_phase": "Exile Phase",
  "narrative_arc": "exile_begins",
  "emotional_tone": "tension",
  "key_characters": "Kaikeyi, Dasharatha, Rama",
  "question_count": 4
}
```

### EpisodeDetail (extends EpisodeSummary)
```json
{
  "sarga_start": 9,
  "sarga_end": 12,
  "opening_text": "The lamps of Ayodhya burned all night...",
  "closing_text": "And so Rama turned toward the forest...",
  "user_progress": { "questions_attempted": 2, "questions_correct": 2, "completed_at": null }
}
```

---

### DailyShloka
```json
{
  "id": 1,
  "sequence_number": 1,
  "sanskrit_devanagari": "तमसो मा ज्योतिर्गमय",
  "sanskrit_transliteration": "tamas mā jyotirgamaya",
  "translation_en": "Lead me from darkness to light",
  "translation_hi": null,
  "meaning_context": "This verse from the Brihadaranyaka Upanishad...",
  "source_kanda": "Bala",
  "source_sarga": 1,
  "source_verse": "1.4",
  "theme": "dharma"
}
```

> DB table `daily_shlokas` currently empty. Endpoint returns `null` until seeded.

---

### StoryInsight (from /insights/daily)
```json
{
  "id": 2,
  "title": "Sita's Unyielding Flame",
  "narrative": "When Ravana's golden Lanka glittered before her...",
  "lesson": "True strength is the refusal to bend identity under pressure.",
  "story_phase": "Sita Haran",
  "character": "Sita"
}
```

---

### SavedQuestion
```json
{
  "saved_id": 3,
  "saved_at": "2026-04-27T09:15:00",
  "user_note": "beautiful question",
  "device_id": "abc123",
  "question_id": 7
}
```
Note: `GET /saved-questions` returns flat rows (not nested question object). Fetch full question separately via `GET /questions/{id}` if needed.

---

## Story Phases (Canonical Order)
```
1. Early Life of Rama
2. Exile Phase
3. Sita Haran
4. Search for Sita
5. Lanka War
6. Return and Reunion
7. Other
```

## Kandas (Books)
```
Bala, Ayodhya, Aranya, Kishkindha, Sundara, Yuddha
```

---

## Design System

### Palette
| Name | Hex | Usage |
|---|---|---|
| Parchment | `#F5E6C8` | Primary background |
| Saffron | `#E8821A` | Primary accent, CTA buttons |
| Temple Red | `#8B1A1A` | Correct answer glow, headers |
| Sandalwood | `#A0785A` | Secondary text, dividers |
| Deep Forest | `#2C4A2E` | Dark mode background |
| Gold | `#C9A84C` | Correct answer highlight, stars |
| Charcoal | `#1C1C1E` | Body text on light bg |

### Typography
- **Headings:** Google Fonts — *Cinzel* (serif, Roman-classical feel)
- **Body / options:** *Inter* or *Lato*
- **Sanskrit/verse text:** *Noto Serif Devanagari*

### Textures
- Parchment background: subtle paper grain texture (low opacity overlay)
- Background watermark: faded verse text at 6-8% opacity
- Illustrations: tasteful line-art or watercolor style only — NOT photographic

---

## Screen → Endpoint Map

| Screen | Primary endpoint | Secondary |
|---|---|---|
| Home | `GET /home` | — |
| Quiz (by phase) | `GET /questions?story_phase=X` | `POST /user-progress/answer` |
| Quiz (by episode) | `GET /episodes/{id}/questions` | `POST /user-progress/answer` |
| Journey | `GET /journey` | `GET /episodes` |
| Explore (phases) | `GET /phases` | `GET /phases/{phase}/story` |
| Episode detail | `GET /episodes/{id}` | — |
| Daily Insight card | Bundled in `GET /home` as `daily_insight` | `GET /insights/daily` |
| Daily Shloka card | Bundled in `GET /home` as `daily_shloka` | `GET /daily-shloka` |
| Saved / Bookmarks | `GET /saved-questions` | `POST /saved-questions`, `DELETE /saved-questions/{id}` |
| Progress / Stats | `GET /user-progress` | — |

---

## v1 Scope

**Ship:**
- Home screen (greeting + daily_insight + daily_shloka + continue_journey + week_summary)
- Quiz flow: by episode or by phase; scene_setup → question → answer reveal → narrative_continuation + forward_hook
- Journey screen: current position + milestones
- Explore screen: phase list + phase story detail
- Bookmarks: save/unsave questions
- Local progress (streak, score) via `/user-progress`

**NOT in v1:**
- Authentication / accounts
- Leaderboards / social
- Hindi language
- Push notifications
- Payments

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| User identity | device_id string | No auth needed for v1 |
| State | Server-side (SQLite) | Streak + progress accurate across devices |
| Content pipeline | 3-pass LLM (generate → validate → critique) | Quality gate before DB |
| LLM model | GPT-5.5 via Responses API | Best narrative quality |
| Questions per episode | ~5-8 | Paced learning, not exhausting |
| Explanation style | 5 narrative fields (not 1 paragraph) | Immersive story experience |
