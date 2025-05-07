"""
Memory sharing module for connecting memory lanes with intelligent experts
"""

import streamlit as st

def get_memories_for_expert(expert_type):
    """
    Get relevant memories for a specific expert type
    
    Args:
        expert_type (str): The type of expert (health, work, education, etc.)
        
    Returns:
        list: A list of relevant memories
    """
    # Map expert types to memory lanes
    expert_to_lane = {
        "health": "health_memory",
        "wellness": "health_memory",
        "fitness": "health_memory",
        "nutrition": "health_memory",
        "medical": "health_memory",
        
        "work": "work_memory",
        "career": "work_memory",
        "business": "work_memory",
        "professional": "work_memory",
        
        "education": "work_memory",
        "academic": "work_memory",
        "learning": "work_memory",
        
        "personal": "journal_memory",
        "life": "journal_memory",
        "relationship": "journal_memory",
        "emotional": "journal_memory",
        "family": "journal_memory"
    }
    
    # Determine which memory lane to use
    memory_lane = expert_to_lane.get(expert_type.lower(), None)
    
    if not memory_lane or memory_lane not in st.session_state:
        return []
    
    # Return the memories from the appropriate lane
    return st.session_state[memory_lane]

def get_memory_context_for_expert(expert_type, max_memories=5):
    """
    Get a formatted context string with relevant memories for an expert
    
    Args:
        expert_type (str): The type of expert
        max_memories (int): Maximum number of memories to include
        
    Returns:
        str: A formatted context string with relevant memories
    """
    memories = get_memories_for_expert(expert_type)
    
    if not memories:
        return ""
    
    # Format the memories into a context string
    context = f"\n\nRELEVANT USER MEMORIES ({expert_type.upper()}):\n"
    
    # Get the most recent memories (up to max_memories)
    recent_memories = memories[-max_memories:]
    
    for i, memory in enumerate(recent_memories):
        context += f"\n{i+1}. [{memory['timestamp']}]\n"
        context += f"   User: {memory['user_message']}\n"
        context += f"   Previous response: {memory['ai_response']}\n"
    
    return context 