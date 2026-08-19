import streamlit as st
from google import genai

st.title("🤖 Ultron")

client = genai.Client(api_key=st.secrets["AQ.Ab8RN6KCrK9qhdA7q2_6lH56IwpLpDNYdBvxPfkAWcyKfstzyw"])
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash")
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    response = st.session_state.chat.send_message(user_input)

    st.session_state.messages.append({"role": "assistant", "content": response.text})
    with st.chat_message("assistant"):
        st.write(response.text)