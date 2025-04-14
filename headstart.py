import streamlit as st
import os
import time
import hashlib
from datetime import datetime
import openai
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

# --- Set page config ---
st.set_page_config(
    page_title="Headstart Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
    <style>
        html, body, .main { background-color: #f3f2f1; font-family: 'Segoe UI', sans-serif; }
        .block-container { max-width: 720px; margin: auto; padding-top: 2rem; padding-bottom: 7rem; }
        .stChatFloatingInputContainer { bottom: 20px; max-width: 700px; left: 50%; transform: translateX(-50%); }
        .message-block { margin-bottom: 1.5rem; }
        .user-group { align-items: flex-end; }
        .assistant-group { align-items: flex-start; }
        .message { max-width: 70%; padding: 0.8rem 1rem; border-radius: 8px; margin: 2px 0; font-size: 15px; }
        .user-message { background-color: #e6e6e6; color: #000; text-align: right; }
        .assistant-message { background-color: #fff; border: 1px solid #ccc; color: #000; }
        .sender-label { font-size: 13px; font-weight: 600; margin-bottom: 0.3rem; }
        .timestamp { font-size: 11px; color: #666; margin-bottom: 0.5rem; }
        .reply-reference { font-size: 13px; color: #999; font-style: italic; }
        .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f8f9fa; text-align: center; padding: 10px; font-size: 12px; border-top: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- Title and Description ---
st.markdown('<h1>Try Headstart Copilot!</h1>', unsafe_allow_html=True)
st.markdown('<div class="demo-banner">Demo</div>', unsafe_allow_html=True)
st.markdown('<p class="description">Type the role of the meeting participant, the company, and your meeting objective.</p>', unsafe_allow_html=True)

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "seen_hashes" not in st.session_state:
    st.session_state.seen_hashes = set()

# --- Generate unique ID ---
def generate_message_id(content, role):
    return hashlib.md5(f"{role}:{content}".encode()).hexdigest()

# --- Call Azure OpenAI agent ---
def call_openai_agent(user_input):
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Headstart Copilot, an intelligent assistant that helps users prepare for meetings..."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response["choices"][0]["message"]["content"].strip()
        return [("assistant", answer, datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input)]
    except Exception as e:
        return [("assistant", f"⚠️ Error: {str(e)}", datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input)]

# --- Chat history UI ---
last_sender = None
rendered_ids = set()
for role, message, timestamp, reply_to in st.session_state.chat_history:
    msg_id = generate_message_id(message, role)
    if msg_id in rendered_ids:
        continue
    rendered_ids.add(msg_id)
    reply_to = reply_to or "your message"
    if role == 'assistant':
        st.markdown(f"""
        <div class='message-block assistant-group'>
            <div class='sender-label'>Headstart Copilot</div>
            <div class='timestamp'>{timestamp}</div>
            <div class='reply-reference'>*In response to: \"{reply_to}\"*</div>
            <div class='message assistant-message'>{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='message-block user-group'>
            <div class='sender-label'>You</div>
            <div class='timestamp'>{timestamp}</div>
            <div class='message user-message'>{message}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Chat input ---
prompt = st.chat_input("Type a message")
if prompt:
    user_message = prompt.strip()
    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    content_hash = generate_message_id(user_message, "user")

    if content_hash not in st.session_state.seen_hashes:
        st.session_state.seen_hashes.add(content_hash)
        st.session_state.chat_history.append(("user", user_message, timestamp, None))

        if user_message.lower() in ["hi", "hello", "hey", "start"]:
            welcome_message = """Welcome to Headstart Copilot\nYour intelligent companion for high-impact meetings.\n\nTo get started, please enter:\n• The **role** of the meeting participant\n• The **company** they represent\n• Your **meeting objective**"""
            st.session_state.chat_history.append(("assistant", welcome_message, timestamp, user_message))
        else:
            thinking_placeholder = st.empty()
            thinking_placeholder.info("Headstart Copilot is thinking...")
            responses = call_openai_agent(user_message)
            thinking_placeholder.empty()
            st.session_state.chat_history.extend(responses)
        st.rerun()

# --- Footer ---
st.markdown("""
    <div class="footer">
        <strong>Prototype Version:</strong> Developed for the Copilot Hackathon (April 2025) | Powered by OpenAI's GPT-4o via Azure & hosted on Streamlit
    </div>
""", unsafe_allow_html=True)
