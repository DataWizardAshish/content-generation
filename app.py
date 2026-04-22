import streamlit as st
import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.dirname(__file__))

from src import database as db
from src.generation_service import generate_questions
from src.review_service import approve, reject, get_pending, get_library, export_to_json

st.set_page_config(
    page_title="Epic Quiz Admin",
    page_icon="📚",
    layout="wide",
)

# Init DB on startup
db.init_db()


# ─── Sidebar Stats ────────────────────────────────────────────────────────────
def render_sidebar():
    stats = db.get_stats()
    st.sidebar.title("📚 Epic Quiz Admin")
    st.sidebar.markdown("---")
    st.sidebar.metric("Pending Review", stats["pending"])
    st.sidebar.metric("Approved", stats["approved"])
    st.sidebar.metric("Rejected", stats["rejected"])
    st.sidebar.metric("Generation Runs", stats["runs"])


render_sidebar()

tab_generate, tab_review, tab_library = st.tabs(["⚡ Generate", "🔍 Review", "📖 Library"])


# ─── TAB 1: GENERATE ──────────────────────────────────────────────────────────
with tab_generate:
    st.header("Generate Quiz Questions")
    st.markdown("Paste chapter text below, set parameters, and generate questions.")

    col1, col2 = st.columns([3, 1])
    with col1:
        chapter_title = st.text_input("Chapter Title (optional)", placeholder="e.g., Adi Parva - Chapter 1")
    with col2:
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=30, value=10)

    chapter_text = st.text_area(
        "Chapter Text",
        height=350,
        placeholder="Paste the chapter text here...",
    )

    if st.button("⚡ Generate Questions", type="primary", use_container_width=True):
        if not chapter_text.strip():
            st.error("Please paste chapter text before generating.")
        else:
            with st.spinner(f"Generating {num_questions} questions via Claude API..."):
                result = generate_questions(
                    chapter_text=chapter_text.strip(),
                    num_questions=num_questions,
                    chapter_title=chapter_title.strip(),
                )

            if result["error"]:
                st.error(f"Generation failed: {result['error']}")
            else:
                n = len(result["questions"])
                st.success(f"Generated {n} questions! Switch to the Review tab to approve them.")
                st.balloons()

                with st.expander("Preview generated questions"):
                    for i, q in enumerate(result["questions"], 1):
                        st.markdown(f"**Q{i}: {q['question']}**")
                        st.markdown(f"- A: {q['option_a']}")
                        st.markdown(f"- B: {q['option_b']}")
                        st.markdown(f"- C: {q['option_c']}")
                        st.markdown(f"- D: {q['option_d']}")
                        st.markdown(f"✅ **{q['correct_answer']}** | 💬 {q['explanation']}")
                        st.markdown(f"Difficulty: `{q['difficulty']}` | Topic: `{q.get('topic','')}`")
                        st.divider()

                st.rerun()


