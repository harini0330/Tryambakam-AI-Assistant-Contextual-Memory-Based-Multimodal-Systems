import base64
import cv2
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key="")

# Webcam handler
class WebcamStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(0)
        if not self.stream.isOpened():
            raise ValueError("Could not open webcam.")
        self.frame = None

    def read_frame(self, encode=False):
        ret, frame = self.stream.read()
        if not ret:
            return None
        if encode:
            _, buffer = cv2.imencode(".jpeg", frame)
            return base64.b64encode(buffer).decode()
        return frame

    def stop(self):
        self.stream.release()

# Function to encode image from file
def encode_image_file(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Generate response using OpenAI GPT
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
        return f"Error: {e}"

# Main program
webcam = None

try:
    while True:
        command = input("Enter command (vision/upload/quit): ").lower()
        
        if command == "quit":
            break
            
        elif command == "vision":
            if webcam is None:
                webcam = WebcamStream()
            
            while True:
                manual_input = input("Type a prompt (or 'back' to return to main menu): ")
                if manual_input.lower() == 'back':
                    break
                    
                # Read webcam frame and encode it
                image_base64 = webcam.read_frame(encode=True)
                if not image_base64:
                    print("Error: Could not read webcam frame.")
                    continue

                # Generate response
                response = generate_response(manual_input, image_base64)
                print(response)
                
                # Display the webcam feed
                frame = webcam.read_frame()
                if frame is not None:
                    cv2.imshow("Webcam Feed", frame)
                    if cv2.waitKey(1) in [27, ord("q")]:  # 'Esc' or 'q' to quit
                        break
                        
        elif command == "upload":
            image_path = input("Enter the path to your image: ")
            if os.path.exists(image_path):
                try:
                    image_base64 = encode_image_file(image_path)
                    prompt = input("Enter your prompt: ")
                    response = generate_response(prompt, image_base64)
                    print(response)
                except Exception as e:
                    print(f"Error processing image: {e}")
            else:
                print("Invalid file path. Please try again.")
                
        else:
            print("Invalid command. Please use 'vision', 'upload', or 'quit'")

except KeyboardInterrupt:
    print("\nProgram terminated by user")
finally:
    if webcam:
        webcam.stop()
    cv2.destroyAllWindows()
