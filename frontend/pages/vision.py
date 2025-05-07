import streamlit as st
import sys
import os
import tempfile
import time
import threading

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.vision_utils import (
    process_uploaded_image, 
    capture_webcam_image, 
    generate_vision_response,
    analyze_image_content,
    analyze_image_text,
    analyze_image_emotions,
    analyze_image_objects,
    analyze_image_comprehensive,
    continuous_webcam_analysis
)
from backend.voice_interface import voice_output

# Check if app is initialized
if 'initialized' not in st.session_state or not st.session_state.initialized:
    st.switch_page("app.py")

# Initialize session state for this page
if 'vision_history' not in st.session_state:
    st.session_state.vision_history = []

if 'continuous_analysis_results' not in st.session_state:
    st.session_state.continuous_analysis_results = []

def process_vision_query(image_base64, prompt):
    """Process a vision query with the given image and prompt"""
    if not image_base64 or not prompt:
        st.error("Both image and prompt are required")
        return
    
    with st.spinner("Analyzing image..."):
        try:
            # Check if OpenAI API key is available
            if hasattr(st.session_state, 'openai_api_key') and st.session_state.openai_api_key:
                # Create a temporary client with OpenAI API key
                import openai
                openai_client = openai.OpenAI(
                    api_key=st.session_state.openai_api_key,
                    base_url="https://api.openai.com/v1"
                )
                
                # Use OpenAI's vision API directly
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500
                )
                
                response_text = response.choices[0].message.content.strip()
                error = None
            else:
                # Fall back to the regular client
                response_text, error = generate_vision_response(st.session_state.client, prompt, image_base64)
            
            if error:
                st.error(error)
                st.warning("Vision API error. Trying text-only fallback...")
                
                # Fallback to text-only analysis
                fallback_response = st.session_state.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an AI assistant that can analyze images, but the image could not be processed. Please apologize and explain that there was an issue with image processing."},
                        {"role": "user", "content": f"I wanted you to analyze this image with the following prompt: {prompt}"}
                    ],
                    max_tokens=500
                )
                
                response_text = fallback_response.choices[0].message.content.strip()
                st.warning("Using text-only fallback response")
            
            # Add to history
            st.session_state.vision_history.append({
                "image": image_base64,
                "prompt": prompt,
                "response": response_text
            })
            
            # Speak the response if voice is enabled
            if st.session_state.voice_enabled:
                voice_output.speak(response_text)
            
            return response_text
        except Exception as e:
            st.error(f"Error processing vision query: {e}")
            return None

def run_analysis(image_base64, analysis_type):
    """Run a specific type of analysis on an image"""
    if not image_base64:
        st.error("No image available for analysis")
        return
    
    with st.spinner(f"Running {analysis_type} analysis..."):
        try:
            if analysis_type == "content":
                response, error = analyze_image_content(st.session_state.client, image_base64)
            elif analysis_type == "text":
                response, error = analyze_image_text(st.session_state.client, image_base64)
            elif analysis_type == "emotions":
                response, error = analyze_image_emotions(st.session_state.client, image_base64)
            elif analysis_type == "objects":
                response, error = analyze_image_objects(st.session_state.client, image_base64)
            elif analysis_type == "comprehensive":
                response, error = analyze_image_comprehensive(st.session_state.client, image_base64)
            else:
                return None, "Invalid analysis type"
            
            if error:
                st.error(error)
                return
            
            # Add to history
            st.session_state.vision_history.append({
                "image": image_base64,
                "prompt": f"{analysis_type.capitalize()} Analysis",
                "response": response
            })
            
            # Speak the response if voice is enabled
            if st.session_state.voice_enabled:
                voice_output.speak(response)
            
            return response
        except Exception as e:
            st.error(f"Error in {analysis_type} analysis: {e}")
            return None

