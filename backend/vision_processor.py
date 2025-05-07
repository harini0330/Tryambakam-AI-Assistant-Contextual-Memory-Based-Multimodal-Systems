import cv2
import base64
import os
from backend.config import client

class VisionProcessor:
    def __init__(self):
        pass
        
    def process_image(self, image_data, prompt):
        """Process an image with a given prompt"""
        # This is a placeholder - in a real implementation, 
        # you would call the vision API here
        return "Image analysis result would appear here"
        
    def encode_image(self, image_path):
        """Encode an image file to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

def generate_response(prompt, image_base64):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated model name
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Vision API error: {e}")
        return f"Error: {e}" 