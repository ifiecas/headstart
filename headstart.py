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
            max-width: 900px; 
            margin: auto; 
            padding: 1rem 3rem 8rem 3rem;
        }}
        
        /* Typography improvements */
        p {{
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        
        .message p:last-child {{
            margin-bottom: 0;
        }}
        
        /* Message list styling */
        .message-list {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        
        .message-list li {{
            margin-bottom: 6px;
        }}
        
        /* Bold and emphasis */
        .message strong, .message b {{
            font-weight: 600;
        }}
        
        .message em, .message i {{
            font-style: italic;
            color: inherit;
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
        .chat-container-wrapper {{
            position: relative;
            margin-bottom: 2rem;
        }}
        
        .chat-container {{
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            padding: 2rem;
            margin-bottom: 2rem;
            min-height: 450px;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        
        /* Date separator */
        .date-separator {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 1.5rem 0;
            position: relative;
        }}
        
        .date-separator::before {{
            content: '';
            flex-grow: 1;
            border-top: 1px solid #e2e8f0;
            margin-right: 1rem;
        }}
        
        .date-separator::after {{
            content: '';
            flex-grow: 1;
            border-top: 1px solid #e2e8f0;
            margin-left: 1rem;
        }}
        
        .date-separator span {{
            background-color: #f8fafc;
            border-radius: 20px;
            padding: 0.25rem 1rem;
            font-size: 12px;
            color: #64748b;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        /* Message blocks */
        .message-block {{
            display: flex;
            flex-direction: column;
            margin-bottom: 2rem;
            max-width: 85%;
            position: relative;
        }}
        
        .user-group {{
            align-self: flex-end;
        }}
        
        .assistant-group {{
            align-self: flex-start;
        }}
        
        /* Message bubbles */
        .message {{
            padding: 1rem 1.4rem;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.6;
            position: relative;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .user-message {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border-bottom-right-radius: 4px;
            text-align: left;
        }}
        
        .assistant-message {{
            background-color: white;
            border: 1px solid #e1e4e8;
            color: {TEXT_COLOR};
            border-bottom-left-radius: 4px;
        }}
        
        /* Avatar bubbles */
        .message-block::before {{
            content: '';
            position: absolute;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            top: 0;
            background-size: cover;
            background-position: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .assistant-group::before {{
            left: -48px;
            background-color: {PRIMARY_COLOR};
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-4-8c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1zm8 0c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1zm-4 5.5c2.5 0 4.5-1.5 5.5-3.5h-11c1 2 3 3.5 5.5 3.5z"/></svg>');
        }}
        
        .user-group::before {{
            right: -48px;
            background-color: #6b7280;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>');
        }}
        
        /* Message metadata */
        .message-metadata {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
            padding: 0 2px;
        }}
        
        .sender-label {{
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
        }}
        
        .timestamp {{
            font-size: 11px;
            color: #718096;
        }}
        
        .reply-reference {{
            font-size: 12px;
            color: #718096;
            font-style: italic;
            margin-top: 0.2rem;
            margin-bottom: 0.6rem;
            border-left: 2px solid {SECONDARY_COLOR};
            padding-left: 8px;
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
    
# --- Fix existing chat_history format if needed ---
# This ensures backward compatibility with existing sessions
if st.session_state.chat_history:
    fixed_history = []
    for item in st.session_state.chat_history:
        if len(item) == 4:  # Old format without message_id
            role, message, timestamp, reply_to = item
            message_id = generate_message_id(message, role)
            fixed_history.append((role, message, timestamp, reply_to, message_id))
        elif len(item) == 5:  # New format with message_id
            fixed_history.append(item)
        else:
            # Skip invalid items
            continue
    st.session_state.chat_history = fixed_history

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
    # Replace newlines with proper paragraph breaks for better readability
    formatted_message = ""
    for paragraph in message.split('\n\n'):
        if paragraph.strip():
            # Check if this is a list item (starts with - or *)
            is_list = False
            list_items = []
            for line in paragraph.split('\n'):
                line = line.strip()
                if line and (line.startswith('- ') or line.startswith('* ')):
                    is_list = True
                    item_content = line[2:].strip()
                    list_items.append(f"<li>{item_content}</li>")
            
            if is_list:
                formatted_message += f"<ul class='message-list'>{''.join(list_items)}</ul>"
            else:
                # Regular paragraph
                lines = [line for line in paragraph.split('\n') if line.strip()]
                if lines:
                    formatted_message += f"<p>{'<br>'.join(lines)}</p>"
    
    # If message has no paragraphs, just use the original with br tags
    if not formatted_message:
        formatted_message = f"<p>{message.replace('\n', '<br>')}</p>"
    
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
        <div class='message {message_class}'>{formatted_message}</div>
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
        
        # Add relevant chat history (last 10 messages)
        relevant_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 0 else []
        for chat_item in relevant_history:
            # Handle different formats of chat history items
            if len(chat_item) >= 2:  # Need at minimum role and content
                role = chat_item[0]
                content = chat_item[1]
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
        
        # Create response with 5 elements (role, content, timestamp, reply_to, message_id)
        return [("assistant", answer, datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input, message_id)]
    
    except Exception as e:
        error_message = f"⚠️ Error: {str(e)}"
        message_id = generate_message_id(error_message, "assistant")
        return [("assistant", error_message, datetime.now().strftime("%d/%m/%Y %I:%M %p"), user_input, message_id)]

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
    for chat_item in st.session_state.chat_history:
        # Check if the chat item has 5 elements (including message_id)
        if len(chat_item) == 5:
            role, message, timestamp, reply_to, message_id = chat_item
        # Backwards compatibility with old format (4 elements)
        elif len(chat_item) == 4:
            role, message, timestamp, reply_to = chat_item
            message_id = None
        else:
            # Skip invalid format
            continue
            
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
            try:
                # Process the user message
                simulate_typing(user_message)
                responses = call_openai_agent(user_message)
                
                # Ensure responses have the correct format before adding them
                fixed_responses = []
                for response in responses:
                    if len(response) == 5:  # Already has message_id
                        fixed_responses.append(response)
                    elif len(response) == 4:  # Needs message_id
                        role, message, ts, reply = response
                        msg_id = generate_message_id(message, role)
                        fixed_responses.append((role, message, ts, reply, msg_id))
                
                st.session_state.chat_history.extend(fixed_responses)
            except Exception as e:
                # Handle any errors
                error_message = f"⚠️ Error: {str(e)}"
                message_id = generate_message_id(error_message, "assistant")
                st.session_state.chat_history.append(("assistant", error_message, timestamp, user_message, message_id))
        
        # Update last activity time
        st.session_state.last_activity = datetime.now()
        
        st.rerun()

# --- JavaScript for enhanced functionality ---
st.markdown("""
<script>
// Handle feedback submissions
function handleFeedback(messageId, feedbackType) {
    // In a real app, this would send feedback to a server
    console.log(`Feedback for ${messageId}: ${feedbackType}`);
    
    // Update the UI to show feedback was received
    const feedbackBtn = event.target;
    const allBtns = document.querySelectorAll(`.feedback-btn[onclick*="${messageId}"]`);
    
    // Reset all buttons
    allBtns.forEach(btn => {
        btn.style.color = '#718096';
        btn.style.transform = 'scale(1)';
    });
    
    // Highlight selected button
    feedbackBtn.style.color = feedbackType === 'helpful' ? '#0078D4' : '#f56565';
    feedbackBtn.style.transform = 'scale(1.2)';
    
    // Show temporary toast notification
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = 'Thanks for your feedback!';
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 2000);
}

// Smooth scrolling to bottom of chat
function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Format code blocks
function formatCodeBlocks() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        const codeBlocks = message.querySelectorAll('pre code');
        if (codeBlocks.length > 0) {
            codeBlocks.forEach(block => {
                // Add copy button
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-code-btn';
                copyBtn.innerHTML = '📋 Copy';
                copyBtn.onclick = function() {
                    const code = block.textContent;
                    navigator.clipboard.writeText(code);
                    copyBtn.innerHTML = '✓ Copied!';
                    setTimeout(() => {
                        copyBtn.innerHTML = '📋 Copy';
                    }, 2000);
                };
                
                // Create wrapper for code block
                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-wrapper';
                
                // Move code block into wrapper
                block.parentNode.insertBefore(wrapper, block);
                wrapper.appendChild(block);
                
                // Add copy button to wrapper
                wrapper.appendChild(copyBtn);
            });
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    scrollToBottom();
    formatCodeBlocks();
    
    // Observe for content changes
    const observer = new MutationObserver(function() {
        scrollToBottom();
        formatCodeBlocks();
    });
    
    // Start observing chat container
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        observer.observe(chatContainer, { childList: true, subtree: true });
    }
});
</script>

<style>
/* Toast notification */
.toast-notification {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background-color: #0078D4;
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    z-index: 1000;
    opacity: 0;
    transition: all 0.3s ease;
}

/* Code block styling */
.code-block-wrapper {
    position: relative;
    margin: 1rem 0;
    border-radius: 8px;
    overflow: hidden;
}

.copy-code-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background-color: rgba(255,255,255,0.8);
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
    z-index: 1;
    transition: all 0.2s ease;
}

.copy-code-btn:hover {
    background-color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <div class="footer-logo">
                <span class="footer-icon">🚀</span>
                <strong>Headstart Copilot</strong>
            </div>
            <div class="footer-links">
                <a href="#" class="footer-link">Terms</a>
                <a href="#" class="footer-link">Privacy</a>
                <a href="#" class="footer-link">Help</a>
            </div>
            <div class="footer-info">
                Prototype Version 1.0 | Hackathon Edition (April 2025) | Powered by Azure OpenAI
            </div>
        </div>
    </div>

<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    box-shadow: 0 -3px 10px rgba(0,0,0,0.05);
    z-index: 100;
}

.footer-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}

.footer-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
}

.footer-icon {
    font-size: 16px;
}

.footer-links {
    display: flex;
    gap: 16px;
}

.footer-link {
    color: #4a5568;
    text-decoration: none;
    font-size: 12px;
    transition: color 0.2s;
}

.footer-link:hover {
    color: #0078D4;
}

.footer-info {
    font-size: 12px;
    color: #718096;
}

@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        gap: 8px;
        text-align: center;
    }
    
    .footer-logo {
        justify-content: center;
    }
    
    .footer-links {
        justify-content: center;
        margin: 8px 0;
    }
}
</style>
""", unsafe_allow_html=True)

# Check for inactivity timeout (5 minutes)
try:
    if datetime.now().timestamp() - st.session_state.last_activity.timestamp() > 300:
        inactivity_message = "It looks like you've been inactive for a while. Can I help you with anything else?"
        # Only add this message if it's not already the last message
        if (len(st.session_state.chat_history) == 0 or 
            (len(st.session_state.chat_history) > 0 and 
             (len(st.session_state.chat_history[-1]) < 2 or 
              st.session_state.chat_history[-1][0] != "assistant" or 
              st.session_state.chat_history[-1][1] != inactivity_message))):
            message_id = generate_message_id(inactivity_message, "assistant")
            st.session_state.chat_history.append(
                ("assistant", inactivity_message, datetime.now().strftime("%d/%m/%Y %I:%M %p"), None, message_id)
            )
            st.session_state.last_activity = datetime.now()
            st.rerun()
except Exception as e:
    # Silently handle any errors in the inactivity check
    pass
