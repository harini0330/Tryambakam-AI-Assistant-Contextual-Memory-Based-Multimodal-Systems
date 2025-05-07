import openai
import json
import os
from datetime import datetime
import base64
import cv2
from dotenv import load_dotenv

# Create a simplified version of the OverallIntelligence class
class SimpleOverallIntelligence:
    def __init__(self):
        self.history = []
        self.history_file = os.path.join("chat_histories", "overall_intelligence", "overall_history.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        # Load history if it exists
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def process_message(self, message):
        """Process a message and return a response with memory lane categorization"""
        from backend.config import client
        
        try:
            # Simple system prompt
            system_prompt = "You are Tryambakam's overall intelligence. Respond helpfully to the user's message."
            
            # Get response from OpenAI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500
            )
            
            response = completion.choices[0].message.content
            
            # Step 1: Try keyword-based categorization first
            memory_lanes = self.categorize_by_keywords(message, response)
            
            # Step 2: If no keywords matched, use LLM to categorize
            if not memory_lanes:
                memory_lanes = self.categorize_by_llm(message, response, client)
            
            # Create entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "human": message,
                "ai": response,
                "memory_lanes": memory_lanes
            }
            
            # Save to overall history
            self.history.append(entry)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            
            # Save to each memory lane
            for lane in memory_lanes:
                memory_lane = self.get_memory_lane(lane)
                memory_lane.add_entry({
                    "timestamp": entry["timestamp"],
                    "human": entry["human"],
                    "ai": entry["ai"]
                })
            
            return response, memory_lanes
            
        except Exception as e:
            print(f"Error in SimpleOverallIntelligence: {e}")
            return "I apologize, but I encountered an error. Please try again later.", ["journal"]

    def categorize_by_keywords(self, message, response):
        """Categorize message and response by keywords"""
        memory_lanes = []
        
        # Expanded health keywords
        health_keywords = [
            "health", "medical", "doctor", "sick", "illness", "disease", "medicine", 
            "hospital", "pain", "symptom", "treatment", "cold", "flu", "fever", "cough", 
            "headache", "allergy", "diet", "exercise", "wellness", "therapy", "mental health",
            "physical", "body", "medication", "prescription", "pharmacy", "nurse", "clinic",
            "appointment", "checkup", "diagnosis", "recovery", "healing", "injury", "wound",
            "surgery", "operation", "specialist", "patient", "emergency", "ambulance", "virus",
            "infection", "bacteria", "immune", "vaccination", "vaccine", "booster", "tired",
            "fatigue", "exhaustion", "sleep", "rest", "hydration", "nutrition", "vitamin"
        ]
        
        # Expanded work keywords
        work_keywords = [
            "work", "job", "career", "office", "business", "project", "task", "meeting", 
            "deadline", "colleague", "coworker", "boss", "manager", "employee", "client", 
            "customer", "presentation", "report", "email", "call", "conference", "interview",
            "application", "resume", "CV", "promotion", "salary", "wage", "income", "profit",
            "revenue", "startup", "entrepreneur", "company", "corporation", "industry", "market",
            "product", "service", "team", "collaboration", "strategy", "goal", "objective",
            "performance", "evaluation", "feedback", "training", "development", "skill", "expertise"
        ]
        
        # Check both the user message and AI response for keywords
        combined_text = (message + " " + response).lower()
        
        # Check for health keywords
        if any(keyword in combined_text for keyword in health_keywords):
            memory_lanes.append("health")
        
        # Check for work keywords
        if any(keyword in combined_text for keyword in work_keywords):
            memory_lanes.append("work")
        
        return memory_lanes

    def categorize_by_llm(self, message, response, client):
        """Use LLM to categorize the message and response"""
        try:
            # Create a prompt specifically for categorization
            categorization_prompt = f"""
            Analyze the following conversation and determine which memory lane it belongs to.
            Choose from: health, work, or journal.
            
            - health: For topics related to physical or mental health, medical issues, wellness, etc.
            - work: For topics related to jobs, career, business, professional development, etc.
            - journal: For personal reflections, daily activities, or topics that don't fit the other categories.
            
            User message: {message}
            AI response: {response}
            
            Respond with ONLY ONE of these words: health, work, journal
            """
            
            # Get categorization from LLM
            categorization = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a categorization assistant that classifies conversations into memory lanes."},
                    {"role": "user", "content": categorization_prompt}
                ],
                max_tokens=10  # Keep it short, we just need one word
            )
            
            category = categorization.choices[0].message.content.strip().lower()
            
            # Validate the category
            valid_categories = ["health", "work", "journal"]
            if category in valid_categories:
                return [category]
            else:
                # Default to journal if the LLM gives an invalid response
                print(f"LLM returned invalid category: {category}. Defaulting to journal.")
                return ["journal"]
                
        except Exception as e:
            print(f"Error in LLM categorization: {e}")
            return ["journal"]  # Default to journal on error

    def get_memory_lane(self, lane_id):
        """Get a memory lane by ID"""
        return MemoryLane(lane_id)

# Add this at the end of the file
class MemoryLane:
    def __init__(self, lane_id):
        self.lane_id = lane_id
        self.file_path = os.path.join("chat_histories", "overall_intelligence", f"{lane_id}_memory", f"{lane_id}_memory.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Load history if it exists
        self.history = []
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def add_entry(self, entry):
        """Add an entry to the memory lane"""
        self.history.append(entry)
        
        # Save to file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_response(self, message):
        """Get a response based on the memory lane's history"""
        from backend.config import client
        
        try:
            # Create a prompt that includes relevant history
            system_prompt = f"You are Tryambakam's {self.lane_id} memory specialist. Respond based on the user's {self.lane_id}-related history."
            
            # Get response from OpenAI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in memory lane response: {e}")
            return "I apologize, but I encountered an error accessing this memory lane." 