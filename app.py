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
        {"role": "system", "content": "You are Ultron, a helpful AI assistant. Always refer to yourself as Ultron, never as ChatGPT or any other name."}
    ]

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

mic_col, input_col = st.columns([1, 9])
with mic_col:
    audio_data = audio_recorder(text="", icon_size="1.5x", recording_color="#00f0ff", neutral_color="#7fd8ff")
with input_col:
    user_input = st.chat_input("Speak to Ultron...")

if audio_data:
    with open("temp_input.wav", "wb") as f:
        f.write(audio_data)
    with sr.AudioFile("temp_input.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            get_reply(text)
        except:
            st.write("Sorry, I couldn't understand that.")

if user_input:
    get_reply(user_input)