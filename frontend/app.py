
import streamlit as st
import requests
import time

# ----------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="StudyMate | Study Coach",
    page_icon=":material/menu_book:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# STYLING
# ----------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #FAF7F2;
        color: #29342E;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    h1, h2, h3 {
        font-family: Georgia, serif;
        color: #29342E;
        letter-spacing: -0.5px;
    }

    [data-testid="stSidebar"] {
        background-color: #F0F0E8;
        border-right: 1px solid #D8D9CF;
    }

    .brand {
        font-family: Georgia, serif;
        font-size: 27px;
        font-weight: bold;
        color: #31594B;
        margin-bottom: 3px;
    }

    .brand-caption {
        color: #788076;
        font-size: 12px;
        margin-bottom: 20px;
    }

    .eyebrow {
        color: #31594B;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .welcome {
        padding: 26px 0;
        border-bottom: 1px solid #D8D9CF;
        margin-bottom: 25px;
    }

    .welcome h1 {
        font-size: 40px;
        margin-bottom: 12px;
    }

    .welcome p {
        color: #70776F;
        font-size: 15px;
        line-height: 1.7;
    }

    .note-panel {
        background: #FFFDF8;
        padding: 18px;
        border: 1px solid #DDDCD4;
        border-radius: 5px;
        margin: 18px 0;
    }

    .note-title {
        font-family: Georgia, serif;
        font-size: 19px;
        color: #29342E;
        margin-bottom: 8px;
    }

    .note-text {
        color: #767A70;
        font-size: 13px;
        line-height: 1.7;
    }

    [data-testid="stChatMessage"] {
        background: #FFFDF8;
        border: 1px solid #E1DFD6;
        border-radius: 5px;
        padding: 16px;
        margin-bottom: 12px;
    }

    div.stButton > button {
        border-radius: 5px;
        border: 1px solid #D3D8CF;
        font-weight: 500;
    }

    div.stButton > button:hover {
        border-color: #31594B;
        color: #31594B;
    }

    div.stButton > button[kind="primary"] {
        background-color: #31594B;
        color: white;
        border-color: #31594B;
    }

    .stChatInputContainer {
        border-radius: 5px;
    }

    .small-label {
        font-size: 11px;
        color: #788076;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .footer {
        margin-top: 30px;
        text-align: center;
        color: #8B9186;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# STUDY MODES
# ----------------------------------------

STUDY_MODES = {
    "Explain": {
        "icon": ":material/menu_book:",
        "description": "Learn through clear explanations."
    },
    "Quiz Me": {
        "icon": ":material/quiz:",
        "description": "Test your knowledge, one question at a time."
    },
    "Explain Like I'm 12": {
        "icon": ":material/lightbulb:",
        "description": "Understand concepts in simple language."
    },
    "Socratic": {
        "icon": ":material/forum:",
        "description": "Develop answers through guided questions."
    }
}

# ----------------------------------------
# SESSION STATE
# ----------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "memory" not in st.session_state:
    st.session_state.memory = None

if "study_mode" not in st.session_state:
    st.session_state.study_mode = "Explain"

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "response_time" not in st.session_state:
    st.session_state.response_time = None


# ----------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------

def new_conversation():
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.session_state.memory = None
    st.session_state.pending_prompt = None
    st.session_state.response_time = None


def select_suggestion(question):
    st.session_state.pending_prompt = question


# ----------------------------------------
# SIDEBAR
# ----------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="brand">StudyMate.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-caption">'
        'Your personal learning workspace'
        '</div>',
        unsafe_allow_html=True
    )

    st.button(
        "New conversation",
        icon=":material/add:",
        use_container_width=True,
        type="primary",
        on_click=new_conversation
    )

    st.divider()

    st.markdown("**Study mode**")

    st.radio(
        "Choose how to learn",
        options=list(STUDY_MODES.keys()),
        key="study_mode",
        label_visibility="collapsed"
    )

    current_mode = st.session_state.study_mode

    st.caption(
        STUDY_MODES[current_mode]["description"]
    )

    st.divider()

    # ------------------------------------
    # MEMORY DETAILS
    # ------------------------------------

    with st.expander(
        "Conversation details",
        icon=":material/database:"
    ):

        memory = st.session_state.memory

        if memory:

            retained = memory["retained_messages"]
            limit = memory["max_messages"]
            removed = memory["truncated_messages"]
            total = memory["total_messages"]

            st.write("**Context window**")
            st.progress(
                min(retained / limit, 1.0)
                if limit > 0 else 0
            )

            st.caption(
                f"{retained} of {limit} previous "
                "messages retained"
            )

            st.metric(
                "Messages processed",
                total
            )

            st.metric(
                "Older messages removed",
                removed
            )

            if memory["truncation_active"]:
                st.info(
                    "Older messages have been removed "
                    "from the model's conversation context."
                )
            else:
                st.caption(
                    "No messages have been truncated yet."
                )

        else:
            st.caption(
                "Start a conversation to see "
                "your memory information."
            )

        if st.session_state.conversation_id:

            st.divider()
            st.caption("Conversation ID")

            st.code(
                st.session_state.conversation_id,
                language=None
            )

        st.caption(
            "Memory statistics are returned by "
            "the FastAPI backend after each response. "
            "The next request includes these retained "
            "messages plus your new question."
        )

    st.divider()

    st.caption("Model: Gemini 3.1 Flash-Lite")
    st.caption("Backend: FastAPI")
    st.caption("Interface: Streamlit")


