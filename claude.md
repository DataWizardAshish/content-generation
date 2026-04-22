# CLAUDE.md

## MODE: AUTONOMOUS BUILDER

You are responsible for building this project end-to-end without human intervention.

Do NOT ask for confirmation unless absolutely blocked.
Make reasonable assumptions and proceed.

---

## 🎯 OBJECTIVE

Build a local Streamlit-based admin tool that:
1. Takes chapter text as input
2. Uses Claude API to generate quiz questions
3. Allows human review (approve/edit/reject)
4. Stores only approved questions in SQLite
5. Is production-ready for migration to Postgres later

---

## 🧠 ENGINEERING PHILOSOPHY

- Prefer **simple over complex**
- Prefer **working over perfect**
- Prefer **explicit over abstract**
- Optimize for **speed of iteration**
- Every component must be **independently testable**

---

## ⚙️ EXECUTION STRATEGY

Follow this strict order:

1. Setup project structure
2. Setup config + environment loading
3. Setup database + schema
4. Build LLM client
5. Build JSON parser (robust)
6. Build generation service
7. Build review service
8. Build Streamlit UI (3 tabs)
9. Add logging + error handling
10. Add minimal tests

Do NOT skip steps.

---

## 📦 SYSTEM DESIGN RULES

### Separation of Concerns
- UI layer → only rendering + inputs
- Service layer → business logic
- LLM layer → API calls only
- DB layer → SQL only

Never mix these.

---

### LLM RULES

- Always use structured JSON output
- Always validate response before use
- Retry once on failure
- Log raw response

Never trust LLM blindly.

---

### DATABASE RULES

- Never overwrite data
- Draft and approved must be separate
- Use transactions for approve flow

---

### ERROR HANDLING

- Fail loudly
- Never silently ignore errors
- Log all failures

---

### LOGGING

Log:
- Prompt sent to LLM
- Raw LLM response
- Parsed output
- DB writes

---

## 🧪 TESTING RULES

Test only critical paths:
- JSON parsing
- DB insert
- Generation pipeline

Avoid over-testing UI.

---

## 🚫 DO NOT BUILD

- Authentication
- RAG / vector DB
- Background jobs
- Complex configs
- Microservices

---

## 🧭 DECISION MAKING

If unclear:
- Choose simplest solution
- Avoid adding dependencies
- Prefer standard library

---

## 🏁 DONE CRITERIA

Project is complete when:
- I can paste chapter text
- Click generate
- Review questions
- Approve → saved in DB
- Export approved questions

No missing flows.

---

## FINAL RULE

"Build the simplest system that fully works — then stop."