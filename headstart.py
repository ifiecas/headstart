import streamlit as st
import traceback
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os
import time
import hashlib
from datetime import datetime

# --- Page config ---
st.set_page_config(
    page_title="Headstart Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load environment variables ---
load_dotenv()

# --- Azure AI Foundry setup ---
conn_str = os.getenv("AZURE_AI_CONN_STR")
project_client = None
agent = None

debug_mode = st.sidebar.toggle("🛠 Debug Mode", value=False)

try:
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=conn_str
    )
    agent = project_client.agents.get_agent("asst_Z9DXOAm2RZnDkZtrg0O9BXna")
except Exception as e:
    st.error(f"❌ Failed to initialize Azure AI Project Client: {e}")
    st.stop()

# --- CSS Styling ---
st.markdown("""
    <style>
        html, body, .main { height: 100%; background-color: #f3f2f1; }
        .block-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 720px;
            margin: auto;
            padding: 0;
        }
        .chat-scroll {
            flex-grow: 1;
            overflow-y: auto;
            padding: 1rem;
        }
        .message-block {
            margin-bottom: 1rem;
        }
        .user-group, .assistant-group {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        .user-group { align-items: flex-end; }
        .message {
            max-width: 70%;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin: 2px 0;
            font-size: 15px;
            line-height: 1.4;
        }
        .user-message {
            background-color: #e6e6e6;
            color: #000;
            align-self: flex-end;
        }
        .assistant-message {
            background-color: #fff;
            border: 1px solid #ccc;
            color: #000;
        }
        .sender-label {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 0.2rem;
        }
        .timestamp {
            font-size: 11px;
            color: #666;
            margin-bottom: 0.5rem;
        }
        .chat-input-container {
            position: sticky;
            bottom: 0;
            background-color: #fff;
            padding: 1rem;
            border-top: 1px solid #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🤖 Headstart Copilot")

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "thread_id" not in st.session_state:
    thread = project_client.agents.create_thread()
    st.session_state.thread_id = thread.id
if "seen_hashes" not in st.session_state:
    st.session_state.seen_hashes = set()

# --- Reset Conversation ---
if st.button("🔄 New Conversation"):
    thread = project_client.agents.create_thread()
    st.session_state.thread_id = thread.id
    st.session_state.chat_history = []
    st.session_state.seen_hashes = set()
    st.experimental_rerun()

# --- Generate unique ID ---
def generate_message_id(content, role):
    return hashlib.md5(f"{role}:{content}".encode()).hexdigest()

# --- Azure call function ---
def call_azure_agent(user_input):
    # Modify assistant replies to prepend reference to user message

    try:
        project_client.agents.create_message(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        project_client.agents.create_and_process_run(
            thread_id=st.session_state.thread_id,
            agent_id=agent.id
        )

        start_time = time.time()
        timeout = 15
        new_responses = []

        while True:
            messages = project_client.agents.list_messages(thread_id=st.session_state.thread_id)

            for msg in messages.text_messages:
                try:
                    role = getattr(msg, 'role', None)
                    text = getattr(msg, 'text', None)
                    content = getattr(text, 'value', '').strip()
                    if role == 'assistant':
                        content = f'*<span style="font-size: 13px; color: #999;">In response to: {user_input}</span>*<br><br>' + content
                    if not content:
                        continue
                    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                    formatted_content = f'*<span style="font-size: 13px; color: #999;">In response to: {user_input}</span>*<br><br>' + content if role == 'assistant' else content
                    new_responses.append((role, formatted_content, timestamp, user_input if role == 'assistant' else None))
                except AttributeError:
                    continue
            if new_responses or (time.time() - start_time > timeout):
                break
            time.sleep(0.5)

        if not new_responses:
            return [("assistant", "⚠️ No response received from Azure AI within timeout.", datetime.now().strftime("%d/%m/%Y %I:%M %p"), None)]
        return new_responses

    except Exception as e:
        if debug_mode:
            st.sidebar.error("Exception occurred")
            st.sidebar.code(traceback.format_exc())
        return [("assistant", "⚠️ Sorry, I couldn’t reach Azure right now. Please try again shortly.", datetime.now().strftime("%d/%m/%Y %I:%M %p"), None)]

# --- Grouped Chat Display ---
st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
last_sender = None
rendered_ids = set()
for idx, (role, message, timestamp, reply_to) in enumerate(st.session_state.chat_history):
    msg_id = generate_message_id(message, role)
    if msg_id in rendered_ids:
        continue
    rendered_ids.add(msg_id)
    is_new_group = last_sender != role
    if is_new_group:
        st.markdown(f"""
        <div class='message-block {role}-group'>
            <div class='sender-label'>{'User Demo' if role == 'user' else 'Headstart Copilot'}</div>
            <div class='timestamp'>{timestamp}{f'<br><span style="font-size: 11px; color: #999;">In response to: "{reply_to}"</span>' if reply_to else ''}</div>
            <div class='message {'user-message' if role == 'user' else 'assistant-message'}'>{message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message {'user-message' if role == 'user' else 'assistant-message'}'>{message}</div>", unsafe_allow_html=True)
    last_sender = role
st.markdown('</div>', unsafe_allow_html=True)

# --- Chat input (fixed bottom) ---
with st.container():
    with st.markdown('<div class="chat-input-container">', unsafe_allow_html=True):
        prompt = st.chat_input("Type a message")

# --- Handle new message ---
if prompt:
    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    content_hash = generate_message_id(prompt.strip(), "user")
    if content_hash not in [generate_message_id(m, r) for r, m, *_ in st.session_state.chat_history]:
        st.session_state.chat_history.append(("user", prompt.strip(), timestamp, None))
        with st.spinner("Headstart Copilot is thinking..."):
            responses = call_azure_agent(prompt)
            for role, message, timestamp, reply_to in responses:
                msg_id = generate_message_id(message, role)
                if msg_id not in [generate_message_id(m, r) for r, m, *_ in st.session_state.chat_history]:
                    st.session_state.chat_history.append((role, message, timestamp, prompt.strip() if role == 'assistant' else None))
