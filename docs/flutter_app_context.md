# Epic Quiz App — Flutter Context Doc

Copy this file into the Flutter repo as `CLAUDE.md` before starting any session.

---

## Project Overview

User-facing quiz app for Indian epics (Ramayana first, Mahabharata later).
Admin tool (`content_generation/`) generates and curates questions via LLM pipeline.
This Flutter app consumes those questions via REST API.

---

## Backend API

**Source repo:** `content_generation/` (separate repo, runs locally or on server)
**API layer:** FastAPI (`src/api.py`) sitting on top of SQLite `questions.db`
**Base URL (local dev):** `http://localhost:8000`

### Endpoints (to be built in content_generation repo)

```
GET /questions
  ?difficulty=easy|medium|hard
  ?story_phase=Early Life of Rama|Exile Phase|Sita Haran|Search for Sita|Lanka War|Return and Reunion
  ?limit=10
  Returns: list of approved questions

GET /questions/daily-insight
  Returns: single question where is_daily_insight=1, rotated daily

GET /questions/{id}
  Returns: single question by ID
```

### Question Data Model

```json
{
  "id": 1,
  "question": "string",
  "option_a": "string",
  "option_b": "string",
  "option_c": "string",
  "option_d": "string",
  "correct_answer": "A|B|C|D",
  "explanation": "string (present-tense immersive narrative, 4-6 sentences)",
  "difficulty": "easy|medium|hard",
  "topic": "string",
  "story_phase": "Early Life of Rama|Exile Phase|Sita Haran|Search for Sita|Lanka War|Return and Reunion|Other",
  "narrative_arc": "string (short phrase e.g. exile_begins, war_preparation)",
  "chapter_title": "string (Wikisource chapter e.g. 'Book I – Canto I: Nárad')",
  "engagement_score": 8,
  "is_daily_insight": true,
  "approved_at": "2026-04-23T10:00:00"
}
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
- **Body / options:** *Inter* or *Lato* (clean, readable)
- **Sanskrit/verse text:** *Noto Serif Devanagari* (if Hindi added later)

### Textures
- Parchment background: subtle paper grain texture (low opacity overlay)
- Background watermark: faded Ramayana verse text at 6-8% opacity on key screens
- Rama-Sita illustration: tasteful line-art or watercolor style, used on Home and onboarding — NOT photographic

---

## Screen Specs

### 1. Home Screen
- "Today's Quest" card — shows Daily Insight question
- Greeting: "Begin your journey, [name]" or "What do you seek today?"
- Background: parchment + faint shloka watermark
- Bottom nav: Home | Quiz | Journey | Explore

### 2. Quiz Screen
- Full-screen question card
- 4 option tiles, tap to select
- Submit → reveal correct/wrong
- Correct: gold glow + brief explanation shown
- Wrong: muted grey fade + explanation shown
- Swipe right → next question
- No timer (calm, reflective pace)

### 3. Journey Screen (Progress)
- Visual story arc map: Early Life → Exile → Sita Haran → Search → Lanka War → Return
- Each phase shows: X questions answered / Y total
- Feels like a scroll or map, not a progress bar
- Unlocks phases as user answers questions

### 4. Explore / Library Screen
- Browse by story phase or difficulty
- Card per question: chapter title, difficulty badge, story phase tag
- Tap to read full Q+A (study mode)

### 5. Onboarding (first launch)
- 3 slides: What is this? → How it works → Begin
- Rama-Sita illustration on slide 1
- Minimal, no account required (local progress storage for v1)

---

## State Management

Use **Riverpod** (preferred) or **Provider**.
No complex state needed for v1 — questions loaded from API, answers stored locally.

Local persistence: `shared_preferences` for progress tracking (which questions answered, streak).

---

## Story Phase Order (for Journey map)

```
1. Early Life of Rama
2. Exile Phase
3. Sita Haran
4. Search for Sita
5. Lanka War
6. Return and Reunion
7. Other
```

---

## Content Quality Notes

Questions in the DB went through a 3-step LLM pipeline:
1. **Generate** — GPT-4o with strict grounding rules
2. **Grounding validation** — second LLM pass, verifies answer traceable to source text
3. **Self-critique** — third LLM pass, scores engagement 1-10, flags daily insight candidates

`engagement_score` ≥ 8 = high quality question. `is_daily_insight = true` = best of the best.
Use `is_daily_insight` questions prominently (daily card, featured sections).

---

## v1 Scope (ship this, nothing else)

- [ ] Home screen with daily insight question
- [ ] Quiz flow (fetch questions by story phase, answer, see explanation)
- [ ] Journey screen (story arc progress)
- [ ] Local progress persistence (no auth, no backend account)
- [ ] FastAPI backend running on localhost (or simple server)

## NOT in v1
- Authentication / user accounts
- Leaderboards
- Hindi language
- Personalization / recommendations
- Push notifications
- Payments

---

## Repo Structure (suggested)

```
epic_quiz_app/
  lib/
    main.dart
    screens/
      home_screen.dart
      quiz_screen.dart
      journey_screen.dart
      explore_screen.dart
    widgets/
      question_card.dart
      option_tile.dart
      phase_map.dart
    services/
      api_service.dart       ← HTTP calls to FastAPI
      progress_service.dart  ← local SharedPreferences
    models/
      question.dart
    theme/
      app_theme.dart         ← colors, fonts, textures
  assets/
    fonts/
    images/
      rama_sita.png
      parchment_texture.png
  pubspec.yaml
  CLAUDE.md  ← this file
```

---

## Key Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Platform | Flutter | Cross-platform, smooth animations |
| Backend | FastAPI on SQLite | Thin layer, existing DB, swap to Postgres later |
| State mgmt | Riverpod | Clean, testable, scales |
| Auth | None (v1) | Ship fast, local progress only |
| Repo | Separate from admin tool | Different deploy targets, different tech |
| Content source | Admin tool DB via API | Human-reviewed, quality pipeline |
