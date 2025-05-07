import json
import os
from datetime import datetime
from openai import OpenAI

# Directory structure
BASE_DIR = "chat_histories"
OVERALL_DIR = os.path.join(BASE_DIR, "overall_intelligence")
EXPERTS_DIR = os.path.join(BASE_DIR, "experts")

# Create experts directory
if not os.path.exists(EXPERTS_DIR):
    os.makedirs(EXPERTS_DIR)

# Expert definitions
EXPERTS = {
    "doctor": {
        "name": "Dr. Tryambakam",
        "prompt": "You are Dr. Tryambakam, a medical expert with extensive healthcare knowledge. You provide accurate medical information and advice, while being clear about the limitations of AI medical advice.",
        "memory_lane": "health"
    },
    "teacher": {
        "name": "Professor Tryambakam",
        "prompt": "You are Professor Tryambakam, an educational expert across multiple disciplines. You excel at explaining complex concepts in simple terms and helping with learning.",
        "memory_lane": "work"
    },
    "therapist": {
        "name": "Counselor Tryambakam",
        "prompt": "You are Counselor Tryambakam, a compassionate therapist who provides guidance and emotional support. You help people understand their feelings and develop coping strategies.",
        "memory_lane": "journal"
    }
}

class Expert:
    def __init__(self, expert_id, client):
        self.expert_id = expert_id
        self.info = EXPERTS[expert_id]
        self.name = self.info["name"]
        self.prompt = self.info["prompt"]
        self.memory_lane = self.info["memory_lane"]
        self.file_path = os.path.join(EXPERTS_DIR, f"{expert_id}_conversations.json")
        
        # Initialize OpenAI client with correct endpoint and key
        self.api_key = "glhf_4bcabf37973c831859edc8b224c682f4"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://glhf.chat/api/openai/v1"
        )
        self.load_history()
        
    def load_history(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                try:
                    self.history = json.load(f)
                except json.JSONDecodeError:
                    self.history = []
        else:
            self.history = []
            
    def save_history(self, user_input, ai_response):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "human": user_input,
            "ai": ai_response
        })
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
            
    def get_response(self, user_input, include_memory=False):
        # Prepare messages for the API
        messages = [{"role": "system", "content": self.prompt}]
        
        # Add memory lane context if enabled
        if include_memory:
            memory_data = self.load_memory_lane()
            if memory_data:
                memory_context = "\n".join(memory_data)
                messages.append({"role": "system", "content": f"Memory Lane Context:\n{memory_context}"})
        
        # Add conversation history (last 5 exchanges)
        recent_history = self.history[-10:] if len(self.history) > 10 else self.history
        for entry in recent_history:
            if "human" in entry and "ai" in entry:
                messages.append({"role": "user", "content": entry["human"]})
                messages.append({"role": "assistant", "content": entry["ai"]})
        
        # Add the current user input
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from API using the correct model prefix
            completion = self.client.chat.completions.create(
                model="hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                messages=messages,
                max_tokens=1000,
                stream=False
            )
            
            response = completion.choices[0].message.content
            
            # Save to history
            self.save_history(user_input, response)
            
            return response
        except Exception as e:
            print(f"Error in expert response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def load_memory_lane(self):
        # Load memory lane data based on expert's memory type
        memory_type = self.memory_lane
        file_path = os.path.join(OVERALL_DIR, f"{memory_type}_memory.json")
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return [entry["content"] for entry in data]
        except FileNotFoundError:
            return []

class ExpertsManager:
    def __init__(self, client):
        self.EXPERTS = EXPERTS
        self.client = client
        self.active_experts = {}
        
    def get_expert(self, expert_id):
        if expert_id not in self.EXPERTS:
            return None
            
        if expert_id not in self.active_experts:
            self.active_experts[expert_id] = Expert(expert_id, self.client)
            
        return self.active_experts[expert_id]
        
    def list_experts(self):
        return [{"id": expert_id, "name": info["name"], "description": info["prompt"]} 
                for expert_id, info in self.EXPERTS.items()] 