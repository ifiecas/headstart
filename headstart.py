import streamlit as st
import traceback
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os
import time

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
        body { background-color: #f3f2f1; }
        .block-container {
            max-width: 800px;
            margin: auto;
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .stMarkdown { font-family: Segoe UI, sans-serif; color: #201f1e; }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🤖 Headstart Copilot")
st.markdown("Welcome to your meeting prep assistant. Ask anything to start preparing for your meeting.")

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "thread_id" not in st.session_state:
    thread = project_client.agents.create_thread()
    st.session_state.thread_id = thread.id
if "seen_messages" not in st.session_state:
    st.session_state.seen_messages = set()

# --- Reset Conversation ---
if st.button("🔄 New Conversation"):
    thread = project_client.agents.create_thread()
    st.session_state.thread_id = thread.id
    st.session_state.chat_history = []
    st.session_state.seen_messages = set()
    st.experimental_rerun()

# --- Azure call function using message content hashes for deduplication ---
def call_azure_agent(user_input):
    try:
        if debug_mode:
            st.write("📤 Sending message to Azure AI...")

        project_client.agents.create_message(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        if debug_mode:
            st.write("⚙️ Running assistant...")

        project_client.agents.create_and_process_run(
            thread_id=st.session_state.thread_id,
            agent_id=agent.id
        )

        if debug_mode:
            st.write("📥 Fetching messages from thread...")

        start_time = time.time()
        timeout = 15
        seen_hashes = st.session_state.seen_messages
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

                    content_hash = hash((role, content))
                    if content_hash not in seen_hashes:
                        new_responses.append((role, content))
                        seen_hashes.add(content_hash)

                        if debug_mode:
                            st.write(f"🧠 DEBUG - Role: {role}, Message: {content}")

                except AttributeError:
                    if debug_mode:
                        st.warning("⚠️ Skipped malformed message")

            if new_responses or (time.time() - start_time > timeout):
                break
            time.sleep(0.5)

        if not new_responses:
            return [("assistant", "⚠️ No response received from Azure AI within timeout.")]

        return new_responses

    except Exception as e:
        error_trace = traceback.format_exc()
        st.error("❌ Azure API call failed. Displaying fallback message.")
        if debug_mode:
            st.code(error_trace)
        return [("assistant", "⚠️ Sorry, I couldn’t reach Azure right now. Please try again shortly.")]

# --- Chat input ---
prompt = st.chat_input("Enter your message...")

# --- Handle new message ---
if prompt and ("user", prompt) not in st.session_state.chat_history:
    st.session_state.chat_history.append(("user", prompt))
    st.chat_message(name="You").markdown(prompt)

    with st.spinner("Headstart Copilot is thinking..."):
        responses = call_azure_agent(prompt)
        for role, message in responses:
            if (role, message) not in st.session_state.chat_history:
                st.session_state.chat_history.append((role, message))
                st.chat_message(name="Headstart Copilot" if role == "assistant" else "You").markdown(message)

# --- Display full chat history ---
for role, message in st.session_state.chat_history:
    st.chat_message(name="Headstart Copilot" if role == "assistant" else "You").markdown(message)

# 📌 Note:
# ✅ FIXED: Avoid nested `with st.chat_message()` calls. Use one-liner format like:
# st.chat_message(name="...").markdown("...")