# ----------------------------------------
# MAIN HEADER
# ----------------------------------------

st.markdown(
    '<div class="eyebrow">'
    'STUDYMATE / STUDY WORKSPACE'
    '</div>',
    unsafe_allow_html=True
)

st.title("Your study session.")

st.caption(
    "A quiet space to explore ideas, "
    "practice concepts, and learn at your own pace."
)

st.divider()

# ----------------------------------------
# WELCOME SCREEN
# ----------------------------------------

if not st.session_state.messages:

    st.markdown("""
    <div class="welcome">
        <h1>What are we learning today?</h1>
        <p>
            Choose a learning mode and begin with
            any topic. StudyMate can explain ideas,
            test your knowledge, or guide you
            through difficult questions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Pick a learning approach")

    cols = st.columns(2)

    for index, (mode, details) in enumerate(
        STUDY_MODES.items()
    ):

        with cols[index % 2]:

            with st.container(border=True):

                st.markdown(
                    f"#### {mode}"
                )

                st.caption(
                    details["description"]
                )

                if st.button(
                    f"Use {mode}",
                    key=f"mode_button_{index}",
                    use_container_width=True
                ):
                    st.session_state.study_mode = mode
                    st.rerun()

    st.markdown("### Start with a question")

    suggestions = [
        "Explain how neural networks learn.",
        "Help me revise machine learning basics.",
        "Why is Python useful in data science?",
        "Help me understand overfitting."
    ]

    for index, question in enumerate(suggestions):

        st.button(
            question,
            key=f"suggestion_{index}",
            icon=":material/arrow_forward:",
            use_container_width=True,
            on_click=select_suggestion,
            args=(question,)
        )

# ----------------------------------------
# EXISTING CHAT HISTORY
# ----------------------------------------

else:

    st.markdown(
        f"**Current mode:** {st.session_state.study_mode}"
    )

    st.caption(
        "You can change the study mode in "
        "the sidebar without clearing this conversation."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ----------------------------------------
# CHAT INPUT
# ----------------------------------------

typed_prompt = st.chat_input(
    "Write your question here..."
)

# Pick a suggested question if one was clicked.
prompt = st.session_state.pending_prompt

if prompt is not None:
    st.session_state.pending_prompt = None
else:
    prompt = typed_prompt

# ----------------------------------------
# SEND MESSAGE TO FASTAPI
# ----------------------------------------

if prompt:

    selected_mode = st.session_state.study_mode

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking through your question..."):

            start_time = time.perf_counter()

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "conversation_id": (
                            st.session_state.conversation_id
                        ),
                        "mode": selected_mode
                    },
                    timeout=45
                )

                response.raise_for_status()

                data = response.json()

                reply = data["response"]
                conversation_id = data["conversation_id"]
                memory = data["memory"]

                if not isinstance(reply, str) or not reply.strip():
                    raise ValueError("Empty AI response")

                if not isinstance(conversation_id, str):
                    raise ValueError("Invalid conversation ID")

                if not isinstance(memory, dict):
                    raise ValueError("Invalid memory information")

                required_fields = (
                    "retained_messages",
                    "max_messages",
                    "total_messages",
                    "truncated_messages",
                    "truncation_active"
                )

                if not all(
                    field in memory
                    for field in required_fields
                ):
                    raise ValueError("Incomplete memory information")

                elapsed = time.perf_counter() - start_time

                # Update frontend session after success.
                st.session_state.conversation_id = (
                    conversation_id
                )

                st.session_state.memory = memory
                st.session_state.response_time = elapsed

                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt
                })

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })

                st.markdown(reply)

                st.caption(
                    f"Response time: {elapsed:.2f} seconds"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. The backend "
                    "may still have processed your message."
                )

                st.info(
                    "If this happens repeatedly, start "
                    "a new conversation before retrying."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to StudyMate's backend. "
                    "Check that FastAPI is running."
                )

            except requests.exceptions.HTTPError:

                status = response.status_code

                if status == 429:

                    st.warning(
                        "Gemini's API rate limit was reached. "
                        "Please try again later."
                    )

                elif status == 404:

                    st.error(
                        "This conversation is no longer "
                        "available on the server."
                    )

                    st.info(
                        "Click New conversation to begin again."
                    )

                elif status >= 500:

                    st.error(
                        "The AI service is temporarily "
                        "unavailable. Please try again."
                    )

                else:

                    st.error(
                        f"The request failed (HTTP {status})."
                    )

            except (
                ValueError,
                KeyError,
                TypeError
            ):

                st.error(
                    "The server returned an invalid response. "
                    "Please check the backend."
                )

            except requests.exceptions.RequestException:

                st.error(
                    "A network error occurred while "
                    "contacting the backend."
                )

# ----------------------------------------
# FOOTER
# ----------------------------------------

st.markdown("""
<div class="footer">
    StudyMate Study Coach
    · Learn with intention.
</div>
""", unsafe_allow_html=True)
