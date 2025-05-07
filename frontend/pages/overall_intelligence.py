import streamlit as st
import sys
import os
import json
import datetime
import re
import time

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.memory_lanes import OverallIntelligence
from backend.voice_interface import voice_output
from streamlit_chat import message

# Initialize session state for this page
if 'overall_intelligence' not in st.session_state:
    if 'client' in st.session_state and st.session_state.client:
        st.session_state.overall_intelligence = OverallIntelligence(st.session_state.client)
    else:
        st.session_state.overall_intelligence = None

if 'current_lane' not in st.session_state:
    st.session_state.current_lane = "journal"  # Default lane
    
if 'lane_messages' not in st.session_state:
    st.session_state.lane_messages = {}
    for lane in ["health", "work", "journal"]:
        st.session_state.lane_messages[lane] = []

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Check if app is initialized
if 'initialized' not in st.session_state or not st.session_state.initialized:
    st.switch_page("app.py")

# Initialize session state for this page
if 'overall_messages' not in st.session_state:
    st.session_state.overall_messages = []

if 'health_memory' not in st.session_state:
    st.session_state.health_memory = []

if 'work_memory' not in st.session_state:
    st.session_state.work_memory = []

if 'journal_memory' not in st.session_state:
    st.session_state.journal_memory = []

if 'universal_chat_history' not in st.session_state:
    st.session_state.universal_chat_history = []

def switch_lane(lane):
    """Switch to a different memory lane"""
    st.session_state.current_lane = lane
    
    # Load messages for this lane if not already loaded
    if not st.session_state.lane_messages[lane]:
        lane_obj = st.session_state.overall_intelligence.memory_lanes[lane]
        st.session_state.lane_messages[lane] = lane_obj.get_memory_history()
    
    st.rerun()

