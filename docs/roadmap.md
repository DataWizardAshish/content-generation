# ROADMAP.md

## STATUS TRACKING

- [ ] Not Started
- [~] In Progress
- [x] Done

---

## PHASE 1: FOUNDATION
- [x] Create repo structure
- [x] Setup virtual environment
- [x] Add requirements.txt
- [x] Setup .env config

---

## PHASE 2: DATABASE
- [x] questions_draft table
- [x] questions_approved table
- [x] generation_runs table
- [x] Test DB insert + read

---

## PHASE 3: LLM LAYER
- [x] Setup Anthropic → migrated to OpenAI → migrated to GPT-5.5 (Responses API)
- [x] Structured JSON output
- [x] Retry + logging

---

## PHASE 4: PARSER
- [x] Parse JSON response
- [x] Validate schema
- [x] Handle malformed output
- [x] Unit tests

---

## PHASE 5: SERVICES
- [x] Generation service (input → prompt → LLM → parse → save draft)
- [x] Review service (approve / reject / edit)

---

## PHASE 6: UI (STREAMLIT)
- [x] Generate tab
- [x] Review tab (approve/reject/edit)
- [x] Library tab (filter + export)

---

## PHASE 7: QUALITY
- [x] Logging system
- [x] Error handling

---

## PHASE 8: FINALIZATION
- [x] End-to-end test
- [x] Export feature

---

## PHASE 9: PROMPT QUALITY
- [x] Strict grounding rules (answer traceable to exact quote)
- [x] Distractor quality rule (plausible "almost right")
- [x] Self-contained questions
- [x] "You Are There" explanation style

---

## PHASE 10: MULTI-STEP PIPELINE
- [x] Grounding validation pass (2nd LLM call)
- [x] Self-critique pass (3rd LLM call)
- [x] Engagement scoring 1-10
- [x] Daily Insight Candidate flag (score ≥ 8)

---

## PHASE 11: CONTENT TAGGING
- [x] Story phase tagging (7 phases)
- [x] Narrative arc metadata per question
- [x] DB migration pattern (_migrate())

---

## PHASE 12: CRAWLER
- [x] Wikisource Ramayana auto-crawler (271 chapters)
- [x] MD5-keyed HTML disk cache
- [x] Persistent crawl state
- [x] Auto-fill chapter text into Generate tab

---

## PHASE 13: UI ENHANCEMENTS
- [x] Grounding badge in Review tab
- [x] Engagement score display (color-coded)
- [x] Story phase selectbox (editable before approve)
- [x] Library: filter by chapter + difficulty
- [x] Library: delete approved questions

---

## PHASE 14: LLM MIGRATION — GPT-5.5 + RESPONSES API
- [x] Migrate from OpenAI Chat Completions to Responses API (`client.responses.create()`)
- [x] Use `input=` param (not `messages=`), `text.verbosity=low`
- [x] Structured Outputs via JSON schema in `text.format`
- [x] Remove `reasoning.effort` (not supported by GPT-5.5 generalist)
- [x] OPENAI_MODEL=gpt-5.5 in .env
- [x] Outcome-first prompt rewrites (no CAPS headers, no shouting)

---

## PHASE 15: 5-FIELD NARRATIVE PIPELINE
- [x] 5 fields per question: scene_setup, question, narrative_continuation, deep_context, forward_hook
- [x] Distinct voice per field (cinematic / neutral / past-tense prose / reflective / 1-sentence hook)
- [x] Story continuation rule: forward_hook(Q_n) flows into scene_setup(Q_n+1)
- [x] 2 few-shot examples embedded in SYSTEM_PROMPT (Tataka single + Bali pair)
- [x] VALIDATION_SYSTEM_PROMPT validates all 5 fields
- [x] SELF_CRITIQUE_SYSTEM_PROMPT adds enrichment_score + narrative_flow_score
- [x] DB migrations: enrichment_score, narrative_flow_score columns
- [x] schemas.py: QUESTIONS_SCHEMA, VALIDATION_SCHEMA, CRITIQUE_SCHEMA
- [x] generation_service: _normalize_fields(), episode_metadata passthrough
- [x] parser.py: explanation optional, all 5 fields optional
- [x] Streamlit review UI: shows all 5 fields
- [x] 22/22 tests passing after pipeline change

