# ROADMAP.md

## STATUS TRACKING

Each task must be marked:
- [ ] Not Started
- [~] In Progress
- [x] Done

---

## PHASE 1: FOUNDATION

### Project Setup
- [x] Create repo structure
- [x] Setup virtual environment
- [x] Add requirements.txt
- [x] Setup .env config

---

## PHASE 2: DATABASE

- [x] Create SQLite connection module
- [x] Create schema.sql
- [x] Implement questions_draft table
- [x] Implement questions_approved table
- [x] Implement generation_runs table
- [x] Test DB insert + read

---

## PHASE 3: LLM LAYER

- [x] Setup Claude API client
- [x] Create prompt template (v1)
- [x] Implement API call function
- [x] Add retry + logging

---

## PHASE 4: PARSER

- [x] Parse JSON response
- [x] Validate schema
- [x] Handle malformed output
- [x] Add unit tests

---

## PHASE 5: SERVICES

### Generation Service
- [x] Input → prompt → LLM → parse → save draft
- [x] Create generation_runs entry

### Review Service
- [x] Approve flow (draft → approved)
- [x] Reject flow
- [x] Edit flow

---

## PHASE 6: UI (STREAMLIT)

### Generate Tab
- [x] Text input
- [x] Metadata input
- [x] Generate button

### Review Tab
- [x] Show 1 question at a time
- [x] Edit capability
- [x] Approve / Reject buttons

### Library Tab
- [x] Show approved questions
- [x] Filters
- [x] Export

---

## PHASE 7: QUALITY

- [x] Logging system
- [x] Error handling
- [x] Cost tracking (optional)

---

## PHASE 8: FINALIZATION

- [x] End-to-end test
- [x] Fix edge cases
- [x] Backup export feature
- [x] README

---

## PHASE 9: PROMPT QUALITY

- [x] Strict grounding rules (every answer traceable to exact quote)
- [x] Hallucination killer — discard question if no supporting phrase found
- [x] Distractor quality rule ("almost right" — real names/events, not obviously wrong)
- [x] Self-contained questions (specific names, no pronouns unless named in same sentence)
- [x] Answer position randomization (correct answer spread across A/B/C/D)
- [x] "You Are There" explanation style (present tense, 4-6 sentences, open with scene, embed answer, close with significance)

---

## PHASE 10: MULTI-STEP PIPELINE

- [x] Grounding validation pass (second LLM call, VALIDATION_SYSTEM_PROMPT)
- [x] Self-critique pass (third LLM call, SELF_CRITIQUE_SYSTEM_PROMPT)
- [x] Engagement scoring 1-10 per question
- [x] Daily Insight Candidate flag (score ≥ 8 + surprising explanation)
- [x] `call_llm_text()` — separate LLM call without JSON response_format constraint

---

## PHASE 11: CONTENT TAGGING

- [x] Story phase tagging (Early Life of Rama, Exile Phase, Sita Haran, Search for Sita, Lanka War, Return and Reunion, Other)
- [x] Narrative arc metadata per question (short phrase: exile_begins, war_preparation, etc.)
- [x] DB migration pattern — `_migrate()` adds columns to existing DBs without data loss

---

## PHASE 12: CRAWLER

- [x] Wikisource Ramayana auto-crawler (271 chapters)
- [x] MD5-keyed HTML disk cache (`crawler_cache/`) — no re-fetch on repeat runs
- [x] Persistent crawl state (`crawler_state.json`) — resumes from last position
- [x] Auto-skip chapters with no extractable text
- [x] Auto-fill chapter title + text directly into Generate tab fields

---

## PHASE 13: UI ENHANCEMENTS

- [x] Grounding badge in Review tab (✅/❌/⚠️ + confidence score + supporting text)
- [x] Engagement score display (color-coded: green ≥ 8, yellow ≥ 5, red < 5) + 🌟 Daily Insight badge
- [x] Improvement suggestion from self-critique shown in Review
- [x] Story phase selectbox in Review (editable before approve)
- [x] Library: filter by chapter + difficulty (dynamic options from DB)
- [x] Library: delete approved questions
- [x] Library: 🌟 insight badge + engagement score in card header

---

## COMPLETION CHECK

- [x] Generate → Review → Approve works end-to-end
- [x] No crashes
- [x] Data persists correctly
- [x] 3-step pipeline (generate → validate → self-critique) runs on each generation
- [x] Crawler auto-fills chapter text from Wikisource
- [x] All metadata (story phase, narrative arc, engagement, insight flag) saved in DB

---

## RULE

Do not move to next phase until current is complete.
