# SETUP.md

## 🛠️ Local Setup

### 1. Clone Repo
git clone <repo>
cd epic-quiz-admin

---

### 2. Create Virtual Environment
python -m venv .venv

Activate:
- Windows: .venv\Scripts\activate
- Mac/Linux: source .venv/bin/activate

---

### 3. Install Dependencies
pip install -r requirements.txt

---

### 4. Environment Variables

Create `.env`:

ANTHROPIC_API_KEY=your_key_here

---

### 5. Run App
streamlit run app.py

---

## 📦 Required Packages

- streamlit
- anthropic
- python-dotenv
- sqlite3 (builtin)
- pydantic (optional for validation)

---

## 🗄️ Database

- SQLite file auto-created: `questions.db`
- Schema auto-initialized on first run

---

## 🔐 Notes

- Never commit `.env`
- Backup `questions.db` regularly

---

## 🚀 First Run Flow

1. Open app
2. Paste chapter text
3. Generate questions
4. Review + approve
5. Verify DB entries

---

## 🧭 Troubleshooting

- API error → check key
- JSON parse error → check logs
- DB error → reset DB file

---

## DONE

System is ready when full flow works without errors.