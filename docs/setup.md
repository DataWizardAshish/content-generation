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

OPENAI_API_KEY=your_key_here

---

### 5. Run App
streamlit run app.py

---

## 📦 Required Packages

- streamlit
- openai
- python-dotenv
- requests
- beautifulsoup4
- sqlite3 (builtin)

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
2. Paste chapter text manually — OR — use "Crawl Next Chapter" to auto-fetch from Wikisource
3. Set number of questions (default: 3)
4. Click Generate — runs 3-step pipeline: generate → grounding validation → self-critique
5. Review questions (grounding badge + engagement score shown)
6. Approve → saved in DB
7. Export from Library tab

---

## 🧭 Troubleshooting

- API error → check key
- JSON parse error → check logs
- DB error → reset DB file

---

## DONE

System is ready when full flow works without errors.