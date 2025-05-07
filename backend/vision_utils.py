import base64
import cv2
import os
import tempfile
from PIL import Image
import io
import time
import openai
import streamlit as st

def encode_image_file(image_path):
    """Encode an image file to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def encode_image_bytes(image_bytes):
    """Encode image bytes to base64"""
    return base64.b64encode(image_bytes).decode("utf-8")

def process_uploaded_image(uploaded_file):
    """Process an uploaded image file from Streamlit"""
    if uploaded_file is None:
        return None, "No file uploaded"
    
    try:
        # Read the file
        image_bytes = uploaded_file.getvalue()
        
        # Convert to base64
        base64_image = encode_image_bytes(image_bytes)
        
        return base64_image, "Image processed successfully"
    except Exception as e:
        return None, f"Error processing image: {e}"

def capture_webcam_image():
    """Capture an image from the webcam"""
    try:
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Could not open webcam"
        
        # Capture frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None, "Failed to capture image from webcam"
        
        # Convert to base64
        _, buffer = cv2.imencode(".jpg", frame)
        base64_image = base64.b64encode(buffer).decode("utf-8")
        
        return base64_image, "Webcam image captured successfully"
    except Exception as e:
        return None, f"Error capturing webcam image: {e}"

def generate_vision_response(client, prompt, image_base64):
    """Generate a response using the vision model with OpenAI format"""
    try:
        # Create a direct OpenAI client with the OpenAI API key from session state
        openai_client = openai.OpenAI(
            api_key=st.session_state.openai_api_key,  # Use the OpenAI API key, not the client's API key
            base_url="https://api.openai.com/v1"  # Use the official OpenAI API
        )
        
        # Use the OpenAI GPT-4 Vision API format
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
        
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        # If OpenAI direct API fails, try with the client's API
        try:
            # Simple text-only request as fallback
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that can analyze images, but the image could not be processed. Please apologize and explain that there was an issue with image processing."},
                    {"role": "user", "content": f"I wanted you to analyze this image with the following prompt: {prompt}"}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content.strip(), f"Vision API failed, using text-only fallback. Error: {e}"
        except Exception as e2:
            return None, f"Error generating vision response: {e}. Fallback also failed: {e2}"

def analyze_image_content(client, image_base64):
    """Analyze the content of an image (what's in the image)"""
    prompt = "Describe what you see in this image in detail. Include objects, people, scenes, colors, and any text visible."
    return generate_vision_response(client, prompt, image_base64)

def analyze_image_text(client, image_base64):
    """Extract and analyze text from an image"""
    prompt = "Extract and read all text visible in this image. If there's no text, just say 'No text found in the image.'"
    return generate_vision_response(client, prompt, image_base64)

def analyze_image_emotions(client, image_base64):
    """Analyze emotions and expressions in the image"""
    prompt = "Analyze the emotions and expressions of any people in this image. If there are no people, describe the mood or atmosphere of the image."
    return generate_vision_response(client, prompt, image_base64)

def analyze_image_objects(client, image_base64):
    """Identify and count objects in the image"""
    prompt = "Identify and count all distinct objects in this image. List them in order of prominence."
    return generate_vision_response(client, prompt, image_base64)

def analyze_image_comprehensive(client, image_base64):
    """Perform a comprehensive analysis of the image"""
    prompt = """Perform a comprehensive analysis of this image:
1. Describe the main subject and setting
2. Identify key objects and their relationships
3. Note any text visible and its context
4. Analyze the composition, colors, and visual elements
5. Interpret the mood, tone, or message of the image
6. Provide any additional relevant observations"""
    return generate_vision_response(client, prompt, image_base64)

def continuous_webcam_analysis(client, analysis_type="general", max_duration=60):
    """Run continuous webcam analysis for a specified duration"""
    try:
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Could not open webcam"
        
        start_time = time.time()
        results = []
        
        while time.time() - start_time < max_duration:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                break
            
            # Display the frame
            cv2.imshow('Webcam Analysis (Press ESC to stop)', frame)
            
            # Process every 5 seconds
            if int(time.time() - start_time) % 5 == 0:
                # Convert to base64
                _, buffer = cv2.imencode(".jpg", frame)
                base64_image = base64.b64encode(buffer).decode("utf-8")
                
                # Analyze based on type
                if analysis_type == "general":
                    response, _ = analyze_image_content(client, base64_image)
                elif analysis_type == "text":
                    response, _ = analyze_image_text(client, base64_image)
                elif analysis_type == "emotions":
                    response, _ = analyze_image_emotions(client, base64_image)
                elif analysis_type == "objects":
                    response, _ = analyze_image_objects(client, base64_image)
                
                timestamp = time.strftime("%H:%M:%S")
                results.append(f"[{timestamp}] {response}")
            
            # Check for ESC key to exit
            if cv2.waitKey(1) == 27:  # ESC key
                break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        
        return "\n\n".join(results)
    
    except Exception as e:
        return f"Error in continuous analysis: {e}" 