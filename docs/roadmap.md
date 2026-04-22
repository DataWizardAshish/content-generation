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

## COMPLETION CHECK

- [x] Generate → Review → Approve works end-to-end
- [x] No crashes
- [x] Data persists correctly

---

## RULE

Do not move to next phase until current is complete.
