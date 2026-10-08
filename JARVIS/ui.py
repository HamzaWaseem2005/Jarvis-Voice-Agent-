import html
import io
import os
import re
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PIN_WORKING_DIR = False
if PIN_WORKING_DIR:
    os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import asyncio
import traceback

import pyttsx3
import speech_recognition as sr
import streamlit as st

from AGENT.agent import run_agent

PROJECT_NAME = "Jarvis Voice Agent"
PROJECT_TAGLINE = "A voice-first AI assistant that listens, thinks and answers out loud."
DEVELOPER = "Hamza"
PROJECT_FEATURES = [
    ("Voice input", "Speak naturally and Jarvis transcribes it with Google Speech Recognition."),
    ("ReAct agent", "The agent reasons step by step and uses tools to complete your request."),
    ("Conversation memory", "Replies stay consistent per user and conversation thread."),
    ("Voice replies", "Every answer is spoken back to you with text-to-speech."),
]
FALLBACK_STACK = [
    "Python",
    "Streamlit",
    "SpeechRecognition",
    "Google Speech API",
    "pyttsx3",
    "sounddevice",
    "soundfile",
    "NumPy",
]
EXTRA_STACK = []


def load_tech_stack() -> list[str]:
    path = os.path.join(PROJECT_ROOT, "requirements.txt")
    names = []
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("#", "-")):
                    continue
                name = re.split(r"[<>=!~\[;@ ]", line, maxsplit=1)[0].strip()
                if name:
                    names.append(name)
    stack = names if names else FALLBACK_STACK
    merged = ["Python"] + [n for n in stack if n.lower() != "python"] + EXTRA_STACK
    seen, result = set(), []
    for n in merged:
        if n.lower() not in seen:
            seen.add(n.lower())
            result.append(n)
    return result


TECH_STACK = load_tech_stack()

