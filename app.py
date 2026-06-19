import streamlit as st
import json
import random

st.set_page_config(page_title="StatBaazi", page_icon="📊", layout="centered")

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ====================== SESSION STATE ======================
if "current_module" not in st.session_state:
    st.session_state.current_module = None
if "current_stage_name" not in st.session_state:
    st.session_state.current_stage_name = None
if "stage_attempts" not in st.session_state:
    st.session_state.stage_attempts = 0
if "current_questions" not in st.session_state:
    st.session_state.current_questions = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0

STAGES = ["Beginners", "Moderate", "Expert", "Pro"]
MAX_ATTEMPTS = 3

def reset_stage(stage_name=None):
    """Reset for a specific stage (or current). Module 1 has no attempt limit."""
    if stage_name:
        st.session_state.current_stage_name = stage_name
    st.session_state.current_question_index = 0
    st.session_state.stage_attempts = 0
    if st.session_state.current_module and st.session_state.current_stage_name:
        module = data["modules"][str(st.session_state.current_module)]
        questions = module["stages"][st.session_state.current_stage_name]
        st.session_state.current_questions = random.sample(questions, min(5, len(questions)))

def complete_stage():
    """Mark stage as complete (no auto next)."""
    st.session_state.current_question_index = 5  # trigger complete UI
    st.session_state.stage_attempts = 0

# ====================== UI ======================
st.title("🎮 StatBaazi")
st.subheader("Statistics Mastery Game — Free Play Mode")

# ====================== MAIN MENU: ALL MODULES VISIBLE ======================
if st.session_state.current_module is None:
    st.write("### 📚 Choose any Module to begin (Free Play — not sequential)")

    # Show all modules as nice cards/buttons side by side
    module_items = list(data["modules"].items())
    cols = st.columns(len(module_items))

    for idx, (mod_id, mod_info) in enumerate(module_items):
        with cols[idx]:
            st.markdown(f"### Module {mod_id}")
            st.write(f"**{mod_info['name']}**")
            num_qs = sum(len(s) for s in mod_info["stages"].values())
            st.caption(f"{num_qs} questions across 4 stages")
            if st.button(f"▶ Start Module {mod_id}", key=f"start_mod_{mod_id}", use_container_width=True):
                st.session_state.current_module = mod_id
                st.session_state.current_stage_name = "Beginners"
                st.session_state.current_question_index = 0
                st.session_state.stage_attempts = 0
                st.session_state.score = 0
                reset_stage("Beginners")
                st.rerun()

    st.markdown("---")
    st.info("💡 **Tip:** This is free-play mode. Pick any module and any stage. Module 1 (Descriptive Statistics) has **unlimited attempts**.")
    st.stop()

# ====================== MODULE VIEW ======================
module = data["modules"][str(st.session_state.current_module)]
is_module1 = str(st.session_state.current_module) == "1"

# Top navigation
nav_col1, nav_col2, nav_col3 = st.columns([2, 3, 2])
with nav_col1:
    if st.button("🏠 Back to All Modules", use_container_width=True):
        st.session_state.current_module = None
        st.session_state.current_stage_name = None
        st.session_state.current_questions = []
        st.rerun()
with nav_col2:
    st.markdown(f"<h3 style='text-align:center'>Module {st.session_state.current_module} — {module['name']}</h3>", unsafe_allow_html=True)
with nav_col3:
    st.metric("Total Score", st.session_state.score, delta=None)

# ====================== STAGE SELECTOR (always visible, non-sequential) ======================
st.write("### Choose Stage")
stage_cols = st.columns(4)
for s_idx, stage in enumerate(STAGES):
    with stage_cols[s_idx]:
        is_active = (stage == st.session_state.current_stage_name)
        btn_type = "primary" if is_active else "secondary"
        if st.button(stage, key=f"nav_{stage}", type=btn_type, use_container_width=True):
            if stage != st.session_state.current_stage_name:
                reset_stage(stage)
                st.rerun()

current_stage = st.session_state.current_stage_name or "Beginners"

# ====================== ATTEMPTS / PROGRESS (conditional) ======================
if not is_module1:
    attempts_left = MAX_ATTEMPTS - st.session_state.stage_attempts
    st.write(f"**Attempts Left for this stage:** {attempts_left} / {MAX_ATTEMPTS}")
    if attempts_left <= 0:
        st.warning("No attempts remaining. Retry the stage or choose another.")
else:
    st.success("✅ **Module 1: Descriptive Statistics** — Unlimited attempts! Practice freely.")

if st.session_state.current_questions and st.session_state.current_question_index < 5:
    progress = st.session_state.current_question_index / 5
    st.progress(progress, text=f"Question {st.session_state.current_question_index + 1} of 5 in {current_stage}")

# ====================== STAGE COMPLETE SCREEN ======================
if st.session_state.current_question_index >= 5 and st.session_state.current_questions:
    st.balloons()
    st.success(f"🎉 **Stage Complete: {current_stage}**")
    st.info(f"You scored **+{min(5, st.session_state.current_question_index)}0 points** this stage (10 per correct answer).")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Replay this Stage", use_container_width=True):
            reset_stage(current_stage)
            st.rerun()
    with c2:
        if st.button("📖 Choose Different Stage", use_container_width=True):
            st.session_state.current_question_index = 0
            st.session_state.current_questions = []
            st.session_state.stage_attempts = 0
            st.rerun()
    with c3:
        if st.button("🏠 Back to Module Menu", use_container_width=True):
            st.session_state.current_module = None
            st.rerun()
    st.stop()

# ====================== QUESTION DISPLAY ======================
if len(st.session_state.current_questions) > 0 and st.session_state.current_question_index < 5:
    q = st.session_state.current_questions[st.session_state.current_question_index]

    st.markdown(f"### Q{st.session_state.current_question_index + 1}. {q['question']}")

    # Answer buttons
    for option in ["A", "B", "C", "D"]:
        if st.button(f"{option}. {q['options'][option]}", key=f"ans_{option}_{st.session_state.current_question_index}", use_container_width=True):
            if option == q["correct"]:
                st.success("✅ **Correct!** +10 points")
                st.session_state.score += 10
                st.session_state.current_question_index += 1
                # Auto-advance handled by index; complete screen shows at >=5
                st.rerun()
            else:
                explanation = q["explanation_wrong"].get(option, "That's not correct.")
                st.error(f"❌ **Wrong!** {explanation}")

                if not is_module1:
                    # Module 2+: count attempts and possibly lock
                    st.session_state.stage_attempts += 1
                    if st.session_state.stage_attempts >= MAX_ATTEMPTS:
                        st.error("🚫 You have used all 3 attempts for this stage.")
                        if st.button("🔄 Retry this Stage from Start", key="retry_stage"):
                            reset_stage(current_stage)
                            st.rerun()
                        if st.button("📚 Switch to another Stage", key="switch_stage"):
                            st.session_state.current_question_index = 0
                            st.session_state.current_questions = []
                            st.rerun()
                    else:
                        st.info(f"Attempts used: {st.session_state.stage_attempts}/{MAX_ATTEMPTS}")
                        if st.button("🔄 Try this question again", key="retry_q"):
                            st.rerun()
                else:
                    # Module 1: unlimited attempts — stay on same question
                    st.info("Module 1 has unlimited attempts. Review the explanation and try again!")
                    if st.button("🔄 Try this question again", key="retry_q_mod1"):
                        st.rerun()

else:
    if st.session_state.current_module:
        st.warning("No questions loaded for this stage. Please select a different stage or check data.")
        if st.button("Reload Stage"):
            reset_stage(current_stage)
            st.rerun()