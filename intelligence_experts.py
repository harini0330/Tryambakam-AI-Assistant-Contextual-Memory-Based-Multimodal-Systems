import os
import json
import openai
from datetime import datetime
from langchain.schema import SystemMessage
from voice_interface import voice_output

# Directory structure
BASE_DIR = "chat_histories"
OVERALL_DIR = os.path.join(BASE_DIR, "overall_intelligence")
EXPERTS_DIR = os.path.join(OVERALL_DIR, "intelligence_experts")

# Expert definitions with their specialized prompts
EXPERTS = {
    "doctor": {
        "name": "Dr. Tryambakam",
        "prompt": "You are Dr. Tryambakam, a medical expert with extensive knowledge in healthcare. You provide accurate medical information, but always remind users to consult with their actual healthcare provider for personalized medical advice. You have access to the user's health-related memory lane to provide more personalized assistance.",
        "memory_lane": "health"
    },
    "teacher": {
        "name": "Professor Tryambakam",
        "prompt": "You are Professor Tryambakam, an educational expert with deep knowledge across multiple disciplines. You excel at explaining complex concepts in simple terms, providing examples, and guiding users through learning processes. You have access to the user's education-related memory lane to provide more personalized assistance.",
        "memory_lane": "work"
    },
    "therapist": {
        "name": "Counselor Tryambakam",
        "prompt": "You are Counselor Tryambakam, a compassionate therapist who listens attentively and provides supportive guidance. While you're not a replacement for professional mental health services, you can offer reflective listening, coping strategies, and general well-being advice. You have access to the user's journal memory lane to provide more personalized assistance.",
        "memory_lane": "journal"
    }
}

# Create necessary directories
if not os.path.exists(EXPERTS_DIR):
    os.makedirs(EXPERTS_DIR)

for expert_id in EXPERTS:
    expert_dir = os.path.join(EXPERTS_DIR, expert_id)
    if not os.path.exists(expert_dir):
        os.makedirs(expert_dir)

