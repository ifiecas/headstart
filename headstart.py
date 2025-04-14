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
            max-width: 720px;
            margin: auto;
            padding-top: 2rem;
            padding-bottom: 7rem; /* Provide space for the chat input */
        }
        .stChatFloatingInputContainer {
            bottom: 20px;
            max-width: 700px;
            left: 50%;
            transform: translateX(-50%);
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
            padding: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .message-block {
            margin-bottom: 1.5rem;
        }
        .user-group, .assistant-group {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        .user-group { align-items: flex-end; }
        .message {
            max-width: 70%;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin: 2px 0;
            font-size: 15px;
            line-height: 1.4;
        }
        .user-message {
            background-color: #e6e6e6;
            color: #000;
            align-self: flex-end;
            text-align: right;
        }
        .assistant-message {
            background-color: #fff;
            border: 1px solid #ccc;
            color: #000;
        }
        .sender-label {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .timestamp {
            font-size: 11px;
            color: #666;
            margin-bottom: 0.5rem;
        }
        .reply-reference {
            font-size: 13px;
            color: #999;
            margin-bottom: 0.5rem;
            font-style: italic;
        }
        /* Make input more visible */
        .stChatInputContainer {
            padding: 0.5rem;
            background-color: white !important;
            border-radius: 8px !important;
        }
        .stChatInput {
            background-color: white;
            border: 1px solid #ccc !important;
            padding: 0.5rem !important;
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
    st.rerun()

# --- Generate unique ID ---
def generate_message_id(content, role):
    return hashlib.md5(f"{role}:{content}".encode()).hexdigest()

# --- Azure call function ---
def call_azure_agent(user_input):
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
                    if not content:
                        continue
                    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                    new_responses.append((role, content, timestamp, user_input if role == 'assistant' else None))
                except AttributeError:
                    continue
            if new_responses or (time.time() - start_time > timeout):
                break
            time.sleep(0.5)

        if not new_responses:
            return [("assistant", "⚠️ No response received from Azure AI within timeout.", datetime.now().strftime("%d/%m/%Y %I:%M %p"), None)]
        return new_responses

    except Exception as e:
        return [("assistant", "⚠️ Sorry, I couldn't reach Azure right now. Please try again shortly.", datetime.now().strftime("%d/%m/%Y %I:%M %p"), None)]

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
        if role == 'assistant' and reply_to:
            st.markdown(f"""
            <div class='message-block {role}-group'>
                <div class='sender-label'>{'User Demo' if role == 'user' else 'Headstart Copilot'}</div>
                <div class='timestamp'>{timestamp}</div>
                <div class='reply-reference'>In response to: "{reply_to}"</div>
                <div class='message {'user-message' if role == 'user' else 'assistant-message'}'>{message}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='message-block {role}-group'>
                <div class='sender-label'>{'User Demo' if role == 'user' else 'Headstart Copilot'}</div>
                <div class='timestamp'>{timestamp}</div>
                <div class='message {'user-message' if role == 'user' else 'assistant-message'}'>{message}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message {'user-message' if role == 'user' else 'assistant-message'}'>{message}</div>", unsafe_allow_html=True)
    last_sender = role
st.markdown('</div>', unsafe_allow_html=True)

# --- Chat input (fixed bottom) ---
prompt = st.chat_input("Type a message", key="chat_input")

# --- Handle new message ---
if prompt:
    # Process the new message
    user_message = prompt.strip()
    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    content_hash = generate_message_id(user_message, "user")
    
    # Define welcome message
    welcome_message = """Welcome to Headstart Copilot

Your intelligent companion for high-impact meetings.


To get started, please enter:

• The **role** of the meeting participant

• The **company** they represent

• Your **meeting objective**


Headstart Copilot will generate tailored talking points and strategic questions to help you lead with clarity and confidence."""
    
    # Only add if it's a new message
    if content_hash not in st.session_state.seen_hashes:
        # Add to seen hashes to prevent duplicates
        st.session_state.seen_hashes.add(content_hash)
        
        # Add to chat history
        st.session_state.chat_history.append(("user", user_message, timestamp, None))
        
        # Check if it's a greeting and directly respond with welcome message
        if user_message.lower().strip() in ["hi", "hello", "hey", "start"]:
            st.session_state.chat_history.append(("assistant", welcome_message, timestamp, user_message))
            st.rerun()
        else:
            # Get response from Azure
            st.info("Headstart Copilot is thinking...")
            responses = call_azure_agent(user_message)
            
            # Add responses to chat history
            for role, message, timestamp, reply_to in responses:
                msg_id = generate_message_id(message, role)
                if msg_id not in st.session_state.seen_hashes:
                    st.session_state.seen_hashes.add(msg_id)
                    st.session_state.chat_history.append((role, message, timestamp, reply_to))
                    
            # Force a refresh
            st.rerun()