st.set_page_config(
    page_title="Jarvis",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Manrope:wght@400;500;600&display=swap');

:root {
    --bg-deep: #06152A;
    --bg-mid: #0B2342;
    --panel: rgba(18, 52, 92, 0.45);
    --line: rgba(111, 214, 255, 0.22);
    --cyan: #5BDCFF;
    --cyan-soft: #9BE9FF;
    --amber: #FFB547;
    --text: #E6F4FF;
    --muted: #8FB0CC;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background:
        radial-gradient(1200px 600px at 50% -10%, #12396B 0%, transparent 60%),
        linear-gradient(180deg, var(--bg-mid) 0%, var(--bg-deep) 100%) !important;
    color: var(--text);
    font-family: 'Manrope', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem; max-width: 760px; }

.j-title {
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 3.2rem;
    letter-spacing: 0.35em;
    margin: 0;
    padding-left: 0.35em;
    background: linear-gradient(90deg, #7FE4FF, #E6F4FF 50%, #7FE4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.j-sub {
    text-align: center;
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0.2rem 0 0.8rem 0;
}

.chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.45rem; margin-bottom: 0.4rem; }
.chip {
    font-size: 0.8rem; padding: 0.25rem 0.7rem; border-radius: 999px;
    border: 1px solid var(--line); background: var(--panel); color: var(--cyan-soft);
}

.orb-wrap { display: flex; flex-direction: column; align-items: center; margin: 0.6rem 0 0.2rem 0; }
.orb { position: relative; width: 190px; height: 190px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.orb .core {
    width: 74px; height: 74px; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #FFFFFF 0%, var(--cyan-soft) 35%, var(--cyan) 70%);
    box-shadow: 0 0 40px 10px rgba(91, 220, 255, 0.55);
}
.orb .ring { position: absolute; border-radius: 50%; border: 2px solid var(--cyan); }
.orb .r1 { inset: 0; border-style: dashed; opacity: 0.55; }
.orb .r2 { inset: 22px; border-color: var(--cyan-soft); border-top-color: transparent; border-bottom-color: transparent; opacity: 0.9; }
.orb .r3 { inset: 44px; opacity: 0.35; }

.orb.idle .r1 { animation: spin 40s linear infinite; }
.orb.idle .r2 { animation: spin 18s linear infinite reverse; }
.orb.idle .core { animation: breathe 4s ease-in-out infinite; }

.orb.thinking .r1 { animation: spin 6s linear infinite; }
.orb.thinking .r2 { animation: spin 1.6s linear infinite reverse; }
.orb.thinking .core { animation: breathe 1.2s ease-in-out infinite; }

.orb.speaking .ring { border-color: var(--amber); }
.orb.speaking .r1 { animation: spin 14s linear infinite; }
.orb.speaking .r2 { animation: spin 5s linear infinite reverse; }
.orb.speaking .core {
    background: radial-gradient(circle at 35% 30%, #FFFFFF 0%, #FFE0A8 35%, var(--amber) 70%);
    box-shadow: 0 0 46px 12px rgba(255, 181, 71, 0.55);
    animation: pulse 0.9s ease-in-out infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes breathe { 0%,100% { transform: scale(0.94); } 50% { transform: scale(1.06); } }
@keyframes pulse { 0%,100% { transform: scale(0.92); } 50% { transform: scale(1.14); } }

@media (prefers-reduced-motion: reduce) {
    .orb .ring, .orb .core { animation: none !important; }
}

.status { margin-top: 0.8rem; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.15rem; letter-spacing: 0.12em; color: var(--cyan-soft); }
.status.speaking { color: var(--amber); }

[data-testid="stAudioInput"] { background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 0.4rem; margin-top: 0.8rem; }

.chat { display: flex; flex-direction: column; gap: 0.7rem; margin-top: 1.2rem; }
.msg { max-width: 86%; padding: 0.75rem 1rem; line-height: 1.55; font-size: 0.98rem; }
.msg .who { display: block; font-size: 0.78rem; color: var(--muted); margin-bottom: 0.15rem; }
.msg.user { align-self: flex-end; background: rgba(91, 220, 255, 0.14); border: 1px solid var(--line); border-radius: 16px 16px 4px 16px; }
.msg.bot { align-self: flex-start; background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--cyan); border-radius: 4px 16px 16px 16px; }
.empty { text-align: center; color: var(--muted); margin-top: 1.4rem; font-size: 0.95rem; }

[data-testid="stChatInput"] { background: var(--panel); border-radius: 14px; }
.stButton > button { border-radius: 12px; border: 1px solid var(--line); background: var(--panel); color: var(--text); }
.stButton > button:hover { border-color: var(--cyan); color: var(--cyan-soft); }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #0A2547 0%, #061529 100%); border-right: 1px solid var(--line); }
.sb-brand { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.2rem; }
.sb-dot {
    width: 38px; height: 38px; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #fff 0%, var(--cyan-soft) 35%, var(--cyan) 75%);
    box-shadow: 0 0 18px 4px rgba(91, 220, 255, 0.5);
}
.sb-name { font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.3rem; letter-spacing: 0.08em; line-height: 1.1; }
.sb-tag { color: var(--muted); font-size: 0.82rem; margin-bottom: 0.9rem; }
.sb-card { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 0.8rem 0.9rem; margin: 0.5rem 0 0.9rem 0; }
.sb-card h4 { margin: 0 0 0.5rem 0; font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; letter-spacing: 0.06em; color: var(--cyan-soft); }
.sb-feat { margin-bottom: 0.55rem; font-size: 0.84rem; color: var(--muted); line-height: 1.4; }
.sb-feat b { display: block; color: var(--text); font-weight: 600; font-size: 0.88rem; }
.sb-stats { display: flex; gap: 0.6rem; }
.sb-stat { flex: 1; text-align: center; padding: 0.5rem 0; border-radius: 10px; background: rgba(91, 220, 255, 0.08); }
.sb-stat span { display: block; font-family: 'Rajdhani', sans-serif; font-size: 1.6rem; font-weight: 700; color: var(--cyan); line-height: 1; }
.sb-stat small { color: var(--muted); font-size: 0.75rem; }
.sb-foot { text-align: center; color: var(--muted); font-size: 0.78rem; margin-top: 1rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

defaults = {
    "messages": [],
    "mic_key": 0,
    "pending_audio": None,
    "orb_state": "idle",
    "notice": None,
    "last_error": None,
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
bot_msgs = sum(1 for m in st.session_state.messages if m["role"] == "bot")

with st.sidebar:
    st.markdown(
        f"""
        <div class="sb-brand">
            <div class="sb-dot"></div>
            <div class="sb-name">{html.escape(PROJECT_NAME)}</div>
        </div>
        <div class="sb-tag">{html.escape(PROJECT_TAGLINE)}</div>
        """,
        unsafe_allow_html=True,
    )

    features_html = "".join(
        f"<div class='sb-feat'><b>{html.escape(t)}</b>{html.escape(d)}</div>"
        for t, d in PROJECT_FEATURES
    )
    st.markdown(
        f"<div class='sb-card'><h4>What Jarvis can do</h4>{features_html}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sb-card">
            <h4>This session</h4>
            <div class="sb-stats">
                <div class="sb-stat"><span>{user_msgs}</span><small>Questions</small></div>
                <div class="sb-stat"><span>{bot_msgs}</span><small>Replies</small></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sb-card'><h4>Settings</h4></div>", unsafe_allow_html=True)
    user_id = st.text_input("User ID", value="hamza")
    thread_id = st.text_input("Conversation ID", value="voice_session_4")
    speak_replies = st.toggle("Speak replies aloud", value=True)
    speech_rate = st.slider("Voice speed", min_value=120, max_value=240, value=175, step=5)
    language = st.selectbox("Speech language", ["en-US", "en-GB", "en-IN", "ur-PK"], index=0)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_audio = None
        st.session_state.orb_state = "idle"
        st.rerun()

    st.markdown(
        f"""
        <div class="sb-card">
            <h4>Built with</h4>
            <div class="chips" style="justify-content:flex-start">
                {''.join(f'<span class="chip">{html.escape(t)}</span>' for t in TECH_STACK)}
            </div>
        </div>
        <div class="sb-foot">Developed by {html.escape(DEVELOPER)}</div>
        """,
        unsafe_allow_html=True,
    )


def transcribe(wav_bytes: bytes, lang: str) -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language=lang)
    except sr.UnknownValueError:
        st.session_state.notice = "I could not understand that. Please speak a little closer to the mic."
    except sr.RequestError as exc:
        st.session_state.notice = f"Speech service is unavailable right now: {exc}"
    return ""


def synthesize(text: str, rate: int) -> bytes | None:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        engine.stop()
        with open(tmp_path, "rb") as f:
            return f.read()
    except Exception as exc:
        st.session_state.notice = f"Voice output failed: {exc}"
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def render_orb(placeholder, state: str) -> None:
    labels = {
        "idle": "Ready. Tap the mic and speak.",
        "thinking": "Thinking...",
        "speaking": "Speaking...",
    }
    placeholder.markdown(
        f"""
        <div class="orb-wrap">
            <div class="orb {state}">
                <div class="ring r1"></div>
                <div class="ring r2"></div>
                <div class="ring r3"></div>
                <div class="core"></div>
            </div>
            <div class="status {state}">{labels[state]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_user_text(text: str, orb_placeholder) -> None:
    st.session_state.messages.append({"role": "user", "text": text})
    render_orb(orb_placeholder, "thinking")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        reply = run_agent(text, user_id=user_id.strip(), thread_id=thread_id.strip())
        st.session_state.last_error = None
    except Exception as exc:
        st.session_state.last_error = traceback.format_exc()
        print(st.session_state.last_error)
        reply = f"Something went wrong while processing your request: {exc}"

    reply = str(reply)
    st.session_state.messages.append({"role": "bot", "text": reply})

    if speak_replies:
        st.session_state.pending_audio = synthesize(reply, speech_rate)
        st.session_state.orb_state = "speaking" if st.session_state.pending_audio else "idle"
    else:
        st.session_state.orb_state = "idle"


st.markdown('<h1 class="j-title">JARVIS</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="j-sub">{html.escape(PROJECT_TAGLINE)}</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="chips">'
    '<span class="chip">Voice in</span>'
    '<span class="chip">AI agent</span>'
    '<span class="chip">Voice out</span>'
    "</div>",
    unsafe_allow_html=True,
)

orb_placeholder = st.empty()
render_orb(orb_placeholder, st.session_state.orb_state)

audio_file = st.audio_input(
    "Tap the mic to start and stop recording",
    key=f"mic_{st.session_state.mic_key}",
    label_visibility="collapsed",
)

if audio_file is not None:
    wav_bytes = audio_file.getvalue()
    render_orb(orb_placeholder, "thinking")
    spoken_text = transcribe(wav_bytes, language)
    if spoken_text:
        handle_user_text(spoken_text, orb_placeholder)
    st.session_state.mic_key += 1
    st.rerun()

typed = st.chat_input("Or type your message here")
if typed:
    handle_user_text(typed.strip(), orb_placeholder)
    st.rerun()

if st.session_state.notice:
    st.warning(st.session_state.notice)
    st.session_state.notice = None

if st.session_state.last_error:
    with st.expander("Technical details of the last error"):
        st.code(st.session_state.last_error, language="text")

if st.session_state.pending_audio:
    st.audio(st.session_state.pending_audio, format="audio/wav", autoplay=True)
    st.session_state.pending_audio = None
    st.session_state.orb_state = "idle"

if not st.session_state.messages:
    st.markdown(
        '<div class="empty">No messages yet. Try saying "What can you help me with?"</div>',
        unsafe_allow_html=True,
    )
else:
    bubbles = []
    for m in reversed(st.session_state.messages):
        role = "user" if m["role"] == "user" else "bot"
        who = "You" if role == "user" else "Jarvis"
        safe_text = html.escape(m["text"]).replace("\n", "<br>")
        bubbles.append(f'<div class="msg {role}"><span class="who">{who}</span>{safe_text}</div>')
    st.markdown(f'<div class="chat">{"".join(bubbles)}</div>', unsafe_allow_html=True)