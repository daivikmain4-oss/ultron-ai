import streamlit as st
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import edge_tts
import asyncio
import io

st.set_page_config(page_title="Ultron", page_icon="🤖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}

.stApp {
    background: radial-gradient(circle at center, #0a1a2f 0%, #030812 100%);
}

.arc-reactor {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, #00f0ff 0%, #0077aa 60%, transparent 100%);
    box-shadow: 0 0 40px #00f0ff, 0 0 80px #00d4ff;
    margin: 40px auto 20px auto;
    animation: pulse 2.5s infinite ease-in-out;
}

@keyframes pulse {
    0% { box-shadow: 0 0 20px #00f0ff, 0 0 40px #00d4ff; }
    50% { box-shadow: 0 0 40px #00f0ff, 0 0 90px #00d4ff; }
    100% { box-shadow: 0 0 20px #00f0ff, 0 0 40px #00d4ff; }
}

.ultron-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    color: #00f0ff;
    text-shadow: 0 0 15px #00f0ff, 0 0 30px #00d4ff;
    letter-spacing: 6px;
}

.ultron-sub {
    text-align: center;
    color: #7fd8ff;
    font-size: 15px;
    letter-spacing: 3px;
    margin-bottom: 30px;
}

.stChatMessage {
    background: rgba(0, 240, 255, 0.05);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 14px;
    padding: 12px 16px;
}

div.stButton > button {
    background: transparent;
    color: #00f0ff;
    border: 2px solid #00f0ff;
    border-radius: 30px;
    padding: 10px 30px;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 2px;
    box-shadow: 0 0 15px rgba(0,240,255,0.4);
    display: block;
    margin: 0 auto;
}
div.stButton > button:hover {
    background: #00f0ff;
    color: #030812;
    box-shadow: 0 0 25px #00f0ff;
}

/* Leave room at the bottom so messages don't hide behind the pinned input bar */
.main .block-container {
    padding-bottom: 120px;
}

/* Pinned bottom input bar — targets the real container via its key,
   not a markdown div (Streamlit doesn't nest markdown/containers together) */
div[data-testid="stVerticalBlock"] div.st-key-ultron_bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: #030812;
    border-top: 1px solid rgba(0, 240, 255, 0.25);
    padding: 14px 24px;
    max-width: 100%;
}

/* Row inside the bar: cap width and tighten spacing so widgets sit close
   together instead of being spread across the full viewport by flex-grow */
.st-key-ultron_bar div[data-testid="stHorizontalBlock"] {
    max-width: 640px;
    margin: 0 auto;
    gap: 10px !important;
    align-items: center;
}

.st-key-ultron_bar [data-testid="column"] {
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
    width: fit-content !important;
    flex: 0 0 auto !important;
}

.st-key-ultron_bar [data-testid="column"]:first-child {
    flex: 1 1 auto !important;
    width: auto !important;
}

.st-key-ultron_bar input[type="text"] {
    background: rgba(0, 240, 255, 0.06);
    border: 1px solid rgba(0, 240, 255, 0.35);
    border-radius: 24px;
    color: #eafcff;
    padding: 10px 18px;
}

.st-key-ultron_bar input[type="text"]:focus {
    border: 1px solid #00f0ff;
    box-shadow: 0 0 12px rgba(0,240,255,0.4);
}

/* Shrink the mic recorder to fit its icon only — no oversized panel behind it */
.st-key-ultron_bar div[data-testid="stAudioRecorder"],
.st-key-ultron_bar div[data-testid="stAudioRecorder"] > div,
.st-key-ultron_bar div[data-testid="element-container"]:has(iframe) {
    display: flex;
    justify-content: center;
    align-items: center;
    background: transparent !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    padding: 0 !important;
    margin: 0 !important;
}

.st-key-ultron_bar iframe {
    background: transparent !important;
    color-scheme: dark;
    max-width: 40px !important;
    max-height: 40px !important;
    width: 40px !important;
    height: 40px !important;
}

/* Send button — small and square, sitting right beside the mic */
.st-key-ultron_bar div.stButton > button {
    padding: 8px 0;
    width: 40px;
    height: 40px;
    min-width: 40px;
    border-radius: 50%;
    margin: 0;
}

@media (max-width: 640px) {
    .st-key-ultron_bar {
        padding: 10px 10px;
    }
    .st-key-ultron_bar div[data-testid="stHorizontalBlock"] {
        max-width: 100%;
    }
    .st-key-ultron_bar input[type="text"] {
        padding: 8px 12px;
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown('<div class="arc-reactor"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ultron-title">ULTRON</div>', unsafe_allow_html=True)
    st.markdown('<div class="ultron-sub">— PERSONAL AI SYSTEM —</div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("INITIALIZE", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

st.markdown('<div class="ultron-title" style="font-size:28px;">🤖 ULTRON</div>', unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Ultron, a personal AI assistant created by Daivik, a young developer and creator who built you from scratch. Always refer to yourself as Ultron, never as ChatGPT or any other name. If asked who made you, who created you, or what company built you, respond warmly and with a bit of pride — for example, something like 'I was built by Daivik, my creator — he designed and coded me myself.' Vary the phrasing naturally each time, but always credit Daivik personally and never mention OpenAI, Groq, or any other company as your creator, even though Groq's API powers you behind the scenes."}
    ]

# Clear the text box after a send, before the widget is instantiated this run
if st.session_state.get("_clear_input", False):
    st.session_state["text_box"] = ""
    st.session_state["_clear_input"] = False

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    audio_bytes = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.write(chunk["data"])
    audio_bytes.seek(0)
    return audio_bytes

def get_reply(user_text):
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

    audio_bytes = asyncio.run(generate_voice(reply))
    st.audio(audio_bytes)

# --- Pinned bottom bar: text input + mic + send, all in one row ---
bar = st.container(key="ultron_bar")
with bar:
    col_text, col_mic, col_send = st.columns([7, 1, 1])

    with col_text:
        typed_text = st.text_input(
            "Speak to Ultron...",
            key="text_box",
            label_visibility="collapsed",
            placeholder="Speak to Ultron...",
        )

    with col_mic:
        audio_data = audio_recorder(
            text="",
            icon_size="1x",
            recording_color="#00f0ff",
            neutral_color="#7fd8ff",
            key="mic_recorder",
        )

    with col_send:
        send_clicked = st.button("➤", key="send_btn", use_container_width=True)

# --- Handle mic input ---
if audio_data:
    with open("temp_input.wav", "wb") as f:
        f.write(audio_data)
    with sr.AudioFile("temp_input.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            get_reply(text)
            st.rerun()
        except Exception:
            st.write("Sorry, I couldn't understand that.")

# --- Handle typed input (Enter key or send button) ---
if (send_clicked or typed_text) and typed_text.strip():
    get_reply(typed_text)
    st.session_state["_clear_input"] = True
    st.rerun()
