"""KIWi chat frontend. Start with: python -m streamlit run app.py"""

import base64
import hashlib
import importlib
import re
from time import perf_counter, sleep
from kiwi_logging import logger
from response_format import prepare_response
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse

import streamlit as st

THWS_LOGO = Path(__file__).parent / "images" / "thws_logo.png"
AVATARS = {
    "default": Path(__file__).parent / "images" / "KIWi_Avatar.png",
    "greeting": Path(__file__).parent / "images" / "KIWI_Waving.png",
    "loading": Path(__file__).parent / "images" / "KIWi_Meditating.png",
    "answer": Path(__file__).parent / "images" / "KIWi_Holding_book.png",
}


@st.cache_resource(show_spinner=False)
def load_backend(revision):
    """Refresh imported backend code when its source changes during development."""
    import response_format
    import rag

    importlib.reload(response_format)
    backend = importlib.reload(rag)
    logger.info("Backend revision %s loaded", revision[:12])
    return backend.answer


def backend_revision():
    root = Path(__file__).parent
    return hashlib.sha256(
        (root / "rag.py").read_bytes() + (root / "response_format.py").read_bytes()
    ).hexdigest()


def greeting_language(text):
    """Only standalone greetings bypass retrieval, never greetings plus questions."""
    normalized = re.sub(r"[^\w\s]", "", text.casefold()).strip()
    normalized = " ".join(normalized.split())
    normalized = re.sub(r"\s+kiwi$", "", normalized)
    if normalized in {"hi", "hello", "hey", "hi there", "hello there"}:
        return "en"
    if normalized in {"hallo", "guten morgen", "guten tag", "guten abend", "moin", "servus"}:
        return "de"
    return None


def save_reply(reply):
    st.session_state.messages.append(reply)
    st.session_state.chats[st.session_state.active_chat] = {
        "title": st.session_state.messages[0]["content"],
        "messages": st.session_state.messages,
    }


def finish_title_transition(started):
    """Keep fast responses from replacing the animated header mid-transition."""
    if started is not None:
        remaining = 1.4 - (perf_counter() - started)
        if remaining > 0:
            sleep(remaining)

