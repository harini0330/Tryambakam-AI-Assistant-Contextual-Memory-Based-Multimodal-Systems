from flask import Flask, request, jsonify, send_from_directory
import os
import json
import sys
import base64
from backend.config import client
from backend.vision_processor import generate_response
from flask_cors import CORS
from backend.mark1_update import SimpleOverallIntelligence
from backend.memory_manager import memory_manager
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core functionality
from backend.mark1 import ChatManager, OverallIntelligence, process_file_content, save_to_memory_lanes
from backend.intelligence_experts import ExpertsManager
from backend.voice_interface import voice_output

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize components
chat_manager = ChatManager()
overall_intelligence = SimpleOverallIntelligence()
experts_manager = ExpertsManager(client)

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Chat API endpoints
@app.route('/api/chats', methods=['GET'])
def get_chats():
    chats = []
    for page_id, chat_page in chat_manager.chat_pages.items():
        chats.append({
            'id': page_id,
            'title': chat_page.title
        })
    return jsonify(chats)

@app.route('/api/chats', methods=['POST'])
def create_chat():
    data = request.json
    title = data.get('title', 'New Chat')
    page_id = chat_manager.create_chat_page(title)
    return jsonify({'id': page_id, 'title': title})

@app.route('/api/chats/<page_id>/messages', methods=['GET'])
def get_chat_messages(page_id):
    chat_page = chat_manager.get_chat_page(page_id)
    if not chat_page:
        return jsonify({'error': 'Chat not found'}), 404
    
    messages = []
    if os.path.exists(chat_page.file_path):
        with open(chat_page.file_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            for entry in history:
                messages.append({
                    'timestamp': entry.get('timestamp'),
                    'human': entry.get('human'),
                    'ai': entry.get('ai')
                })
    
    return jsonify(messages)

@app.route('/api/chats/<page_id>/messages', methods=['POST'])
def send_message(page_id):
    chat_page = chat_manager.get_chat_page(page_id)
    if not chat_page:
        return jsonify({'error': 'Chat not found'}), 404
    
    data = request.json
    user_input = data.get('message', '')
    
    # Process the message
    messages = [{"role": "system", "content": "You are Tryambakam, an AI assistant. When providing code examples, always wrap them in triple backticks with the language identifier, like ```python for Python code."}]
    
    # Get the conversation history from memory
    if os.path.exists(chat_page.file_path):
        with open(chat_page.file_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
            for entry in history[-10:]:  # Use last 10 messages for context
                if 'human' in entry and entry['human']:
                    messages.append({"role": "user", "content": entry['human']})
                if 'ai' in entry and entry['ai']:
                    messages.append({"role": "assistant", "content": entry['ai']})
    
    # Add the current user message
    messages.append({"role": "user", "content": user_input})
    
    try:
        # Get response from the AI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        # Save the conversation to the chat page
        chat_page.add_message(user_input, ai_response)
        
        return jsonify({
            'response': ai_response
        })
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

# File upload endpoint
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file temporarily
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    file.save(temp_path)
    
    # Process the file
    chat_id = request.form.get('chat_id')
    if chat_id:
        chat_page = chat_manager.get_chat_page(chat_id)
        if chat_page:
            chat_page.process_file(temp_path)
    
    return jsonify({'success': True, 'message': 'File processed successfully'})

# Vision API endpoint
@app.route('/api/vision/analyze', methods=['POST'])
def analyze_vision():
    data = request.json
    image_base64 = data.get('image', '')
    prompt = data.get('prompt', 'Describe this image in detail')
    
    if not image_base64:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Use the simplified function from shortvisionworking
        response_text = generate_response(prompt, image_base64)
        
        # Check if the response contains an error
        if response_text.startswith("Error:"):
            return jsonify({'error': response_text[7:]}), 500
            
        return jsonify({
            'response': response_text
        })
    except Exception as e:
        print(f"Error in vision analysis: {e}")
        return jsonify({'error': str(e)}), 500

# Experts API endpoints
@app.route('/api/experts', methods=['GET'])
def get_experts():
    experts = []
    for expert_id, expert_info in experts_manager.EXPERTS.items():
        experts.append({
            'id': expert_id,
            'name': expert_info['name'],
            'description': expert_info['prompt'][:100] + '...'
        })
    return jsonify(experts)

@app.route('/api/experts/<expert_id>/chat', methods=['POST'])
def chat_with_expert(expert_id):
    try:
        data = request.json
        message = data.get('message', '')
        include_memory = data.get('include_memory', False)
        
        expert = experts_manager.get_expert(expert_id)
        if not expert:
            return jsonify({'error': 'Expert not found'}), 404
        
        response = expert.get_response(message, include_memory)
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error in expert chat: {e}")
        return jsonify({'error': str(e)}), 500

# Voice toggle endpoint
@app.route('/api/voice/toggle', methods=['POST'])
def toggle_voice():
    data = request.json
    enabled = data.get('enabled', None)
    result = voice_output.toggle(enabled)
    return jsonify({'enabled': result})

@app.route('/pages/<page_name>')
def serve_page(page_name):
    return app.send_static_file(f'pages/{page_name}')

# Memory lanes API endpoints
@app.route('/api/memory/<lane_id>/chat', methods=['POST'])
def memory_lane_chat(lane_id):
    data = request.json
    message = data.get('message', '')
    
    # Get the memory lane
    memory_lane = overall_intelligence.get_memory_lane(lane_id)
    if not memory_lane:
        return jsonify({'error': 'Memory lane not found'}), 404
    
    # Get response from the memory lane
    response = memory_lane.get_response(message)
    return jsonify({'response': response})

# Overall Intelligence API endpoint
@app.route('/api/overall/chat', methods=['POST'])
def overall_chat():
    data = request.json
    message = data.get('message', '')
    
    # Process the message with the AI
    response, memory_lanes = process_overall_message(message)
    
    return jsonify({
        'response': response,
        'memory_lanes': memory_lanes
    })

def process_overall_message(message):
    """Process a message in the overall intelligence and return the response"""
    try:
        # Get response from the AI
        response_data = overall_intelligence.process_message(message)
        
        # Check if response is a tuple (response, memory_lanes)
        if isinstance(response_data, tuple) and len(response_data) == 2:
            response, memory_lanes = response_data
            return response, memory_lanes
        else:
            return response_data, ["journal"]
    except Exception as e:
        print(f"Error processing overall message: {e}")
        return "I apologize, but I encountered an error.", ["journal"]

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'status': 'ok', 'message': 'API is working'})

