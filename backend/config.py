import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable or use the provided key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Check if API key is set
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. API calls will fail.")
    print("Please create a .env file with your OpenAI API key.")
else:
    print(f"Using OpenAI API key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]}") 