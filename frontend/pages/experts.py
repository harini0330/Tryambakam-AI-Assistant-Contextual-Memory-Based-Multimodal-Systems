import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.voice_interface import voice_output
from backend.memory_sharing import get_memory_context_for_expert
from streamlit_chat import message

# Check if app is initialized
if 'initialized' not in st.session_state or not st.session_state.initialized:
    st.switch_page("app.py")

# Initialize session state for this page
if 'expert_chats' not in st.session_state:
    st.session_state.expert_chats = {}

# Define experts
EXPERTS = {
    "health": {
        "name": "Health & Wellness Expert",
        "description": "Specializes in physical health, nutrition, fitness, and wellness advice.",
        "system_prompt": "You are a health and wellness expert. Provide accurate, helpful advice on physical health, nutrition, fitness, and wellness topics. Always prioritize evidence-based information and recommend consulting healthcare professionals for serious concerns."
    },
    "work": {
        "name": "Career & Professional Development Expert",
        "description": "Specializes in career guidance, professional development, and workplace advice.",
        "system_prompt": "You are a career and professional development expert. Provide thoughtful guidance on career planning, job searching, workplace challenges, skill development, and professional growth."
    },
    "education": {
        "name": "Education & Learning Expert",
        "description": "Specializes in educational topics, learning strategies, and academic advice.",
        "system_prompt": "You are an education and learning expert. Provide knowledgeable guidance on educational topics, learning strategies, study techniques, academic planning, and educational resources."
    },
    "personal": {
        "name": "Personal Growth & Relationships Expert",
        "description": "Specializes in personal development, relationships, and life balance.",
        "system_prompt": "You are a personal growth and relationships expert. Provide compassionate guidance on personal development, relationships, emotional well-being, and life balance. Focus on practical advice while being supportive and understanding."
    }
}

def get_expert_chat_history(expert_id):
    """Get or initialize chat history for an expert"""
    if expert_id not in st.session_state.expert_chats:
        st.session_state.expert_chats[expert_id] = []
    return st.session_state.expert_chats[expert_id]

def send_message_to_expert(expert_id, message_text):
    """Send a message to an expert and get a response"""
    if not message_text:
        return
    
    # Get expert details
    expert = EXPERTS[expert_id]
    
    # Get chat history
    chat_history = get_expert_chat_history(expert_id)
    
    # Add user message to history
    chat_history.append({"role": "user", "content": message_text})
    
    # Get relevant memory context for this expert
    memory_context = get_memory_context_for_expert(expert_id)
    
    # Prepare messages for API
    messages = [
        {"role": "system", "content": expert["system_prompt"] + memory_context}
    ]
    
    # Add chat history (up to last 10 messages)
    for msg in chat_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Call the API
    with st.spinner(f"{expert['name']} is thinking..."):
        try:
            response = st.session_state.client.chat.completions.create(
                model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                messages=messages,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            chat_history.append({"role": "assistant", "content": ai_response})
            
            # Speak the response if voice is enabled
            if st.session_state.voice_enabled:
                voice_output.speak(ai_response)
                
            return ai_response
            
        except Exception as e:
            st.error(f"Error: {e}")
            return None

def display_expert_chat(expert_id):
    """Display the chat interface for an expert"""
    expert = EXPERTS[expert_id]
    
    st.header(expert["name"])
    st.write(expert["description"])
    
    # Chat history
    chat_history = get_expert_chat_history(expert_id)
    
    # Display chat messages
    for i, msg in enumerate(chat_history):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"{expert_id}_msg_{i}")
        else:
            message(msg["content"], is_user=False, key=f"{expert_id}_msg_{i}")
    
    # Input for new message
    user_input = st.text_input(
        "Your message:",
        key=f"{expert_id}_input"
    )
    
    if st.button("Send", key=f"{expert_id}_send"):
        if user_input:
            send_message_to_expert(expert_id, user_input)
            st.rerun()

def main():
    st.title("Expert Intelligence")
    
    # Sidebar
    with st.sidebar:
        st.header("Select an Expert")
        
        # Expert selection
        expert_id = st.radio(
            "Choose an expert to consult with:",
            list(EXPERTS.keys()),
            format_func=lambda x: EXPERTS[x]["name"]
        )
        
        # Back to main menu
        if st.button("Back to Main Menu"):
            st.switch_page("app.py")
    
    # Display the selected expert's chat interface
    display_expert_chat(expert_id)

if __name__ == "__main__":
    main() 