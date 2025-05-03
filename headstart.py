import streamlit as st
import os
import time
import hashlib
from datetime import datetime
import openai
from dotenv import load_dotenv
import random
import json

# --- Load environment variables ---
load_dotenv()

# --- Set OpenAI API config ---
openai.api_type = "azure"
openai.api_version = "2023-12-01-preview"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

# --- Set page config ---
st.set_page_config(
    page_title="Headstart Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Color palette ---
PRIMARY_COLOR = "#0078D4"  # Microsoft blue
SECONDARY_COLOR = "#50E6FF"
BG_COLOR = "#F5F5F5"
TEXT_COLOR = "#252525"
LIGHT_GRAY = "#F0F0F0"

# --- CSS Styling ---
st.markdown(f"""
    <style>
        /* Global styles */
        html, body, .main, .block-container {{ 
            background-color: {BG_COLOR}; 
            font-family: 'Segoe UI', sans-serif;
            color: {TEXT_COLOR};
        }}
        
        /* Layout */
        .block-container {{ 
            max-width: 800px; 
            margin: auto; 
            padding: 1rem 2rem 8rem 2rem;
        }}
        
        /* Header */
        .header-container {{
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
            border-radius: 10px;
            color: white;
        }}
        
        .logo {{
            font-size: 2rem;
            margin-right: 1rem;
        }}
        
        .header-text h1 {{
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
        }}
        
        .header-text p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }}
        
        /* Demo banner */
        .demo-banner {{
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #ff9800;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        /* Chat container */
        .chat-container {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 1.5rem;
            margin-bottom: 2rem;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }}
        
        /* Message blocks */
        .message-block {{
            display: flex;
            flex-direction: column;
            margin-bottom: 1.5rem;
            max-width: 90%;
        }}
        
        .user-group {{
            align-self: flex-end;
        }}
        
        .assistant-group {{
            align-self: flex-start;
        }}
        
        /* Message bubbles */
        .message {{
            padding: 0.8rem 1.2rem;
            border-radius: 18px;
            margin: 2px 0;
            font-size: 15px;
            line-height: 1.5;
            position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}
        
        .user-message {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border-bottom-right-radius: 4px;
        }}
        
        .assistant-message {{
            background-color: {LIGHT_GRAY};
            color: {TEXT_COLOR};
            border-bottom-left-radius: 4px;
        }}
        
        /* Message metadata */
        .message-metadata {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
        }}
        
        .sender-label {{
            font-size: 13px;
            font-weight: 600;
        }}
        
        .timestamp {{
            font-size: 11px;
            color: #666;
        }}
        
        .reply-reference {{
            font-size: 12px;
            color: #666;
            font-style: italic;
            margin-top: 0.3rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Input area */
        .stChatFloatingInputContainer {{
            bottom: 20px;
            max-width: 800px;
            width: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            padding: 0.5rem;
        }}
        
        .stChatInput {{
            border-radius: 20px !important;
            border: 1px solid #ddd !important;
            padding: 0.8rem 1rem !important;
        }}
        
        /* Typing indicator */
        .typing-indicator {{
            display: flex;
            align-items: center;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .typing-indicator span {{
            height: 8px;
            width: 8px;
            border-radius: 50%;
            background-color: {PRIMARY_COLOR};
            margin-right: 4px;
            animation: typing 1s infinite ease-in-out;
        }}
        
        .typing-indicator span:nth-child(2) {{
            animation-delay: 0.2s;
        }}
        
        .typing-indicator span:nth-child(3) {{
            animation-delay: 0.4s;
        }}
        
        @keyframes typing {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-5px); }}
        }}
        
        /* Footer */
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: white;
            text-align: center;
            padding: 12px;
            font-size: 12px;
            border-top: 1px solid #eee;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        }}
        
        /* Form elements */
        .form-container {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .form-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: {PRIMARY_COLOR};
        }}
        
        /* Tips section */
        .tips-container {{
            background-color: #E6F7FF;
            border-left: 4px solid {PRIMARY_COLOR};
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 0 4px 4px 0;
        }}
        
        .tips-title {{
            font-weight: 600;
            color: {PRIMARY_COLOR};
            margin-bottom: 0.5rem;
        }}
        
        /* Feedback buttons */
        .feedback-buttons {{
            display: flex;
            justify-content: flex-end;
            margin-top: 0.5rem;
        }}
        
        .feedback-btn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 4px 8px;
            color: #666;
            transition: color 0.2s ease;
        }}
        
        .feedback-btn:hover {{
            color: {PRIMARY_COLOR};
        }}
        
        /* Clear chat button */
        .clear-chat {{
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: transparent;
            border: none;
            color: #999;
            cursor: pointer;
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        .clear-chat:hover {{
            background-color: #f0f0f0;
            color: #666;
        }}
        
        /* Buttons */
        .custom-button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }}
        
        .custom-button:hover {{
            background-color: #005a9e;
        }}
        
        /* Stickers */
        .sticker {{
            position: relative;
            display: inline-block;
            margin-right: 8px;
            vertical-align: middle;
        }}
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header {{
            visibility: hidden;
        }}
        
        div.stButton > button:first-child {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-weight: 500;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Session state initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "seen_hashes" not in st.session_state:
    st.session_state.seen_hashes = set()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "company": "",
        "role": "",
        "recent_meetings": []
    }
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.now()

# --- Helper functions ---
def generate_message_id(content, role):
    """Generate a unique ID for a message"""
    return hashlib.md5(f"{role}:{content}:{datetime.now()}".encode()).hexdigest()

def format_chat_message(role, message, timestamp, reply_to=None, message_id=None):
    """Format a chat message as HTML"""
    is_user = role == 'user'
    group_class = "user-group" if is_user else "assistant-group"
    message_class = "user-message" if is_user else "assistant-message"
    sender_label = "You" if is_user else "Headstart Copilot"
    
    # Format the message with Markdown
    message = message.replace('\n', '<br>')
    
    # Reply reference
    reply_html = ""
    if reply_to and not is_user:
        reply_html = f"""<div class='reply-reference'>Re: "{reply_to[:50]}{'...' if len(reply_to) > 50 else ''}"</div>"""
    
    # Feedback buttons for assistant messages
    feedback_html = ""
    if not is_user and message_id:
        feedback_html = f"""
        <div class='feedback-buttons'>
            <button class='feedback-btn' onclick="handleFeedback('{message_id}', 'helpful')">👍</button>
            <button class='feedback-btn' onclick="handleFeedback('{message_id}', 'unhelpful')">👎</button>
        </div>
        """
    
    return f"""
    <div class='message-block {group_class}'>
        <div class='message-metadata'>
            <div class='sender-label'>{sender_label}</div>
            <div class='timestamp'>{timestamp}</div>
        </div>
        {reply_html}
        <div class='message {message_class}'>{message}</div>
        {feedback_html}
    </div>
    """

def call_openai_agent(user_input, system_prompt=None):
    """Call Azure OpenAI API with user input"""
    try:
        # Default system prompt if none provided
        if not system_prompt:
            system_prompt = """You are Headstart Copilot, an intelligent assistant that helps users prepare for meetings.
            Your goal is to help users prepare effectively by providing relevant information, suggested talking points,
            and strategic advice tailored to their meeting context. Be concise, practical, and focus on actionable insights.
            Consider the user's role, the company they're meeting with, and their objective to provide personalized guidance."""
        
        # Add contextual information if available
        if st.session_state.user_profile["name"]:
            system_prompt += f"\n\nUser profile: {json.dumps(st.session_state.user_profile)}"
        
        # Create message history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add relevant chat history (last 5 messages)
        relevant_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 0 else []
        for role, content, _, _ in relevant_history:
            messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_input})
        
        # Call API
        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        answer = response["choices"][0]["message"]["content"].strip()
        message_id = generate_message_id(answer, "assistant")
        
        # Simulate typing animation
        return [("assistant", answer, datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input, message_id)]
    
    except Exception as e:
        error_message = f"⚠️ Error: {str(e)}"
        return [("assistant", error_message, datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input, None)]

def simulate_typing(message):
    """Simulate typing animation for AI responses"""
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
    </div>
    """, unsafe_allow_html=True)
    
    # Simulate thinking time based on message length
    thinking_time = min(len(message) / 100, 2.5)
    time.sleep(thinking_time)
    
    typing_placeholder.empty()

def clear_chat():
    """Clear the chat history"""
    st.session_state.chat_history = []
    st.session_state.seen_hashes = set()
    st.session_state.feedbacks = {}
    st.rerun()

def save_meeting_notes():
    """Save the current chat as meeting notes"""
    if len(st.session_state.chat_history) > 0:
        # Get current timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        
        # Extract meeting topic
        meeting_topic = "Meeting"
        for role, content, _, _ in st.session_state.chat_history[:3]:
            if role == "user" and len(content) > 5:
                meeting_topic = content[:30] + "..." if len(content) > 30 else content
                break
        
        # Save to recent meetings
        meeting_data = {
            "id": hashlib.md5(f"{timestamp}:{meeting_topic}".encode()).hexdigest(),
            "topic": meeting_topic,
            "timestamp": timestamp,
            "messages": st.session_state.chat_history.copy()
        }
        
        # Add to user profile
        st.session_state.user_profile["recent_meetings"].insert(0, meeting_data)
        
        # Keep only last 5 meetings
        if len(st.session_state.user_profile["recent_meetings"]) > 5:
            st.session_state.user_profile["recent_meetings"] = st.session_state.user_profile["recent_meetings"][:5]
        
        # Show success message
        st.success("Meeting notes saved successfully!")
        time.sleep(1.5)
        st.rerun()

# --- Header ---
st.markdown("""
    <div class="header-container">
        <div class="logo">🚀</div>
        <div class="header-text">
            <h1>Headstart Copilot</h1>
            <p>Your intelligent companion for high-impact meetings</p>
        </div>
        <div class="demo-banner">Demo</div>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## User Profile")
    
    # Profile setup
    if not st.session_state.setup_complete:
        with st.form("profile_form"):
            st.markdown("#### Complete your profile")
            name = st.text_input("Your Name", value=st.session_state.user_profile["name"])
            company = st.text_input("Your Company", value=st.session_state.user_profile["company"])
            role = st.text_input("Your Role", value=st.session_state.user_profile["role"])
            
            submit = st.form_submit_button("Save Profile")
            
            if submit:
                st.session_state.user_profile["name"] = name
                st.session_state.user_profile["company"] = company
                st.session_state.user_profile["role"] = role
                st.session_state.setup_complete = True
                st.success("Profile saved!")
                st.rerun()
    else:
        # Display user profile
        st.markdown(f"""
        **Name:** {st.session_state.user_profile["name"]}  
        **Company:** {st.session_state.user_profile["company"]}  
        **Role:** {st.session_state.user_profile["role"]}
        """)
        
        if st.button("Edit Profile", key="edit_profile"):
            st.session_state.setup_complete = False
            st.rerun()
    
    st.divider()
    
    # Recent meetings
    st.markdown("## Recent Meetings")
    if len(st.session_state.user_profile["recent_meetings"]) > 0:
        for meeting in st.session_state.user_profile["recent_meetings"]:
            st.markdown(f"""
            <div style="padding: 8px; margin-bottom: 8px; background-color: #f0f0f0; border-radius: 4px;">
                <div style="font-weight: bold;">{meeting["topic"]}</div>
                <div style="font-size: 12px; color: #666;">{meeting["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent meetings found.")
    
    st.divider()
    
    # Tips
    st.markdown("""
    <div class="tips-container">
        <div class="tips-title">💡 Quick Tips</div>
        <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
            <li>Specify meeting participant's role</li>
            <li>Mention the company you're meeting with</li>
            <li>Be clear about your meeting objective</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Settings and actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", key="clear_chat_btn"):
            clear_chat()
    with col2:
        if st.button("Save Notes", key="save_notes_btn"):
            save_meeting_notes()

# --- Main chat area ---
st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)

# Chat history display
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
        <h3>Welcome to Headstart Copilot</h3>
        <p style="color: #666; max-width: 500px; margin: 0 auto;">
            I'm your intelligent meeting companion. To get started, tell me about your upcoming meeting.
            Include the role of the participant, their company, and your objective.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for role, message, timestamp, reply_to, message_id in st.session_state.chat_history:
        st.markdown(
            format_chat_message(role, message, timestamp, reply_to, message_id),
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# --- Chat input ---
prompt = st.chat_input("Type a message")
if prompt:
    user_message = prompt.strip()
    timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    content_hash = generate_message_id(user_message, "user")
    
    if content_hash not in st.session_state.seen_hashes:
        st.session_state.seen_hashes.add(content_hash)
        message_id = generate_message_id(user_message, "user")
        st.session_state.chat_history.append(("user", user_message, timestamp, None, message_id))
        
        # Check for special commands
        if user_message.lower() in ["clear", "reset", "clear chat"]:
            clear_chat()
        elif user_message.lower() in ["hi", "hello", "hey", "start"]:
            welcome_message = """Welcome to Headstart Copilot! 👋\n\nI'm your AI companion for meeting preparation. To help you effectively, please tell me about your upcoming meeting:\n\n1. Who are you meeting with? (role/position)\n2. What company do they represent?\n3. What's your main objective for this meeting?\n\nFor example: "I'm meeting the Head of Marketing at TechCorp to discuss a potential partnership for our new product launch."
            """
            message_id = generate_message_id(welcome_message, "assistant")
            st.session_state.chat_history.append(("assistant", welcome_message, timestamp, user_message, message_id))
        else:
            # Process the user message
            simulate_typing(user_message)
            responses = call_openai_agent(user_message)
            st.session_state.chat_history.extend(responses)
        
        # Update last activity time
        st.session_state.last_activity = datetime.now()
        
        st.rerun()

# --- JavaScript for handling feedback ---
st.markdown("""
<script>
function handleFeedback(messageId, feedbackType) {
    // In a real app, this would send feedback to a server
    console.log(`Feedback for ${messageId}: ${feedbackType}`);
    
    // Show feedback received message
    alert(`Thank you for your feedback!`);
}
</script>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <div class="footer">
        <strong>Headstart Copilot</strong> | Prototype Version 1.0 | Developed for the Copilot Hackathon (April 2025) | Powered by Azure OpenAI
    </div>
""", unsafe_allow_html=True)

# --- Add auto-scrolling to bottom of chat ---
st.markdown("""
<script>
    function scrollToBottom() {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Run on page load and whenever content changes
    scrollToBottom();
    const observer = new MutationObserver(scrollToBottom);
    observer.observe(document.getElementById('chat-container'), { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# Check for inactivity timeout (5 minutes)
if datetime.now().timestamp() - st.session_state.last_activity.timestamp() > 300:
    inactivity_message = "It looks like you've been inactive for a while. Can I help you with anything else?"
    # Only add this message if it's not already the last message
    if (len(st.session_state.chat_history) == 0 or 
        st.session_state.chat_history[-1][0] != "assistant" or 
        st.session_state.chat_history[-1][1] != inactivity_message):
        message_id = generate_message_id(inactivity_message, "assistant")
        st.session_state.chat_history.append(
            ("assistant", inactivity_message, datetime.now().strftime("%d/%m/%Y %I:%M %p"), None, message_id)
        )
        st.session_state.last_activity = datetime.now()
        st.rerun()