# Add a new endpoint to delete a chat page
@app.route('/api/chats/<page_id>', methods=['DELETE'])
def delete_chat(page_id):
    success = chat_manager.delete_chat_page(page_id)
    if success:
        return jsonify({'success': True, 'message': 'Chat deleted successfully'})
    else:
        return jsonify({'error': 'Chat not found'}), 404

# Add this endpoint to fetch memories
@app.route('/api/memory/<lane_id>', methods=['GET'])
def get_memories(lane_id):
    try:
        if lane_id == 'all':
            # Fetch from all lanes
            memories = []
            for lane in ['health', 'work', 'journal']:
                lane_memory = memory_manager.get_memory_for_lane(lane)
                if lane_memory:
                    # Convert LangChain memory to our format
                    memory_messages = lane_memory.chat_memory.messages
                    lane_memories = []
                    
                    # Process messages in pairs (human, AI)
                    for i in range(0, len(memory_messages), 2):
                        if i+1 < len(memory_messages):
                            human_msg = memory_messages[i]
                            ai_msg = memory_messages[i+1]
                            
                            if isinstance(human_msg, HumanMessage) and isinstance(ai_msg, AIMessage):
                                lane_memories.append({
                                    "timestamp": datetime.now().isoformat(),  # LangChain doesn't store timestamps
                                    "human": human_msg.content,
                                    "ai": ai_msg.content,
                                    "lane": lane
                                })
                    
                    memories.extend(lane_memories)
            return jsonify(memories)
        else:
            # Fetch from specific lane
            lane_memory = memory_manager.get_memory_for_lane(lane_id)
            if lane_memory:
                # Convert LangChain memory to our format
                memory_messages = lane_memory.chat_memory.messages
                memories = []
                
                # Process messages in pairs (human, AI)
                for i in range(0, len(memory_messages), 2):
                    if i+1 < len(memory_messages):
                        human_msg = memory_messages[i]
                        ai_msg = memory_messages[i+1]
                        
                        if isinstance(human_msg, HumanMessage) and isinstance(ai_msg, AIMessage):
                            memories.append({
                                "timestamp": datetime.now().isoformat(),
                                "human": human_msg.content,
                                "ai": ai_msg.content
                            })
                
                return jsonify(memories)
            return jsonify([])
    except Exception as e:
        print(f"Error fetching memories: {e}")
        return jsonify([])

# Add this endpoint to delete a memory
@app.route('/api/memory/<lane_id>/<timestamp>', methods=['DELETE'])
def delete_memory(lane_id, timestamp):
    try:
        # Validate lane_id
        if lane_id not in ['health', 'work', 'journal', 'all']:
            return jsonify({'error': 'Invalid memory lane'}), 400
            
        # Handle 'all' lane specially
        if lane_id == 'all':
            # Delete from all lanes
            for lane in ['health', 'work', 'journal']:
                delete_from_lane(lane, timestamp)
            return jsonify({'success': True, 'message': 'Memory deleted from all lanes'})
        
        # Delete from specific lane
        success = delete_from_lane(lane_id, timestamp)
        if success:
            return jsonify({'success': True, 'message': f'Memory deleted from {lane_id} lane'})
        else:
            return jsonify({'error': 'Memory not found'}), 404
            
    except Exception as e:
        print(f"Error deleting memory: {e}")
        return jsonify({'error': str(e)}), 500

def delete_from_lane(lane_id, timestamp):
    """Delete a memory from a specific lane"""
    lane_path = os.path.join("chat_histories", "overall_intelligence", f"{lane_id}_memory", f"{lane_id}_memory.json")
    
    if not os.path.exists(lane_path):
        return False
        
    # Load memories
    with open(lane_path, 'r', encoding='utf-8') as f:
        memories = json.load(f)
    
    # Find and remove the memory
    original_length = len(memories)
    memories = [m for m in memories if m.get('timestamp') != timestamp]
    
    # If no memory was removed, return False
    if len(memories) == original_length:
        return False
    
    # Save updated memories
    with open(lane_path, 'w', encoding='utf-8') as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)
    
    return True

if __name__ == '__main__':
    app.run(debug=True, port=5000) 