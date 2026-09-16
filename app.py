import os
import re
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PREMIUM COLORFUL CSS
# =========================================================

st.markdown(
    """
<style>

/* APP BACKGROUND */

.stApp {
    background-image:
        radial-gradient(
            circle at 5% 5%,
            rgba(99, 102, 241, 0.13),
            transparent 27%
        ),
        radial-gradient(
            circle at 94% 8%,
            rgba(14, 165, 233, 0.11),
            transparent 27%
        );
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}


/* TOP BAR */

header[data-testid="stHeader"] {
    background:
        linear-gradient(
            90deg,
            #172554,
            #312E81,
            #6D28D9
        ) !important;

    box-shadow:
        0 5px 18px
        rgba(15,23,42,0.18);
}


/* WHITE TOP BAR TEXT */

header[data-testid="stHeader"] button,
header[data-testid="stHeader"] span,
header[data-testid="stHeader"] p,
header[data-testid="stHeader"] svg {
    color: #FFFFFF !important;
}


/* SIDEBAR TITLES */

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}


/* SIDEBAR TEXT */

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #E2E8F0 !important;
}


/* SIDEBAR DIVIDERS */

section[data-testid="stSidebar"] hr {
    border-color:
        rgba(255,255,255,0.15);
}


/* SIDEBAR BUTTONS */

section[data-testid="stSidebar"]
div.stButton > button {
    background: #FFFFFF !important;
    color: #1E2A5A !important;

    border:
        1px solid
        rgba(255,255,255,0.40) !important;

    border-radius: 13px !important;

    min-height: 54px;

    font-size: 15px;
    font-weight: 750;

    box-shadow:
        0 7px 20px
        rgba(15,23,42,0.16);
}


/* SIDEBAR BUTTON TEXT */

section[data-testid="stSidebar"]
div.stButton > button * {
    color: #1E2A5A !important;
}


/* SIDEBAR BUTTON HOVER */

section[data-testid="stSidebar"]
div.stButton > button:hover {
    background: #EEF2FF !important;
    color: #4338CA !important;
    border-color: #A5B4FC !important;
}


/* TABS */

button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 700;
    padding-left: 22px;
    padding-right: 22px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #7C3AED !important;
}

div[data-baseweb="tab-highlight"] {
    background:
        linear-gradient(
            90deg,
            #6366F1,
            #A855F7
        ) !important;

    height: 3px !important;
}


/* DASHBOARD CARDS */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px;

    box-shadow:
        0 12px 32px
        rgba(15,23,42,0.08);
}


/* NORMAL BUTTONS */

div.stButton > button {
    border-radius: 11px;
    min-height: 44px;
    font-weight: 700;
}


/* GENERATE BUTTON */

div.stButton > button[kind="primary"] {
    background:
        linear-gradient(
            90deg,
            #4F46E5,
            #7C3AED,
            #9333EA
        ) !important;

    border: none !important;
    color: #FFFFFF !important;
}


/* TEXT AREA */

textarea {
    border-radius: 14px !important;
}


/* SELECT BOXES */

div[data-baseweb="select"] > div {
    border-radius: 11px;
}


/* RESPONSE LENGTH */

div[role="radiogroup"] {
    gap: 0.9rem;
}


/* ALERTS */

div[data-testid="stAlert"] {
    border-radius: 14px;
}


/* DOWNLOAD BUTTON */

div[data-testid="stDownloadButton"] button {
    width: 100%;
    border-radius: 11px;
}


/* PROGRESS BAR */

div[data-testid="stProgress"]
> div > div > div {
    background:
        linear-gradient(
            90deg,
            #4F46E5,
            #A855F7
        ) !important;
}


/* EXPANDERS */

details {
    border-radius: 13px !important;
}


/* HIDE FOOTER */

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# LOAD API KEY
# =========================================================

load_dotenv()

api_key = os.getenv(
    "GROQ_API_KEY"
)

if not api_key:

    st.error(
        "Groq API key not found. "
        "Please add GROQ_API_KEY "
        "to your .env file."
    )

    st.stop()


client = Groq(
    api_key=api_key
)


# =========================================================
# SESSION STATE
# =========================================================

if "study_input" not in st.session_state:
    st.session_state.study_input = ""

if "latest_response" not in st.session_state:
    st.session_state.latest_response = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_id" not in st.session_state:
    st.session_state.quiz_id = 0

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None


# =========================================================
# CALLBACKS
# =========================================================

def set_topic(topic):

    st.session_state.study_input = (
        topic
    )


def new_study():

    st.session_state.study_input = ""

    st.session_state.latest_response = ""

    st.session_state.quiz = None

    st.session_state.quiz_result = None

    st.session_state.quiz_id += 1


def clear_history():

    st.session_state.history = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "🎓 Study Buddy"
    )

    st.caption(
        "Your Generative AI "
        "learning workspace"
    )

    st.divider()


    st.write(
        "### Quick Actions"
    )


    st.button(
        "＋ New Study",
        use_container_width=True,
        on_click=new_study,
    )


    st.button(
        "🗑 Clear History",
        use_container_width=True,
        on_click=clear_history,
    )


    st.divider()


    st.write(
        "### AI Features"
    )

    st.write(
        "💡 Topic explanations"
    )

    st.write(
        "📝 Smart summaries"
    )

    st.write(
        "❓ Interactive quizzes"
    )

    st.write(
        "🧠 Revision flashcards"
    )


    st.divider()


    st.info(
        "Choose your settings "
        "inside the Dashboard tab "
        "and start learning."
    )


# =========================================================
# HEADER
# =========================================================

st.title(
    "🎓 AI Study Buddy"
)

st.caption(
    "Learn, revise and test yourself "
    "with Generative AI."
)


# =========================================================
# MAIN TABS
# =========================================================

dashboard_tab, quiz_tab, history_tab = (
    st.tabs(
        [
            "🏠 Dashboard",
            "🧩 Quiz",
            "📚 History",
        ]
    )
)


# =========================================================
# PROMPT BUILDER
# =========================================================

def build_prompt(
    selected_mode,
    text,
    selected_difficulty,
    selected_length,
):

    if selected_mode == "Explain Topic":

        return f"""
You are an expert educational tutor.

Explain the following topic to a
{selected_difficulty} learner.

Topic:
{text}

Response length:
{selected_length}

Requirements:
- Start with a simple definition.
- Explain step by step.
- Use clear headings.
- Give real-world examples.
- Highlight important concepts.
- Use bullet points where helpful.
- Finish with a short recap.
"""


    if selected_mode == "Summarize Notes":

        return f"""
You are an expert study assistant.

Summarize the following notes for a
{selected_difficulty} learner.

Notes:
{text}

Response length:
{selected_length}

Requirements:
- Identify the main ideas.
- Remove unnecessary details.
- Use clear headings.
- Use bullet points.
- Highlight important terms.
- Finish with revision points.
"""


    if selected_mode == "Generate Quiz":

        return f"""
Create exactly 5 multiple-choice
questions about:

{text}

Difficulty:
{selected_difficulty}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0,
            "explanation": "Short explanation"
        }}
    ]
}}

