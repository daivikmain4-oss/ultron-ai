import streamlit as st
from groq import Groq
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
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

    tts = gTTS(reply)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    st.audio(audio_bytes)

st.write("🎤 Tap to speak:")
audio_data = audio_recorder()

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

user_input = st.chat_input("Or type a message...")
if user_input:
    get_reply(user_input)