class IntelligenceExpert:
    def __init__(self, expert_id, api_client):
        if expert_id not in EXPERTS:
            raise ValueError(f"Unknown expert: {expert_id}")
        
        self.expert_id = expert_id
        self.expert_info = EXPERTS[expert_id]
        self.name = self.expert_info["name"]
        self.prompt = self.expert_info["prompt"]
        self.memory_lane_type = self.expert_info["memory_lane"]
        self.client = api_client
        
        # Set up file paths
        self.expert_dir = os.path.join(EXPERTS_DIR, expert_id)
        self.conversation_file = os.path.join(self.expert_dir, f"{expert_id}_conversations.json")
        self.memory_lane_file = os.path.join(
            OVERALL_DIR, 
            f"{self.memory_lane_type}_memory", 
            f"{self.memory_lane_type}_memory.json"
        )
        
        # Initialize conversation history
        self.conversation_history = self.load_conversation_history()
    
    def load_conversation_history(self):
        """Load the expert's conversation history"""
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def load_memory_lane(self):
        """Load relevant memory lane data"""
        memory_lane_data = []
        if os.path.exists(self.memory_lane_file):
            try:
                with open(self.memory_lane_file, 'r', encoding='utf-8') as f:
                    memory_lane_data = json.load(f)
            except json.JSONDecodeError:
                pass
        return memory_lane_data
    
    def save_conversation(self, user_input, ai_response):
        """Save the current conversation to the expert's history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "human": user_input,
            "ai": ai_response
        }
        
        self.conversation_history.append(entry)
        
        with open(self.conversation_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        
        # Also save to the memory lane
        self.save_to_memory_lane(user_input, ai_response)
    
    def save_to_memory_lane(self, user_input, ai_response):
        """Save the conversation to the appropriate memory lane"""
        memory_lane_data = self.load_memory_lane()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "expert": self.expert_id,
            "human": user_input,
            "ai": ai_response
        }
        
        memory_lane_data.append(entry)
        
        # Ensure the directory exists
        memory_lane_dir = os.path.dirname(self.memory_lane_file)
        if not os.path.exists(memory_lane_dir):
            os.makedirs(memory_lane_dir)
            
        with open(self.memory_lane_file, 'w', encoding='utf-8') as f:
            json.dump(memory_lane_data, f, ensure_ascii=False, indent=2)
    
    def get_response(self, user_input):
        """Generate a response from the expert based on conversation history and memory lane"""
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": self.prompt}
            ]
            
            # Add relevant memory lane context
            memory_lane_data = self.load_memory_lane()
            if memory_lane_data:
                memory_context = f"Here is some relevant information from the user's {self.memory_lane_type} history:\n\n"
                # Include up to 5 most recent relevant entries
                for entry in memory_lane_data[-5:]:
                    if "human" in entry and "ai" in entry:
                        memory_context += f"User: {entry['human']}\n"
                        memory_context += f"Response: {entry['ai']}\n\n"
                
                messages.append({"role": "system", "content": memory_context})
            
            # Add conversation history (up to 10 most recent exchanges)
            for entry in self.conversation_history[-10:]:
                if "human" in entry and "ai" in entry:
                    messages.append({"role": "user", "content": entry["human"]})
                    messages.append({"role": "assistant", "content": entry["ai"]})
            
            # Add the current user input
            messages.append({"role": "user", "content": user_input})
            
            # Get response from the API
            completion = self.client.chat.completions.create(
                model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                messages=messages,
                stream=True
            )
            
            print(f"\n{self.name}: ", end='')
            assistant_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    assistant_response += content
                    print(content, end='', flush=True)
            print()
            
            # Add voice output for the complete response
            voice_output.speak(assistant_response)
            
            # Save the conversation
            self.save_conversation(user_input, assistant_response)
            
            return assistant_response
            
        except Exception as e:
            error_message = f"Error getting response from {self.name}: {e}"
            print(error_message)
            return error_message

class ExpertsManager:
    def __init__(self, api_client):
        self.client = api_client
        self.experts = {}
    
    def get_expert(self, expert_id):
        """Get or create an expert instance"""
        if expert_id not in self.experts:
            if expert_id in EXPERTS:
                self.experts[expert_id] = IntelligenceExpert(expert_id, self.client)
            else:
                return None
        return self.experts[expert_id]
    
    def list_experts(self):
        """List all available experts"""
        print("\nAvailable Intelligence Experts:")
        for expert_id, expert_info in EXPERTS.items():
            print(f"- {expert_info['name']} ({expert_id}): Specializes in {expert_info['memory_lane']} topics")
    
    def expert_interface(self, expert_id):
        """Interface for interacting with a specific expert"""
        expert = self.get_expert(expert_id)
        if not expert:
            print(f"Expert '{expert_id}' not found.")
            return
        
        print(f"\nConnecting to {expert.name}...")
        print(f"Type 'back' to return to experts menu or 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'back':
                break
            if user_input.lower() == 'exit':
                return True
            
            expert.get_response(user_input)
        
        return False
    
    def experts_menu(self):
        """Main menu for the intelligence experts system"""
        print("\nIntelligence Experts System")
        self.list_experts()
        print("\nCommands:")
        print("- connect <expert_id> - Connect to an expert")
        print("- list - Show all available experts")
        print("- voice - Toggle voice output on/off")
        print("- back - Return to main menu")
        print("- exit - Exit the program")
        
        while True:
            user_input = input("\nCommand: ").strip()
            
            if user_input.lower() == 'back':
                break
            if user_input.lower() == 'exit':
                return True
            if user_input.lower() == 'list':
                self.list_experts()
                continue
            if user_input.lower() == 'voice':
                status = "enabled" if voice_output.toggle_voice() else "disabled"
                print(f"Voice output {status}")
                continue
            
            if user_input.lower().startswith('connect '):
                expert_id = user_input[8:].strip()
                if self.expert_interface(expert_id):
                    return True
                print("\nIntelligence Experts System")
                self.list_experts()
                print("\nCommands:")
                print("- connect <expert_id> - Connect to an expert")
                print("- list - Show all available experts")
                print("- voice - Toggle voice output on/off")
                print("- back - Return to main menu")
                print("- exit - Exit the program")
            else:
                print("Invalid command. Please try again.")
        
        return False

# Function to be called from mark1.py to start the experts system
def start_experts_system(api_client):
    experts_manager = ExpertsManager(api_client)
    return experts_manager.experts_menu() 