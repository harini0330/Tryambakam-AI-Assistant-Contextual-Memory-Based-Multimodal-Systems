import os
import subprocess
import sys
import shutil

def main():
    # Create necessary directories
    os.makedirs("frontend/pages", exist_ok=True)
    os.makedirs("frontend/styles", exist_ok=True)
    os.makedirs("frontend/scripts", exist_ok=True)
    os.makedirs("frontend/assets", exist_ok=True)
    os.makedirs("temp", exist_ok=True)  # For temporary file uploads
    
    # Create CSS and JS files if they don't exist
    css_file = "frontend/styles/main.css"
    js_file = "frontend/scripts/animations.js"
    
    if not os.path.exists(css_file):
        with open(css_file, "w") as f:
            f.write("/* Main CSS for Tryambakam Intelligence System */\n")
    
    if not os.path.exists(js_file):
        with open(js_file, "w") as f:
            f.write("// Animations for Tryambakam Intelligence System\n")
    
    # Required packages
    required_packages = [
        "streamlit",
        "streamlit-chat",
        "streamlit-webrtc",
        "openai",
        "langchain",
        "PyPDF2",
        "python-docx",
        "python-pptx",
        "opencv-python",
        "pillow",
        "python-dotenv",
        "pyttsx3",
        "streamlit-lottie"  # For Lottie animations
    ]
    
    # Check and install required packages
    print("Checking required packages...")
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
    
    # Check for OpenCV (vision capabilities)
    try:
        import cv2
        print("✓ Vision capabilities are available")
    except ImportError:
        print("⚠️ OpenCV is not properly installed. Vision capabilities may be limited.")
        print("  Try manually installing with: pip install opencv-python")
    
    # Start the Streamlit app
    print("\nStarting Tryambakam Intelligence System...")
    subprocess.call(["streamlit", "run", "frontend/app.py"])

if __name__ == "__main__":
    main() 