import streamlit as st
import sys
import os
import base64

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.voice_interface import voice_output
import openai

# Default API key from your existing code
DEFAULT_API_KEY = "glhf_4bcabf37973c831859edc8b224c682f4"

# Add these lines after the DEFAULT_API_KEY definition
DEFAULT_OPENAI_API_KEY = "" # OpenAI API key for vision

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.api_key = DEFAULT_API_KEY  # Use default API key
    st.session_state.openai_api_key = DEFAULT_OPENAI_API_KEY  # Use default OpenAI API key
    st.session_state.client = None
    st.session_state.voice_enabled = False

def initialize_app():
    """Initialize the app with API key and client"""
    if st.session_state.api_key:
        try:
            # Initialize OpenAI client
            client = openai.OpenAI(
                api_key=st.session_state.api_key,
                base_url="https://glhf.chat/api/openai/v1",
            )
            
            # Test the client with a simple request
            response = client.chat.completions.create(
                model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                messages=[
                    {"role": "system", "content": "You are Tryambakam."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            
            st.session_state.client = client
            st.session_state.initialized = True
            
            # Initialize voice
            st.session_state.voice_enabled = voice_output.voice_enabled
            
            return True
        except Exception as e:
            st.error(f"Error initializing API: {e}")
            return False
    else:
        st.error("Please enter an API key")
        return False

# Function to load local CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "styles", "main.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to load local JavaScript
def load_js():
    js_file = os.path.join(os.path.dirname(__file__), "scripts", "animations.js")
    with open(js_file, "r") as f:
        st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# Function to create a pulsing AI brain animation
def ai_brain_animation():
    st.markdown("""
    <div class="ai-brain"></div>
    """, unsafe_allow_html=True)

# Function to create a loading animation
def loading_animation():
    st.markdown("""
    <div class="loading-animation">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Tryambakam Intelligence System",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS and JavaScript
    load_css()
    load_js()
    
    st.title("Tryambakam Intelligence System")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input(
            "API Key", 
            value=st.session_state.api_key if st.session_state.api_key else "",
            type="password",
            help="Enter your API key for the LLM service"
        )
        
        # OpenAI API Key input for vision
        openai_api_key = st.text_input(
            "OpenAI API Key (for Vision)", 
            value=st.session_state.openai_api_key if st.session_state.openai_api_key else "",
            type="password",
            help="Enter your OpenAI API key for vision capabilities"
        )
        
        if st.button("Initialize"):
            with st.spinner("Initializing..."):
                st.session_state.api_key = api_key
                st.session_state.openai_api_key = openai_api_key
                success = initialize_app()
                if success:
                    st.success("Initialization successful!")
                    loading_animation()
        
        # Auto-initialize on first load
        if not st.session_state.initialized and st.session_state.api_key:
            with st.spinner("Auto-initializing..."):
                initialize_app()
        
        # Voice toggle
        if st.session_state.initialized:
            voice_enabled = st.checkbox(
                "Enable Voice Output", 
                value=st.session_state.voice_enabled,
                help="Toggle voice output on/off"
            )
            
            if voice_enabled != st.session_state.voice_enabled:
                voice_output.toggle_voice()
                st.session_state.voice_enabled = voice_output.voice_enabled
    
    # Main content
    if not st.session_state.initialized:
        st.info("Please enter your API key in the sidebar and click Initialize to start.")
        
        # Show animated AI brain
        ai_brain_animation()
        
        # Show demo information with animation
        st.markdown("""
        <div class="welcome-container">
            <h2>Welcome to Tryambakam</h2>
            <p>Tryambakam is an advanced AI assistant system with multiple intelligence modes:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>General Intelligence</h3>
                <p>Chat with the AI in separate chat pages</p>
            </div>
            
            <div class="feature-card">
                <h3>Overall Intelligence</h3>
                <p>Access memory lanes for health, work, and journal</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>Expert Intelligence</h3>
                <p>Consult with specialized AI experts</p>
            </div>
            
            <div class="feature-card">
                <h3>Vision Intelligence</h3>
                <p>Analyze images and visual content</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="welcome-footer">
            <p>Enter your API key to get started!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show the main navigation with animated cards
        st.header("Select Intelligence Mode")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="mode-card" id="general-card">
                <h3>General Intelligence</h3>
                <p>Chat with the AI in separate chat pages</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter General Intelligence", key="general_btn"):
                st.switch_page("pages/general_intelligence.py")
            
            st.markdown("""
            <div class="mode-card" id="overall-card">
                <h3>Overall Intelligence</h3>
                <p>Access memory lanes for health, work, and journal</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter Overall Intelligence", key="overall_btn"):
                st.switch_page("pages/overall_intelligence.py")
                
        with col2:
            st.markdown("""
            <div class="mode-card" id="expert-card">
                <h3>Expert Intelligence</h3>
                <p>Consult with specialized AI experts</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter Expert Intelligence", key="expert_btn"):
                st.switch_page("pages/experts.py")
                
            st.markdown("""
            <div class="mode-card" id="vision-card">
                <h3>Vision Intelligence</h3>
                <p>Analyze images and visual content</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Enter Vision Intelligence", key="vision_btn"):
                st.switch_page("pages/vision.py")
        
        # Show system information with animation
        st.subheader("System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="status-card">
                <h4>API Status</h4>
                <p class="status-active">Connected</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="status-card">
                <h4>Voice Output</h4>
                <p class="status-{'active' if st.session_state.voice_enabled else 'inactive'}">
                    {'Enabled' if st.session_state.voice_enabled else 'Disabled'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="status-card">
                <h4>Vision Capabilities</h4>
                <p class="status-active">Available</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 