---

## PHASE 16: FASTAPI ENRICHMENT LAYER
- [x] FastAPI app (src/api.py) with CORS
- [x] Router: /episodes (list, detail, questions)
- [x] Router: /user-progress (GET summary, POST answer)
- [x] Router: /journey (current position, milestones, week summary)
- [x] Router: /saved-questions (GET, POST, DELETE)
- [x] Router: /shlokas (daily-shloka, browse)
- [x] Router: /home (aggregated home screen data)
- [x] DB: user_progress, user_episode_progress, saved_questions, daily_shlokas tables
- [x] DB: episodes table with 40-episode seed
- [x] Services: streak calculator, shloka rotation, journey calculator
- [x] Tests: 22 enrichment tests (streak, shloka rotation, journey, saved questions, home keys)
- [x] models/enrichment.py (Pydantic models)

---

## PHASE 17: DAILY INSIGHT + PHASE STORIES
- [x] story_insights table (id, title, narrative, lesson, story_phase, character, is_active)
- [x] phase_stories table (story_phase, title, narrative, key_events JSON, key_characters JSON, mood)
- [x] 7 story insights seeded (src/insights_data.py)
- [x] 6 phase stories seeded (one per story phase)
- [x] Router: GET /insights/daily (rotates by day-of-year)
- [x] Router: GET /phases (summary list)
- [x] Router: GET /phases/{story_phase}/story (full narrative)
- [x] /home response: `daily_insight` replaces `todays_quest`
- [x] Tests updated: REQUIRED_KEYS uses `daily_insight` not `todays_quest`

---

## PHASE 18: LLM DAILY INSIGHTS + PHASE WATERMARKS
- [x] `insight_date DATE` column on story_insights (migration)
- [x] `shloka_watermark TEXT` column on phase_stories (migration + backfill)
- [x] `get_or_create_todays_insight(llm_fn)` — generates via LLM on first call per day, stores with insight_date, falls back to seeds
- [x] `src/insight_generation.py` — Valmiki persona prompt, strips markdown fences, validates 5 fields
- [x] GET /insights/daily uses LLM generation (not static rotation)
- [x] GET /home uses same LLM insight with try/except fallback
- [x] Phase stories seeded with 6 Sanskrit shloka_watermarks
- [x] GET /phases/{phase}/story returns shloka_watermark
- [x] /home continue_journey smarter fallback: infers current episode from user_episode_progress rows (handles Flutter local-only progress)
- [x] POST /user-progress/answer correctly sets current_episode_id from question's episode_id
- [x] 22/22 tests passing

---

## PENDING / NEXT PHASES

### PHASE 18: SHLOKA SEEDING
- [ ] Seed daily_shlokas table with 20-30 Ramayana shlokas
- [ ] Structured format: sanskrit_devanagari, transliteration, translation_en, meaning_context, theme, source_kanda

### PHASE 19: EPISODE RICH METADATA
- [ ] Populate emotional_tone, narrative_arc, opening_text, closing_text for all 40 episodes
- [ ] Generate via LLM or manual curation

### PHASE 20: FLUTTER APP
- [ ] Home screen: greeting + daily_insight card + daily_shloka card + continue_journey
- [ ] Quiz flow: scene_setup → question → reveal → narrative_continuation + forward_hook
- [ ] Journey screen: episode arc map + milestones
- [ ] Explore screen: phase list → phase story detail
- [ ] Bookmarks screen
- [ ] Progress stats

---

## RULE

Do not move to next phase until current is complete.
