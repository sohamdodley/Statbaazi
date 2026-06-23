import streamlit as st
import json
import random
import os

st.set_page_config(page_title="StatBaazi", page_icon="🎮", layout="centered")

@st.cache_data
def load_data():
    possible_paths = [
        "data.json",
        os.path.join(os.path.dirname(__file__), "data.json"),
        "/mount/src/statbaazi/data.json",
        "/home/workdir/artifacts/data.json",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    st.error("Could not find data.json. Please make sure it is in the same folder as app.py.")
    st.stop()

data = load_data()

# Session state initialization
if "current_module" not in st.session_state:
    st.session_state.current_module = None
if "current_stage_index" not in st.session_state:
    st.session_state.current_stage_index = 0
if "stage_attempts" not in st.session_state:
    st.session_state.stage_attempts = 0
if "current_questions" not in st.session_state:
    st.session_state.current_questions = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""
if "last_was_correct" not in st.session_state:
    st.session_state.last_was_correct = False

STAGES = ["Beginners", "Moderate", "Expert", "Pro"]
MAX_ATTEMPTS = 3


def reset_stage():
    st.session_state.current_question_index = 0
    st.session_state.stage_attempts = 0
    st.session_state.show_feedback = False
    module = data["modules"][str(st.session_state.current_module)]
    stage_name = STAGES[st.session_state.current_stage_index]
    questions = module["stages"][stage_name]
    st.session_state.current_questions = random.sample(questions, min(5, len(questions)))


def next_stage():
    st.session_state.current_stage_index += 1
    st.session_state.stage_attempts = 0
    st.session_state.show_feedback = False
    if st.session_state.current_stage_index < len(STAGES):
        reset_stage()
    else:
        st.session_state.game_over = True


def advance_question():
    st.session_state.current_question_index += 1
    st.session_state.show_feedback = False
    if st.session_state.current_question_index >= 5:
        next_stage()
    st.rerun()


st.title("🎮 StatBaazi")
st.subheader("Statistics Mastery Game")

if st.session_state.current_module is None:
    st.write("### Select a Module to Start")
    module_choice = st.selectbox(
        "Choose Module",
        list(data["modules"].keys()),
        format_func=lambda x: f"Module {x} - {data['modules'][x]['name']}"
    )
    if st.button("Start Game", type="primary"):
        st.session_state.current_module = module_choice
        st.session_state.current_stage_index = 0
        st.session_state.game_over = False
        st.session_state.score = 0
        reset_stage()
        st.rerun()
else:
    if st.session_state.game_over:
        st.balloons()
        st.success("🎉 Congratulations! You completed the module!")
        st.info(f"**Final Score:** {st.session_state.score} points")
        if st.button("Play Again", type="primary"):
            st.session_state.current_module = None
            st.rerun()
        st.stop()

    if st.session_state.current_stage_index >= len(STAGES):
        st.session_state.game_over = True
        st.rerun()

    module = data["modules"][str(st.session_state.current_module)]
    current_stage = STAGES[st.session_state.current_stage_index]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Module {st.session_state.current_module}**")
    with col2:
        st.write(f"**Stage:** {current_stage}")
    with col3:
        st.write(f"**Score:** {st.session_state.score}")

    st.write(f"**Attempts Left:** {MAX_ATTEMPTS - st.session_state.stage_attempts}")

    progress = (st.session_state.current_question_index) / 5
    st.progress(progress, text=f"Question {st.session_state.current_question_index + 1} of 5")

    if len(st.session_state.current_questions) > 0:
        q = st.session_state.current_questions[st.session_state.current_question_index]

        if not st.session_state.show_feedback:
            st.markdown("### " + q["question"])
            for option in ["A", "B", "C", "D"]:
                if st.button(f"{option}. {q['options'][option]}", key=option):
                    if option == q["correct"]:
                        st.session_state.score += 10
                        st.session_state.last_feedback = "✅ Correct! +10 points"
                        st.session_state.last_was_correct = True
                        st.session_state.show_feedback = True
                        st.rerun()
                    else:
                        explanation = q["explanation_wrong"].get(option, "Wrong answer.")
                        st.session_state.last_feedback = f"❌ Wrong! {explanation}"
                        st.session_state.last_was_correct = False
                        st.session_state.stage_attempts += 1
                        st.session_state.show_feedback = True
                        st.rerun()
        else:
            if st.session_state.last_was_correct:
                st.success(st.session_state.last_feedback)
            else:
                st.error(st.session_state.last_feedback)

            if st.session_state.stage_attempts >= MAX_ATTEMPTS and not st.session_state.last_was_correct:
                st.error("You have used all 3 attempts for this stage.")
                if st.button("Retry This Stage", type="primary"):
                    reset_stage()
                    st.rerun()
            else:
                if st.button("Next Question →", type="primary"):
                    advance_question()
    else:
        st.error("No questions loaded. Please check your data.json file.")