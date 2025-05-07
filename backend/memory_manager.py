from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
import os
import json
from datetime import datetime

# Try to import from the new location first, fall back to old location if needed
try:
    from langchain_community.chat_message_histories import RedisChatMessageHistory
except ImportError:
    try:
        from langchain.memory.chat_message_histories import RedisChatMessageHistory
    except ImportError:
        print("Warning: RedisChatMessageHistory not available. Using in-memory storage only.")
        RedisChatMessageHistory = None

# Import message schema
try:
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    try:
        from langchain.schema import HumanMessage, AIMessage
    except ImportError:
        print("Warning: Message schema not available. Using dictionary representation.")
        
        # Define fallback classes
        class HumanMessage:
            def __init__(self, content):
                self.content = content
                
        class AIMessage:
            def __init__(self, content):
                self.content = content

# Create a singleton instance
memory_manager = None

class LangChainMemoryManager:
    """Memory manager using LangChain for persistent storage and retrieval"""
    
    def __init__(self):
        # Initialize memory lanes
        self.memory_lanes = {
            "health": self._create_memory("health"),
            "work": self._create_memory("work"),
            "journal": self._create_memory("journal")
        }
        
        # Overall memory with window buffer (last 10 messages)
        self.overall_memory = ConversationBufferWindowMemory(k=10)
        
        # Expert memories
        self.expert_memories = {}
    
    def _create_memory(self, lane_id):
        """Create a memory instance for a specific lane"""
        # Use Redis for persistent storage if available
        if RedisChatMessageHistory:
            try:
                return ConversationBufferMemory(
                    chat_memory=RedisChatMessageHistory(
                        session_id=f"tryambakam:{lane_id}",
                        url=os.getenv("REDIS_URL", "redis://localhost:6379")
                    )
                )
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}")
        
        # Fall back to in-memory storage
        print(f"Using in-memory storage for {lane_id} lane")
        return ConversationBufferMemory()
    
    def save_to_memory_lanes(self, human_message, ai_message, lanes):
        """Save a conversation exchange to specified memory lanes"""
        for lane in lanes:
            if lane in self.memory_lanes:
                self.memory_lanes[lane].chat_memory.add_user_message(human_message)
                self.memory_lanes[lane].chat_memory.add_ai_message(ai_message)
        
        # Always save to overall memory
        self.overall_memory.chat_memory.add_user_message(human_message)
        self.overall_memory.chat_memory.add_ai_message(ai_message)
        
        # For backward compatibility, also save to JSON
        self._save_to_json(human_message, ai_message, lanes)
    
    def _save_to_json(self, human_message, ai_message, lanes):
        """Legacy method to save to JSON files for backward compatibility"""
        timestamp = datetime.now().isoformat()
        
        for lane in lanes:
            lane_dir = os.path.join("chat_histories", "overall_intelligence", f"{lane}_memory")
            os.makedirs(lane_dir, exist_ok=True)
            
            file_path = os.path.join(lane_dir, f"{lane}_memory.json")
            
            # Load existing memories
            memories = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memories = json.load(f)
                except:
                    memories = []
            
            # Add new memory
            memories.append({
                "timestamp": timestamp,
                "human": human_message,
                "ai": ai_message
            })
            
            # Save updated memories
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memories, f, ensure_ascii=False, indent=2)
    
    def get_memory_for_lane(self, lane_id):
        """Get memory for a specific lane"""
        if lane_id in self.memory_lanes:
            return self.memory_lanes[lane_id]
        return None
    
    def get_expert_memory(self, expert_id):
        """Get or create memory for an expert"""
        if expert_id not in self.expert_memories:
            self.expert_memories[expert_id] = self._create_memory(f"expert_{expert_id}")
        return self.expert_memories[expert_id]
    
    def get_memory_variables(self, lane_id=None, expert_id=None):
        """Get memory variables for a specific lane or expert"""
        if lane_id:
            memory = self.get_memory_for_lane(lane_id)
        elif expert_id:
            memory = self.get_expert_memory(expert_id)
        else:
            memory = self.overall_memory
            
        if memory:
            return memory.load_memory_variables({})
        return {"history": ""}

# Initialize the singleton instance
memory_manager = LangChainMemoryManager() 