def process_uploaded_file():
    """Process an uploaded file"""
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file:
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        
        # Process the file
        results = st.session_state.overall_intelligence.process_file_upload(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        # Show results
        for category, success, message in results:
            if success:
                st.success(f"{category.capitalize()}: {message}")
            else:
                st.error(f"{category.capitalize()}: {message}")
        
        # Reload messages for current lane
        lane_obj = st.session_state.overall_intelligence.memory_lanes[st.session_state.current_lane]
        st.session_state.lane_messages[st.session_state.current_lane] = lane_obj.get_memory_history()

def on_input_change():
    """Handle user input changes"""
    st.session_state.user_input = st.session_state.widget_input
    st.session_state.widget_input = ""  # Clear the input box

def send_message():
    """Send a message to the AI"""
    if not st.session_state.user_input:
        return
    
    user_input = st.session_state.user_input
    st.session_state.user_input = ""
    
    # Get messages for API and determine categories
    messages, categories = st.session_state.overall_intelligence.get_messages_for_query(user_input)
    
    # Show user message immediately in all relevant lanes
    for category in categories:
        if category not in st.session_state.lane_messages:
            st.session_state.lane_messages[category] = []
            
        st.session_state.lane_messages[category].append({
            "timestamp": "",
            "human": user_input,
            "ai": ""
        })
    
    # Call the API
    with st.spinner("Tryambakam is thinking..."):
        try:
            response = st.session_state.client.chat.completions.create(
                model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                messages=messages,
                stream=False
            )
            
            ai_response = response.choices[0].message.content
            
            # Update the last message with the AI response in all relevant lanes
            for category in categories:
                if st.session_state.lane_messages[category]:
                    st.session_state.lane_messages[category][-1]["ai"] = ai_response
                    st.session_state.lane_messages[category][-1]["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Save to memory lanes
            st.session_state.overall_intelligence.save_response(user_input, ai_response, categories)
            
            # Speak the response if voice is enabled
            if st.session_state.voice_enabled:
                voice_output.speak(ai_response)
                
        except Exception as e:
            st.error(f"Error: {e}")
            # Remove the last message if there was an error
            for category in categories:
                if st.session_state.lane_messages[category]:
                    st.session_state.lane_messages[category].pop()

def categorize_message(message_text):
    """Categorize a message into a memory lane"""
    # Use the AI to categorize the message
    response = st.session_state.client.chat.completions.create(
        model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
        messages=[
            {"role": "system", "content": """You are a message categorizer. 
             Categorize the user's message into one of these categories:
             - health: related to physical health, mental health, wellness, fitness, nutrition, medical issues
             - work: related to career, job, business, professional development, education, skills
             - journal: personal reflections, daily activities, emotions, relationships, life events
             
             Respond with ONLY the category name (health, work, or journal).
             If unsure, choose the most likely category based on the content."""},
            {"role": "user", "content": message_text}
        ],
        max_tokens=10
    )
    
    category = response.choices[0].message.content.strip().lower()
    
    # Extract just the category name if the AI included other text
    if "health" in category:
        return "health"
    elif "work" in category:
        return "work"
    elif "journal" in category:
        return "journal"
    else:
        # Default to journal if categorization failed
        return "journal"

def store_in_memory_lane(message_text, ai_response, category):
    """Store a conversation in the appropriate memory lane"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory_entry = {
        "timestamp": timestamp,
        "user_message": message_text,
        "ai_response": ai_response
    }
    
    if category == "health":
        st.session_state.health_memory.append(memory_entry)
    elif category == "work":
        st.session_state.work_memory.append(memory_entry)
    elif category == "journal":
        st.session_state.journal_memory.append(memory_entry)

def get_memory_context(category):
    """Get relevant memory context for a category"""
    memory_context = ""
    if category == "health":
        memory = st.session_state.health_memory
        memory_context = "This conversation is about health, wellness, fitness, or medical topics."
    elif category == "work":
        memory = st.session_state.work_memory
        memory_context = "This conversation is about work, career, business, or professional development."
    elif category == "journal":
        memory = st.session_state.journal_memory
        memory_context = "This conversation is about personal reflections, daily activities, emotions, or relationships."
    
    # Add recent memories from this category (up to 3)
    if memory:
        memory_context += "\n\nRecent related memories:"
        for entry in memory[-3:]:
            memory_context += f"\n- {entry['timestamp']}:"
            memory_context += f"\n  User: {entry['user_message']}"
            memory_context += f"\n  You: {entry['ai_response']}"
    
    return memory_context

def get_ai_response(message_text, category):
    """Get AI response based on the message and its category"""
    # Get relevant memory context
    memory_context = get_memory_context(category)
    
    # Get AI response with memory context
    response = st.session_state.client.chat.completions.create(
        model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
        messages=[
            {"role": "system", "content": f"""You are Tryambakam, a helpful AI assistant.
             {memory_context}
             
             Respond to the user's message in a helpful, informative way.
             If appropriate, reference or build upon the previous memories.
             Your response should be relevant to the {category} category."""},
            {"role": "user", "content": message_text}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()

def process_message():
    """Process a new message from the user"""
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        
        # Clear the input box
        st.session_state.user_input = ""
        
        # Add user message to chat history immediately
        st.session_state.universal_chat_history.append({
            "role": "user", 
            "content": user_message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Process the message
        with st.spinner("Thinking..."):
            try:
                # Categorize the message
                category = categorize_message(user_message)
                
                # Get AI response
                ai_response = get_ai_response(user_message, category)
                
                # Add AI response to chat history
                st.session_state.universal_chat_history.append({
                    "role": "assistant", 
                    "content": ai_response,
                    "category": category,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Store in appropriate memory lane
                store_in_memory_lane(user_message, ai_response, category)
                
                # Speak the response if voice is enabled
                if st.session_state.voice_enabled:
                    voice_output.speak(ai_response)
            except Exception as e:
                st.error(f"Error processing message: {e}")
                # Add a fallback response
                st.session_state.universal_chat_history.append({
                    "role": "assistant", 
                    "content": "I'm sorry, I encountered an error processing your message. Please try again.",
                    "category": "error",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

def view_memory_lane(lane_name):
    """View a specific memory lane"""
    if lane_name == "health":
        memory = st.session_state.health_memory
        title = "Health Memory Lane"
    elif lane_name == "work":
        memory = st.session_state.work_memory
        title = "Work Memory Lane"
    elif lane_name == "journal":
        memory = st.session_state.journal_memory
        title = "Journal Memory Lane"
    else:
        return
    
    st.subheader(title)
    
    if not memory:
        st.info(f"No memories stored in the {lane_name} lane yet.")
        return
    
    for i, entry in enumerate(reversed(memory)):
        with st.expander(f"Memory {len(memory) - i}: {entry['timestamp']}"):
            st.write("**User:**")
            st.write(entry['user_message'])
            st.write("**Tryambakam:**")
            st.write(entry['ai_response'])

def main():
    st.title("Overall Intelligence")
    
    # Initialize if needed
    if st.session_state.overall_intelligence is None and st.session_state.client:
        st.session_state.overall_intelligence = OverallIntelligence(st.session_state.client)
    
    # Sidebar for lane selection
    with st.sidebar:
        st.header("Memory Lanes")
        
        # Lane selection
        st.subheader("Select Memory Lane")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Health", use_container_width=True):
                switch_lane("health")
        with col2:
            if st.button("Work", use_container_width=True):
                switch_lane("work")
        with col3:
            if st.button("Journal", use_container_width=True):
                switch_lane("journal")
        
        # Show current lane
        st.info(f"Current lane: {st.session_state.current_lane.capitalize()}")
        
        # File upload
        st.file_uploader("Upload a document", 
                         key="uploaded_file", 
                         on_change=process_uploaded_file,
                         type=["txt", "pdf", "docx", "pptx"])
        
        # Back to main menu
        if st.button("Back to Main Menu"):
            st.switch_page("app.py")
    
    # Main chat area
    st.subheader(f"{st.session_state.current_lane.capitalize()} Memory Lane")
    
    # Chat messages
    chat_container = st.container()
    with chat_container:
        messages = st.session_state.lane_messages.get(st.session_state.current_lane, [])
        for i, msg in enumerate(messages):
            message(msg["human"], is_user=True, key=f"user_{i}")
            message(msg["ai"], is_user=False, key=f"ai_{i}")
    
    # Input area
    st.text_input("Message Tryambakam", 
                  key="widget_input", 
                  on_change=on_input_change)
    
    if st.session_state.user_input:
        send_message()
        st.rerun()

    # Sidebar
    with st.sidebar:
        st.header("Memory Lanes")
        
        # Memory lane navigation
        st.subheader("View Memory Lanes")
        memory_lane = st.radio(
            "Select View",
            ["Universal Chat", "Health Memories", "Work Memories", "Journal Memories"],
            index=0,
            key="memory_lane_selection"
        )
        
        # Back to main menu
        if st.button("Back to Main Menu", key="back_to_main"):
            st.switch_page("app.py")
    
    # Main content based on selected view
    if memory_lane == "Universal Chat":
        st.subheader("Universal Chat Interface")
        st.write("Chat naturally and your messages will be automatically categorized and stored in the appropriate memory lane.")
        
        # Chat container
        chat_container = st.container()
        
        # Input container
        input_container = st.container()
        
        # Display chat messages
        with chat_container:
            for i, msg in enumerate(st.session_state.universal_chat_history):
                if msg["role"] == "user":
                    message(msg["content"], is_user=True, key=f"msg_{i}")
                else:
                    # Show category badge for assistant messages
                    category = msg.get("category", "")
                    category_badge = f"**[{category.upper()}]** " if category else ""
                    message(category_badge + msg["content"], is_user=False, key=f"msg_{i}")
        
        # User input
        with input_container:
            st.text_input(
                "Your message:",
                key="user_input",
                on_change=process_message
            )
            
            # Voice input button (placeholder - actual implementation would require additional code)
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🎤", key="voice_input_button"):
                    st.info("Voice input functionality would be implemented here.")
    elif memory_lane == "Health Memories":
        view_memory_lane("health")
    elif memory_lane == "Work Memories":
        view_memory_lane("work")
    elif memory_lane == "Journal Memories":
        view_memory_lane("journal")

if __name__ == "__main__":
    main() 