st.set_page_config(
    page_title="KIWi | THWS CampusPortal",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'kiwi.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.session_state.setdefault("messages", [])
st.session_state.setdefault("chats", {})
st.session_state.setdefault("active_chat", uuid4().hex)


def select_chat(chat_id):
    st.session_state.active_chat = chat_id
    st.session_state.messages = st.session_state.chats[chat_id]["messages"]


def new_chat():
    st.session_state.messages = []
    st.session_state.active_chat = uuid4().hex


with st.sidebar:
    with st.container(key="kiwi_navigation"):
        with st.container(key="kiwi_nav_top"):
            logo_data = base64.b64encode(THWS_LOGO.read_bytes()).decode("ascii")
            st.markdown(
                f'<div class="kiwi-nav-brand"><img src="data:image/png;base64,{logo_data}" '
                'alt="THWS"><span>CampusPortal assistant</span></div>',
                unsafe_allow_html=True,
            )
            st.button("New chat", icon=":material/edit_square:", key="sidebar_new_chat",
                      use_container_width=True, on_click=new_chat)
        with st.container(key="kiwi_nav_history"):
            st.markdown('<div class="kiwi-history-label">Conversations</div>', unsafe_allow_html=True)
            if not st.session_state.chats:
                st.markdown('<div class="kiwi-history-empty">No conversations yet.<br>Start by asking KIWi a question.</div>', unsafe_allow_html=True)
            for chat_id, chat in reversed(list(st.session_state.chats.items())):
                label = chat["title"].replace("\n", " ")
                st.button(
                    label, key=f"chat_{chat_id}",
                    icon=":material/chat_bubble_outline:",
                    type="primary" if chat_id == st.session_state.active_chat else "secondary",
                    use_container_width=True, on_click=select_chat, args=(chat_id,),
                )
        st.markdown('<div class="kiwi-nav-footer"><strong>KIWi</strong><span>KI-Wissensassistenz</span></div>', unsafe_allow_html=True)

title_slot = st.empty()


def render_title(mode):
    avatar_html = ""
    if mode == "welcome":
        image_data = base64.b64encode(AVATARS["default"].read_bytes()).decode("ascii")
        avatar_html = (
            f'<img class="kiwi-title-avatar" src="data:image/png;base64,{image_data}" '
            'alt="KIWi">'
        )
    title_slot.markdown(
        f'<div class="kiwi-chat-title kiwi-title-{mode}">'
        + avatar_html +
        '<h1><span class="kiwi-name-orange" style="color:#ff6b00">KI-WI</span>'
        '<span class="kiwi-name-navy" style="color:#142d4e">ssensassistenz</span></h1></div>',
        unsafe_allow_html=True,
    )


render_title("compact" if st.session_state.messages else "welcome")


def render_message(message):
    """Keep each answer and its numbered retrieval sources together."""
    if message["role"] == "assistant":
        content, sources = prepare_response(message["content"], message.get("sources", []))
        message = {**message, "content": content, "sources": sources}
    state = message.get("avatar", "default" if message.get("error") else "answer")
    avatar = str(AVATARS.get(state, AVATARS["default"])) if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        role_class = "assistant" if message["role"] == "assistant" else "user"
        st.markdown(f'<span class="kiwi-role-{role_class}"></span>', unsafe_allow_html=True)
        st.markdown(message["content"])
        if message.get("error"):
            st.error("Check that Ollama is running, the configured models are installed, and the knowledge index is ready. Then submit your question again.")
        if message.get("sources"):
            with st.expander("Sources and retrieved passages"):
                for number, source in enumerate(message["sources"], 1):
                    st.write(f"[{number}] {source['source']}")
                    details = [f"Record: {source['record_id']}"]
                    if source.get("section"):
                        details.append(source["section"])
                    if source.get("source_last_verified"):
                        details.append(f"Verified: {source['source_last_verified']}")
                    st.caption(" · ".join(details))
                    url = source.get("source_url", "")
                    parsed = urlparse(url)
                    if parsed.scheme in {"http", "https"} and parsed.netloc:
                        st.link_button("Open source", url)
                    st.text(source["text"])
                    if number < len(message["sources"]):
                        st.divider()


for message in st.session_state.messages:
    render_message(message)

# A single top-level input stays pinned to the bottom in both views.
question = st.chat_input("Message KIWi…", key="chat_input")

if question and question.strip():
    title_transition_started = None
    if not st.session_state.messages:
        render_title("shrinking")
        title_transition_started = perf_counter()
        # Finish the title transition before showing the conversation pose.
        finish_title_transition(title_transition_started)
        render_title("compact")
    question = question.strip()
    request_id = uuid4().hex[:8]
    request_started = perf_counter()
    logger.info("Request %s received (%d characters); showing loading animation", request_id, len(question))
    user_message = {"role": "user", "content": question}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    language = greeting_language(question)
    if language:
        save_reply({
            "role": "assistant",
            "avatar": "greeting",
            "content": (
                "Hallo! Ich bin KIWi. Wie kann ich dir bei Fragen zur THWS helfen?"
                if language == "de" else
                "Hi! I'm KIWi. How can I help you with THWS today?"
            ),
        })
        logger.info("Request %s: greeting answered with waving avatar", request_id)
        finish_title_transition(title_transition_started)
        st.rerun()

    pending = st.empty()
    # Browser-side animation continues while the synchronous RAG call runs.
    # A fresh element starts the five-second message timer for each request.
    logo_data = base64.b64encode(AVATARS["loading"].read_bytes()).decode("ascii")
    pending.markdown(f'''
        <div class="kiwi-loading" role="status" aria-live="polite">
            <div class="kiwi-loading-avatar">
                <img src="data:image/png;base64,{logo_data}" alt="KIWi">
            </div>
            <div class="kiwi-loading-bubble">
                <div class="kiwi-loading-labels">
                    <span class="kiwi-loading-initial">KIWi is looking that up for you</span>
                    <span class="kiwi-loading-long">Hang tight, KIWi is at work</span>
                </div>
                <div class="kiwi-typing-dots" aria-hidden="true">
                    <i></i><i></i><i></i>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    try:
        logger.info("Request %s: loading backend", request_id)
        # Load on demand so the interface also opens before backend setup.
        # Importing rag does not start its guarded terminal input loop.
        answer = load_backend(backend_revision())

        text, hits = answer(question, history=st.session_state.messages[:-1])
        reply = {"role": "assistant", "content": text, "sources": hits, "avatar": "answer"}
        logger.info("Request %s completed in %.2fs; displaying response", request_id, perf_counter() - request_started)
    except Exception:
        logger.exception("Request %s failed after %.2fs", request_id, perf_counter() - request_started)
        reply = {
            "role": "assistant",
            "content": "I couldn't complete this request. Please try again once the service is ready.",
            "error": True,
        }
    finally:
        pending.empty()

    save_reply(reply)
    finish_title_transition(title_transition_started)
    st.rerun()