# ─── TAB 2: REVIEW ────────────────────────────────────────────────────────────
with tab_review:
    st.header("Review Questions")

    pending = get_pending()

    if not pending:
        st.info("No pending questions. Generate some first!")
    else:
        st.markdown(f"**{len(pending)} question(s) awaiting review.**")

        # Use session state to track current index
        if "review_idx" not in st.session_state:
            st.session_state.review_idx = 0

        idx = st.session_state.review_idx
        if idx >= len(pending):
            st.session_state.review_idx = 0
            idx = 0

        q = pending[idx]

        progress_val = (idx + 1) / len(pending)
        st.progress(progress_val, text=f"Question {idx + 1} of {len(pending)}")

        # Navigation
        nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
        with nav_col1:
            if st.button("◀ Prev", disabled=idx == 0):
                st.session_state.review_idx = max(0, idx - 1)
                st.rerun()
        with nav_col3:
            if st.button("Next ▶", disabled=idx >= len(pending) - 1):
                st.session_state.review_idx = min(len(pending) - 1, idx + 1)
                st.rerun()

        st.divider()

        # Question display + editing
        with st.form(key=f"review_form_{q['id']}"):
            st.markdown(f"**Chapter:** {q.get('chapter_title', 'N/A')} | **Draft ID:** {q['id']}")

            edited_question = st.text_area("Question", value=q["question"], height=80)

            col_a, col_b = st.columns(2)
            with col_a:
                edited_a = st.text_input("Option A", value=q["option_a"])
                edited_c = st.text_input("Option C", value=q["option_c"])
            with col_b:
                edited_b = st.text_input("Option B", value=q["option_b"])
                edited_d = st.text_input("Option D", value=q["option_d"])

            col_ans, col_diff, col_topic = st.columns(3)
            with col_ans:
                edited_answer = st.selectbox(
                    "Correct Answer",
                    ["A", "B", "C", "D"],
                    index=["A", "B", "C", "D"].index(q["correct_answer"]),
                )
            with col_diff:
                edited_difficulty = st.selectbox(
                    "Difficulty",
                    ["easy", "medium", "hard"],
                    index=["easy", "medium", "hard"].index(q["difficulty"]),
                )
            with col_topic:
                edited_topic = st.text_input("Topic", value=q.get("topic", ""))

            edited_explanation = st.text_area("Explanation", value=q["explanation"], height=80)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                approve_btn = st.form_submit_button("✅ Approve", type="primary", use_container_width=True)
            with btn_col2:
                reject_btn = st.form_submit_button("❌ Reject", use_container_width=True)

        if approve_btn:
            edited_data = {
                "question": edited_question,
                "option_a": edited_a,
                "option_b": edited_b,
                "option_c": edited_c,
                "option_d": edited_d,
                "correct_answer": edited_answer,
                "difficulty": edited_difficulty,
                "topic": edited_topic,
                "explanation": edited_explanation,
            }
            approve(q["id"], edited_data)
            st.success(f"Question {q['id']} approved!")
            # Stay at same index (next question shifts in)
            st.rerun()

        if reject_btn:
            reject(q["id"])
            st.warning(f"Question {q['id']} rejected.")
            st.rerun()


# ─── TAB 3: LIBRARY ───────────────────────────────────────────────────────────
with tab_library:
    st.header("Approved Questions Library")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_topic = st.text_input("Filter by Topic", placeholder="e.g., Kurukshetra")
    with filter_col2:
        filter_difficulty = st.selectbox("Filter by Difficulty", ["", "easy", "medium", "hard"])

    questions = get_library(topic=filter_topic, difficulty=filter_difficulty)

    if not questions:
        st.info("No approved questions yet. Approve some in the Review tab!")
    else:
        st.markdown(f"**{len(questions)} approved question(s)**")

        export_col1, export_col2 = st.columns([3, 1])
        with export_col2:
            json_data = export_to_json(questions)
            st.download_button(
                label="⬇️ Export JSON",
                data=json_data,
                file_name="approved_questions.json",
                mime="application/json",
                use_container_width=True,
            )

        for i, q in enumerate(questions, 1):
            with st.expander(f"Q{i}: {q['question'][:80]}{'...' if len(q['question']) > 80 else ''}"):
                st.markdown(f"**Chapter:** {q.get('chapter_title', 'N/A')}")
                st.markdown(f"**Difficulty:** `{q['difficulty']}` | **Topic:** `{q.get('topic', '')}`")
                st.divider()
                st.markdown(f"**A:** {q['option_a']}")
                st.markdown(f"**B:** {q['option_b']}")
                st.markdown(f"**C:** {q['option_c']}")
                st.markdown(f"**D:** {q['option_d']}")
                st.markdown(f"✅ **Correct: {q['correct_answer']}**")
                st.markdown(f"💬 **Explanation:** {q['explanation']}")
                st.caption(f"Approved at: {q['approved_at']}")