def main():
    st.title("Vision Intelligence")
    
    # Sidebar
    with st.sidebar:
        st.header("Vision Options")
        
        # Analysis mode selection
        st.subheader("Analysis Mode")
        analysis_mode = st.radio(
            "Select Mode",
            ["Single Image", "Continuous Webcam"],
            index=0
        )
        
        # Back to main menu
        if st.button("Back to Main Menu", key="back_to_main"):
            st.switch_page("app.py")
    
    # Main content based on mode
    if analysis_mode == "Single Image":
        # Tabs for different image input methods
        tab1, tab2 = st.tabs(["Upload Image", "Webcam Capture"])
        
        with tab1:
            # Image upload
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="upload_image")
            
            if uploaded_file:
                # Display the image
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                
                # Process the image
                image_base64, message = process_uploaded_image(uploaded_file)
                
                if image_base64:
                    # Analysis options
                    st.subheader("Analysis Options")
                    
                    # Custom prompt
                    st.write("**Custom Analysis**")
                    prompt = st.text_input("Ask about this image:", key="upload_prompt")
                    if st.button("Analyze with Custom Prompt", key="upload_analyze_custom") and prompt:
                        response = process_vision_query(image_base64, prompt)
                        if response:
                            st.markdown("### Analysis Result")
                            st.write(response)
                    
                    # Pre-defined analyses
                    st.write("**Pre-defined Analyses**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Content Analysis", key="upload_content", use_container_width=True):
                            response = run_analysis(image_base64, "content")
                            if response:
                                st.markdown("### Content Analysis")
                                st.write(response)
                        
                        if st.button("Text Extraction", key="upload_text", use_container_width=True):
                            response = run_analysis(image_base64, "text")
                            if response:
                                st.markdown("### Text Extraction")
                                st.write(response)
                    
                    with col2:
                        if st.button("Emotion Analysis", key="upload_emotions", use_container_width=True):
                            response = run_analysis(image_base64, "emotions")
                            if response:
                                st.markdown("### Emotion Analysis")
                                st.write(response)
                        
                        if st.button("Object Detection", key="upload_objects", use_container_width=True):
                            response = run_analysis(image_base64, "objects")
                            if response:
                                st.markdown("### Object Detection")
                                st.write(response)
                    
                    if st.button("Comprehensive Analysis", key="upload_comprehensive", use_container_width=True):
                        response = run_analysis(image_base64, "comprehensive")
                        if response:
                            st.markdown("### Comprehensive Analysis")
                            st.write(response)
                else:
                    st.error(message)
        
        with tab2:
            # Webcam capture
            if st.button("Capture from Webcam", key="webcam_capture"):
                with st.spinner("Accessing webcam..."):
                    image_base64, message = capture_webcam_image()
                    
                    if image_base64:
                        # Display the captured image
                        st.image(f"data:image/jpeg;base64,{image_base64}", caption="Captured Image", use_column_width=True)
                        
                        # Store in session state for later use
                        st.session_state.webcam_image = image_base64
                        
                        st.success("Image captured successfully")
                    else:
                        st.error(message)
            
            # If we have a captured image
            if 'webcam_image' in st.session_state:
                # Analysis options
                st.subheader("Analysis Options")
                
                # Custom prompt
                st.write("**Custom Analysis**")
                prompt = st.text_input("Ask about the webcam image:", key="webcam_prompt")
                if st.button("Analyze with Custom Prompt", key="webcam_analyze_custom") and prompt:
                    response = process_vision_query(st.session_state.webcam_image, prompt)
                    if response:
                        st.markdown("### Analysis Result")
                        st.write(response)
                
                # Pre-defined analyses
                st.write("**Pre-defined Analyses**")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Content Analysis", key="webcam_content", use_container_width=True):
                        response = run_analysis(st.session_state.webcam_image, "content")
                        if response:
                            st.markdown("### Content Analysis")
                            st.write(response)
                    
                    if st.button("Text Extraction", key="webcam_text", use_container_width=True):
                        response = run_analysis(st.session_state.webcam_image, "text")
                        if response:
                            st.markdown("### Text Extraction")
                            st.write(response)
                
                with col2:
                    if st.button("Emotion Analysis", key="webcam_emotions", use_container_width=True):
                        response = run_analysis(st.session_state.webcam_image, "emotions")
                        if response:
                            st.markdown("### Emotion Analysis")
                            st.write(response)
                    
                    if st.button("Object Detection", key="webcam_objects", use_container_width=True):
                        response = run_analysis(st.session_state.webcam_image, "objects")
                        if response:
                            st.markdown("### Object Detection")
                            st.write(response)
                
                    if st.button("Comprehensive Analysis", key="webcam_comprehensive", use_container_width=True):
                        response = run_analysis(st.session_state.webcam_image, "comprehensive")
                        if response:
                            st.markdown("### Comprehensive Analysis")
                            st.write(response)
    
    else:  # Continuous Webcam mode
        st.subheader("Continuous Webcam Analysis")
        st.warning("Note: This will open a separate window for webcam feed. Press ESC to stop the analysis.")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["general", "text", "emotions", "objects"],
            index=0,
            key="continuous_analysis_type"
        )
        
        # Duration selection
        duration = st.slider("Analysis Duration (seconds)", 10, 120, 30, key="continuous_duration")
        
        if st.button("Start Continuous Analysis", key="start_continuous"):
            with st.spinner(f"Running continuous {analysis_type} analysis for {duration} seconds..."):
                # This will block the UI, but it's necessary for the webcam window
                results = continuous_webcam_analysis(
                    st.session_state.client, 
                    analysis_type=analysis_type, 
                    max_duration=duration
                )
                
                # Store results
                st.session_state.continuous_analysis_results.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": analysis_type,
                    "duration": duration,
                    "results": results
                })
                
                # Display results
                st.subheader("Analysis Results")
                st.text_area("Results", results, height=300, key="continuous_results")
    
    # History section
    if st.session_state.vision_history:
        st.subheader("Analysis History")
        
        for i, entry in enumerate(reversed(st.session_state.vision_history)):
            with st.expander(f"Analysis {len(st.session_state.vision_history) - i}: {entry['prompt'][:50]}..."):
                st.image(f"data:image/jpeg;base64,{entry['image']}", width=300)
                st.write(f"**Prompt:** {entry['prompt']}")
                st.write(f"**Response:** {entry['response']}")
    
    # Continuous analysis history
    if st.session_state.continuous_analysis_results:
        st.subheader("Continuous Analysis History")
        
        for i, entry in enumerate(reversed(st.session_state.continuous_analysis_results)):
            with st.expander(f"Continuous Analysis {len(st.session_state.continuous_analysis_results) - i}: {entry['type']} ({entry['timestamp']})"):
                st.write(f"**Type:** {entry['type']}")
                st.write(f"**Duration:** {entry['duration']} seconds")
                st.write(f"**Timestamp:** {entry['timestamp']}")
                st.text_area(f"Results {i}", entry['results'], height=200, key=f"history_results_{i}")

if __name__ == "__main__":
    main() 