Rules:
- Exactly 5 questions.
- Exactly 4 options each.
- answer must be 0, 1, 2 or 3.
- Include explanations.
- No Markdown.
- No code fences.
- JSON only.
"""


    return f"""
You are an educational
flashcard generator.

Create exactly 8 flashcards about:

{text}

Difficulty:
{selected_difficulty}

Response length:
{selected_length}

Format:

### Flashcard 1

**Question**

Question here

**Answer**

Answer here

Requirements:
- Focus on important concepts.
- Keep questions clear.
- Keep answers understandable.
- Make them useful for revision.
"""


# =========================================================
# QUIZ PARSER
# =========================================================

def parse_quiz(
    raw_text
):

    cleaned = (
        raw_text.strip()
    )


    cleaned = cleaned.replace(
        "```json",
        ""
    )


    cleaned = cleaned.replace(
        "```",
        ""
    )


    cleaned = (
        cleaned.strip()
    )


    match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL,
    )


    if match:

        cleaned = (
            match.group(0)
        )


    quiz_data = json.loads(
        cleaned
    )


    questions = quiz_data.get(
        "questions",
        []
    )


    if len(questions) != 5:

        raise ValueError(
            "Quiz must contain "
            "exactly 5 questions."
        )


    for question in questions:

        if not question.get(
            "question"
        ):

            raise ValueError(
                "Question text missing."
            )


        options = question.get(
            "options",
            []
        )


        if len(options) != 4:

            raise ValueError(
                "Every question needs "
                "four options."
            )


        if "answer" not in question:

            raise ValueError(
                "Correct answer missing."
            )


        answer_index = int(
            question["answer"]
        )


        if answer_index not in [
            0,
            1,
            2,
            3,
        ]:

            raise ValueError(
                "Invalid answer index."
            )


        question["answer"] = (
            answer_index
        )


    return quiz_data


# =========================================================
# DASHBOARD
# =========================================================

with dashboard_tab:

    # =====================================================
    # LEARNING CONTROL CARD
    # =====================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "⚙️ Learning Controls"
        )

        st.caption(
            "Customize the AI response "
            "before generating your material."
        )


        control1, control2, control3 = (
            st.columns(
                [1.2, 1, 1.3]
            )
        )


        with control1:

            mode = st.selectbox(
                "AI Mode",
                [
                    "Explain Topic",
                    "Summarize Notes",
                    "Generate Quiz",
                    "Generate Flashcards",
                ],
            )


        with control2:

            difficulty = (
                st.selectbox(
                    "Difficulty",
                    [
                        "Beginner",
                        "Intermediate",
                        "Advanced",
                    ],
                )
            )


        with control3:

            response_length = (
                st.radio(
                    "Response Length",
                    [
                        "Short",
                        "Medium",
                        "Detailed",
                    ],
                    horizontal=True,
                )
            )


    st.write("")


    # =====================================================
    # ASK AI
    # =====================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "✨ Ask your AI tutor"
        )

        st.caption(
            "Enter a topic, question "
            "or paste your study notes."
        )


        st.text_area(
            "What would you like to learn?",
            key="study_input",

            placeholder=(
                "Example: Explain "
                "Generative AI in simple "
                "words with examples..."
            ),

            height=185,
        )


        st.caption(
            "Try a quick topic"
        )


        q1, q2, q3, q4 = (
            st.columns(4)
        )


        with q1:

            st.button(
                "🤖 Generative AI",
                use_container_width=True,
                on_click=set_topic,

                args=(
                    "Explain Generative AI "
                    "in simple words with "
                    "real-world examples.",
                ),
            )


        with q2:

            st.button(
                "🔐 Cyber Security",
                use_container_width=True,
                on_click=set_topic,

                args=(
                    "Explain information "
                    "security and cyber security "
                    "for a beginner.",
                ),
            )


        with q3:

            st.button(
                "🌐 Networking",
                use_container_width=True,
                on_click=set_topic,

                args=(
                    "Explain computer networking "
                    "basics with simple examples.",
                ),
            )


        with q4:

            st.button(
                "📊 Data Science",
                use_container_width=True,
                on_click=set_topic,

                args=(
                    "Explain data science "
                    "and its real-world "
                    "applications.",
                ),
            )


        st.write("")


        generate_button = (
            st.button(
                "✨ Generate with AI",
                type="primary",
                use_container_width=True,
            )
        )


    # =====================================================
    # GENERATION
    # =====================================================

    if generate_button:

        clean_input = (
            st.session_state
            .study_input
            .strip()
        )


        if not clean_input:

            st.warning(
                "Please enter a topic "
                "or notes first."
            )


        else:

            prompt = build_prompt(
                mode,
                clean_input,
                difficulty,
                response_length,
            )


            try:

                with st.spinner(
                    "✨ AI is creating "
                    "your study material..."
                ):

                    response = (
                        client
                        .chat
                        .completions
                        .create(
                            model=(
                                "openai/"
                                "gpt-oss-120b"
                            ),

                            messages=[
                                {
                                    "role":
                                        "system",

                                    "content":
                                        (
                                            "You are AI "
                                            "Study Buddy, "
                                            "a professional, "
                                            "friendly and "
                                            "accurate "
                                            "educational tutor."
                                        ),
                                },

                                {
                                    "role":
                                        "user",

                                    "content":
                                        prompt,
                                },
                            ],

                            temperature=0.4,
                        )
                    )


                    answer = (
                        response
                        .choices[0]
                        .message
                        .content
                    )


                # =========================================
                # QUIZ
                # =========================================

                if (
                    mode
                    == "Generate Quiz"
                ):

                    try:

                        quiz_data = (
                            parse_quiz(
                                answer
                            )
                        )


                        st.session_state.quiz = (
                            quiz_data
                        )


                        st.session_state.quiz_id += 1


                        st.session_state.quiz_result = None


                        st.session_state.latest_response = ""


                        st.session_state.history.insert(
                            0,

                            {
                                "mode":
                                    mode,

                                "question":
                                    clean_input,

                                "answer":
                                    (
                                        "Interactive "
                                        "quiz generated."
                                    ),

                                "time":
                                    datetime.now().strftime(
                                        "%d %b %Y - %I:%M %p"
                                    ),
                            },
                        )


                    except Exception as quiz_error:

                        st.error(
                            "The AI returned "
                            "an invalid quiz. "
                            "Generate it again."
                        )

                        st.caption(
                            f"Technical detail: "
                            f"{quiz_error}"
                        )


                # =========================================
                # NORMAL CONTENT
                # =========================================

                else:

                    st.session_state.quiz = None

                    st.session_state.quiz_result = None


                    st.session_state.latest_response = (
                        answer
                    )


                    st.session_state.history.insert(
                        0,

                        {
                            "mode":
                                mode,

                            "question":
                                clean_input,

                            "answer":
                                answer,

                            "time":
                                datetime.now().strftime(
                                    "%d %b %Y - %I:%M %p"
                                ),
                        },
                    )


            except Exception as error:

                st.error(
                    f"Something went wrong: "
                    f"{error}"
                )


    # =====================================================
    # FULL WIDTH RESPONSE
    # =====================================================

    st.write("")


    with st.container(
        border=True
    ):

        st.subheader(
            "🧠 AI Response"
        )


        if (
            mode == "Generate Quiz"
            and st.session_state.quiz
        ):

            st.success(
                "✅ Your interactive "
                "quiz is ready!"
            )

            st.write(
                "Open the **🧩 Quiz** tab "
                "to answer the questions."
            )


        elif (
            st.session_state
            .latest_response
        ):

            st.markdown(
                st.session_state
                .latest_response
            )


            st.write("")


            st.download_button(
                "⬇ Download Study Notes",

                data=(
                    st.session_state
                    .latest_response
                ),

                file_name=(
                    "AI_Study_Buddy_Notes.txt"
                ),

                mime="text/plain",

                use_container_width=True,
            )


        else:

            st.info(
                "✨ Your generated AI "
                "response will appear here."
            )

            st.write(
                "Choose your learning mode, "
                "enter a topic and click "
                "**Generate with AI**."
            )


    # =====================================================
    # COLORED FEATURE CARDS
    # =====================================================

    st.write("")

    st.subheader(
        "🚀 Your AI Learning Toolkit"
    )


    f1, f2, f3, f4 = (
        st.columns(4)
    )


    with f1:

        st.info(
            "💡 **Explain**\n\n"
            "Understand complex topics "
            "with simple explanations "
            "and practical examples."
        )


    with f2:

        st.success(
            "📝 **Summarize**\n\n"
            "Turn long notes into "
            "clear and useful "
            "revision points."
        )


    with f3:

        st.warning(
            "❓ **Quiz**\n\n"
            "Test your knowledge "
            "with AI-generated "
            "interactive questions."
        )


    with f4:

        st.error(
            "🧠 **Flashcards**\n\n"
            "Create quick question "
            "and answer cards "
            "for memorization."
        )


# =========================================================
# QUIZ TAB
# =========================================================

with quiz_tab:

    st.subheader(
        "🧩 Interactive AI Quiz"
    )

    st.caption(
        "Generate your quiz from "
        "the Dashboard and complete it here."
    )


    if not st.session_state.quiz:

        st.info(
            "No quiz generated yet."
        )

        st.write(
            "Go to **🏠 Dashboard**, "
            "select **Generate Quiz**, "
            "enter a topic and generate it."
        )


    else:

        questions = (
            st.session_state.quiz.get(
                "questions",
                []
            )
        )


        st.success(
            "✅ Your quiz is ready."
        )


        user_answers = []


        with st.form(
            key=(
                f"quiz_form_"
                f"{st.session_state.quiz_id}"
            )
        ):

            for index, question in enumerate(
                questions
            ):

                with st.container(
                    border=True
                ):

                    st.subheader(
                        f"Question {index + 1}"
                    )


                    st.write(
                        question["question"]
                    )


                    answer = st.radio(
                        "Choose your answer",

                        question["options"],

                        index=None,

                        key=(
                            f"quiz_"
                            f"{st.session_state.quiz_id}_"
                            f"{index}"
                        ),
                    )


                    user_answers.append(
                        answer
                    )


            submit_quiz = (
                st.form_submit_button(
                    "✅ Submit Quiz",
                    use_container_width=True,
                )
            )


        if submit_quiz:

            if None in user_answers:

                st.warning(
                    "Please answer all "
                    "questions first."
                )


            else:

                score = 0

                details = []


                for index, question in enumerate(
                    questions
                ):

                    correct = (
                        question["options"][
                            int(
                                question["answer"]
                            )
                        ]
                    )


                    selected = (
                        user_answers[index]
                    )


                    is_correct = (
                        selected == correct
                    )


                    if is_correct:
                        score += 1


                    details.append(
                        {
                            "number":
                                index + 1,

                            "selected":
                                selected,

                            "correct":
                                correct,

                            "is_correct":
                                is_correct,

                            "explanation":
                                question.get(
                                    "explanation",
                                    (
                                        "No explanation "
                                        "available."
                                    ),
                                ),
                        }
                    )


                percentage = int(
                    (
                        score
                        / len(questions)
                    )
                    * 100
                )


                st.session_state.quiz_result = {
                    "score":
                        score,

                    "total":
                        len(questions),

                    "percentage":
                        percentage,

                    "details":
                        details,
                }


        if st.session_state.quiz_result:

            result = (
                st.session_state.quiz_result
            )


            st.divider()

            st.subheader(
                "📊 Quiz Results"
            )


            r1, r2 = st.columns(2)


            with r1:

                st.metric(
                    "Score",
                    (
                        f"{result['score']}"
                        f"/{result['total']}"
                    ),
                )


            with r2:

                st.metric(
                    "Percentage",
                    f"{result['percentage']}%",
                )


            st.progress(
                result["percentage"]
                / 100
            )


            for detail in result["details"]:

                if detail["is_correct"]:

                    st.success(
                        f"Question "
                        f"{detail['number']} "
                        f"— Correct ✅"
                    )


                else:

                    st.error(
                        f"Question "
                        f"{detail['number']} "
                        f"— Incorrect ❌"
                    )

                    st.write(
                        "**Your answer:** "
                        + detail["selected"]
                    )

                    st.write(
                        "**Correct answer:** "
                        + detail["correct"]
                    )


                st.caption(
                    "Explanation: "
                    + detail["explanation"]
                )


# =========================================================
# HISTORY TAB
# =========================================================

with history_tab:

    st.subheader(
        "📚 Study History"
    )

    st.caption(
        "Review your previous "
        "AI learning sessions."
    )


    if not st.session_state.history:

        st.info(
            "You do not have "
            "any study history yet."
        )


    else:

        for item in (
            st.session_state.history[:10]
        ):

            title = (
                item["question"][:70]
            )


            with st.expander(
                f"{item['mode']} • {title}"
            ):

                st.caption(
                    item["time"]
                )


                st.markdown(
                    "**Your Input**"
                )

                st.write(
                    item["question"]
                )


                st.markdown(
                    "**AI Response**"
                )

                st.markdown(
                    item["answer"]
                )