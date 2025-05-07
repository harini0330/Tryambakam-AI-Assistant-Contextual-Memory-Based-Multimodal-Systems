document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const overallInput = document.getElementById('overall-input');
    const sendOverallBtn = document.getElementById('send-overall-btn');
    const messagesContainer = document.getElementById('overall-messages');
    const memoryLanes = document.querySelectorAll('.memory-lane');
    
    console.log("Overall.js loaded");
    console.log("Overall input:", overallInput);
    console.log("Send button:", sendOverallBtn);
    
    // API endpoint for Overall Intelligence
    const API_ENDPOINT = 'https://glhf.chat/api/openai/v1/chat/completions';
    const API_KEY = 'glhf_4bcabf37973c831859edc8b224c682f4';
    
    // Current active memory lane
    let activeMemoryLane = 'all'; // Default to all lanes
    
    // Chat history for context
    let chatHistory = [];
    
    // Add a welcome message
    addMessage("Welcome to Tryambakam's Overall Intelligence. How can I help you today?", false);
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false, memoryLanes = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        
        const iconDiv = document.createElement('div');
        iconDiv.classList.add('message-icon');
        
        const icon = document.createElement('i');
        icon.className = isUser ? 'fas fa-user' : 'fas fa-brain';
        iconDiv.appendChild(icon);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Add main content
        contentDiv.textContent = content;
        
        // If AI message has memory lane tags, add them
        if (!isUser && memoryLanes && memoryLanes.length > 0) {
            const memoryTagsDiv = document.createElement('div');
            memoryTagsDiv.classList.add('memory-tags');
            
            memoryLanes.forEach(lane => {
                const tag = document.createElement('span');
                tag.classList.add('memory-tag');
                tag.classList.add(`memory-${lane.toLowerCase()}`);
                tag.textContent = lane;
                memoryTagsDiv.appendChild(tag);
            });
            
            contentDiv.appendChild(document.createElement('br'));
            contentDiv.appendChild(memoryTagsDiv);
        }
        
        messageDiv.appendChild(iconDiv);
        messageDiv.appendChild(contentDiv);
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save to chat history
        chatHistory.push({
            role: isUser ? "user" : "assistant",
            content: content,
            memoryLanes: memoryLanes
        });
        
        // Save chat history to localStorage
        localStorage.setItem('overallChatHistory', JSON.stringify(chatHistory));
        
        return messageDiv;
    }
    
    // Function to send a message
    function sendMessage() {
        const message = overallInput.value.trim();
        if (!message) return;
        
        // Clear input
        overallInput.value = '';
        
        // Add user message
        addMessage(message, true);
        
        // Add loading message
        const loadingMessage = addMessage("Thinking...", false);
        
        // Send to API with a timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        fetch('/api/overall/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message }),
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            return response.json();
        })
        .then(data => {
            // Remove loading message
            loadingMessage.remove();
            
            // Add AI response
            addMessage(data.response, false, data.memory_lanes);
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Remove loading message
            loadingMessage.remove();
            
            // Add error message
            if (error.name === 'AbortError') {
                addMessage("Request timed out. Please try again.", false);
            } else {
                addMessage("I apologize, but I encountered an error. Please try again.", false);
            }
        });
    }
    
    // Function to update memory lane indicators
    function updateMemoryLaneIndicators(lanes) {
        const indicators = document.querySelectorAll('.memory-indicator');
        
        // Reset all indicators
        indicators.forEach(indicator => {
            indicator.classList.remove('active');
        });
        
        // Activate indicators for the current memory lanes
        lanes.forEach(lane => {
            const indicator = document.querySelector(`.memory-indicator[data-lane="${lane.toLowerCase()}"]`);
            if (indicator) {
                indicator.classList.add('active');
            }
        });
    }
    
    // Load chat history from localStorage
    function loadChatHistory() {
        const savedHistory = localStorage.getItem('overallChatHistory');
        if (savedHistory) {
            chatHistory = JSON.parse(savedHistory);
            
            // Clear messages container
            messagesContainer.innerHTML = '';
            
            // Add messages from history
            chatHistory.forEach(msg => {
                addMessage(msg.content, msg.role === 'user', msg.memoryLanes || []);
            });
        } else {
            // Add welcome message if no history
            addMessage("Welcome to Tryambakam's Overall Intelligence. I'll help categorize and store your information in the appropriate memory lanes: Health, Work, and Journal. How can I assist you today?", false, ['Health', 'Work', 'Journal']);
        }
    }
    
    // Event listeners
    if (sendOverallBtn) {
        sendOverallBtn.addEventListener('click', sendMessage);
    }
    
    if (overallInput) {
        overallInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Memory lane filter functionality
    memoryLanes.forEach(lane => {
        lane.addEventListener('click', function() {
            const laneName = this.getAttribute('data-lane');
            
            // Toggle active state
            if (this.classList.contains('active')) {
                this.classList.remove('active');
                activeMemoryLane = 'all';
            } else {
                memoryLanes.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                activeMemoryLane = laneName;
            }
            
            // Filter messages based on selected lane
            const messages = document.querySelectorAll('.message');
            messages.forEach(msg => {
                if (activeMemoryLane === 'all') {
                    msg.style.display = 'flex';
                } else {
                    const tags = msg.querySelectorAll('.memory-tag');
                    const hasTag = Array.from(tags).some(tag => 
                        tag.textContent.toLowerCase() === activeMemoryLane
                    );
                    
                    msg.style.display = hasTag ? 'flex' : 'none';
                }
            });
        });
    });
    
    // Load chat history on page load
    loadChatHistory();
});

// Add CSS for loading indicator
document.head.insertAdjacentHTML('beforeend', `
<style>
.loading-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    margin: 10px 0;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    align-self: center;
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
`); 