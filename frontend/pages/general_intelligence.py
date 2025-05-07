import streamlit as st
import sys
import os
import time
import tempfile

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.chat_manager import ChatManager
from backend.voice_interface import voice_output
from streamlit_chat import message

# Initialize session state for this page
if 'chat_manager' not in st.session_state:
    st.session_state.chat_manager = ChatManager()

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
    
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None
    
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Check if app is initialized
if 'initialized' not in st.session_state or not st.session_state.initialized:
    st.switch_page("app.py")

def create_new_chat():
    """Create a new chat page"""
    title = st.session_state.new_chat_title
    if title:
        page_id, chat_page = st.session_state.chat_manager.create_chat_page(title)
        st.session_state.current_chat_id = page_id
        st.session_state.current_chat = chat_page
        st.session_state.chat_messages = chat_page.get_chat_history()
        st.success(f"Created new chat: {title}")
        st.session_state.new_chat_title = ""  # Clear the input
        st.rerun()

def switch_chat(page_id):
    """Switch to a different chat page"""
    chat_page = st.session_state.chat_manager.get_chat_page(page_id)
    if chat_page:
        st.session_state.current_chat_id = page_id
        st.session_state.current_chat = chat_page
        st.session_state.chat_messages = chat_page.get_chat_history()
        st.rerun()

def delete_chat(page_id):
    """Delete a chat page"""
    if page_id == st.session_state.current_chat_id:
        st.session_state.current_chat_id = None
        st.session_state.current_chat = None
        st.session_state.chat_messages = []
    
    success, message = st.session_state.chat_manager.delete_chat_page(page_id)
    if success:
        st.success(message)
    else:
        st.error(message)
    st.rerun()

def process_uploaded_file():
    """Process an uploaded file"""
    if st.session_state.current_chat is None:
        st.error("Please select or create a chat first")
        return
    
    uploaded_file = st.session_state.uploaded_file
    if uploaded_file:
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        
        # Process the file
        success, message = st.session_state.current_chat.process_file(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        if success:
            st.success(message)
        else:
            st.error(message)

def on_input_change():
    """Handle user input changes"""
    st.session_state.user_input = st.session_state.widget_input
    st.session_state.widget_input = ""  # Clear the input box

def send_message():
    """Send a message to the AI"""
    if not st.session_state.user_input or not st.session_state.current_chat:
        return
    
    user_input = st.session_state.user_input
    st.session_state.user_input = ""
    
    # Get messages for API
    messages = st.session_state.current_chat.get_messages_for_api()
    messages.append({"role": "user", "content": user_input})
    
    # Show user message immediately
    st.session_state.chat_messages.append({
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
            
            # Update the last message with the AI response
            st.session_state.chat_messages[-1]["ai"] = ai_response
            st.session_state.chat_messages[-1]["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Save to chat history
            st.session_state.current_chat.save_history(user_input, ai_response)
            
            # Speak the response if voice is enabled
            if st.session_state.voice_enabled:
                voice_output.speak(ai_response)
                
        except Exception as e:
            st.error(f"Error: {e}")
            # Remove the last message if there was an error
            if st.session_state.chat_messages:
                st.session_state.chat_messages.pop()

def main():
    st.title("General Intelligence")
    
    # Sidebar for chat management
    with st.sidebar:
        st.header("Chat Management")
        
        # Create new chat
        st.subheader("Create New Chat")
        st.text_input("Chat Title", key="new_chat_title")
        st.button("Create", on_click=create_new_chat)
        
        # List existing chats
        st.subheader("Your Chats")
        chat_list = st.session_state.chat_manager.list_chat_pages()
        
        if not chat_list:
            st.info("No chats found. Create a new chat to get started.")
        else:
            for page_id, title in chat_list:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    if st.button(f"{title}", key=f"chat_{page_id}", use_container_width=True):
                        switch_chat(page_id)
                with col2:
                    if st.button("🗑️", key=f"delete_{page_id}"):
                        # Show confirmation dialog
                        if st.session_state.get(f"confirm_delete_{page_id}", False):
                            delete_chat(page_id)
                            st.session_state[f"confirm_delete_{page_id}"] = False
                        else:
                            st.session_state[f"confirm_delete_{page_id}"] = True
                            st.warning(f"Click again to confirm deletion of '{title}'")
                with col3:
                    if st.session_state.current_chat_id == page_id:
                        st.success("✓")
        
        # Back to main menu
        if st.button("Back to Main Menu"):
            st.switch_page("app.py")
    
    # Main chat area
    if st.session_state.current_chat:
        st.subheader(f"Chat: {st.session_state.current_chat.title}")
        
        # File upload
        st.file_uploader("Upload a document to the chat", 
                         key="uploaded_file", 
                         on_change=process_uploaded_file,
                         type=["txt", "pdf", "docx", "pptx"])
        
        # Chat messages
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state.chat_messages):
                message(msg["human"], is_user=True, key=f"user_{i}")
                message(msg["ai"], is_user=False, key=f"ai_{i}")
        
        # Input area
        st.text_input("Message Tryambakam", 
                      key="widget_input", 
                      on_change=on_input_change)
        
        if st.session_state.user_input:
            send_message()
            st.rerun()
    else:
        st.info("Please select an existing chat or create a new one to start.")

if __name__ == "__main__":
    main() 