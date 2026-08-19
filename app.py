import streamlit as st
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import edge_tts
import asyncio
import io

st.set_page_config(page_title="Ultron", page_icon="🤖")
st.title("🤖 Ultron")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are Ultron, a helpful AI assistant built by Daivik. Always refer to yourself as Ultron, never as ChatGPT or any other name."}
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

col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.chat_input("Type a message...")
with col2:
    audio_data = audio_recorder(text="", icon_size="2x")

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