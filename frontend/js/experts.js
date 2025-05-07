document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const expertInput = document.getElementById('expert-input');
    const sendExpertBtn = document.getElementById('send-expert-btn');
    const expertItems = document.querySelectorAll('.expert-item');
    const expertContent = document.querySelector('.expert-content');
    const expertHeader = document.querySelector('.expert-header h2');
    const expertsArea = document.querySelector('.experts-area');
    const expertsSidebar = document.querySelector('.experts-sidebar');
    
    console.log("Experts.js loaded");
    console.log("Expert input:", expertInput);
    console.log("Send button:", sendExpertBtn);
    
    let activeExpert = null;
    
    // Add experts sidebar toggle button
    const sidebarToggleBtn = document.createElement('button');
    sidebarToggleBtn.classList.add('experts-sidebar-toggle');
    sidebarToggleBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    expertsArea.appendChild(sidebarToggleBtn);
    
    // Check if sidebar was hidden in previous session
    if (localStorage.getItem('expertsSidebarHidden') === 'true') {
        expertsArea.classList.add('sidebar-hidden');
    }
    
    // Add event listener for sidebar toggle
    sidebarToggleBtn.addEventListener('click', function() {
        console.log("Experts toggle button clicked");
        expertsArea.classList.toggle('sidebar-hidden');
        localStorage.setItem('expertsSidebarHidden', expertsArea.classList.contains('sidebar-hidden'));
    });
    
    // Add memory storage for experts
    const ExpertMemory = {
        // Store conversations for each expert
        conversations: JSON.parse(localStorage.getItem('expertConversations') || '{}'),
        
        // Save a message to expert's conversation history
        saveMessage: function(expertName, message, isUser) {
            if (!this.conversations[expertName]) {
                this.conversations[expertName] = [];
            }
            
            this.conversations[expertName].push({
                content: message,
                timestamp: new Date().toISOString(),
                isUser: isUser
            });
            
            // Save to localStorage
            localStorage.setItem('expertConversations', JSON.stringify(this.conversations));
        },
        
        // Get conversation history for an expert
        getConversation: function(expertName) {
            return this.conversations[expertName] || [];
        }
    };
    
    // Add after ExpertMemory definition
    const MemoryLaneAccess = {
        enabled: false,
        
        // Load memory lane data for the current expert
        async loadMemoryLane(expertName) {
            if (!this.enabled) return [];
            
            const memoryType = this.getMemoryType(expertName);
            try {
                const response = await fetch(`/api/memory/${memoryType}`);
                const data = await response.json();
                return data.memories || [];
            } catch (error) {
                console.error('Error loading memory lane:', error);
                return [];
            }
        },
        
        // Get memory type based on expert
        getMemoryType(expertName) {
            switch(expertName) {
                case 'Dr. Tryambakam':
                    return 'health';
                case 'Professor Tryambakam':
                    return 'work';
                case 'Counselor Tryambakam':
                    return 'journal';
                default:
                    return null;
            }
        }
    };
    
    // Function to add a message to the expert chat
    function addMessage(content, isUser = false) {
        // Clear placeholder if it exists
        const placeholder = expertContent.querySelector('.expert-icon');
        if (placeholder) {
            expertContent.innerHTML = '';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        
        // Create message container with proper alignment
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message-container');
        messageContainer.classList.add(isUser ? 'user-container' : 'ai-container');
        
        const iconDiv = document.createElement('div');
        iconDiv.classList.add('message-icon');
        
        const icon = document.createElement('i');
        icon.className = isUser ? 'fas fa-user' : 'fas fa-user-md';
        iconDiv.appendChild(icon);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = content;
        
        // Arrange elements based on user or AI
        if (isUser) {
            messageContainer.appendChild(contentDiv);
            messageContainer.appendChild(iconDiv);
        } else {
            messageContainer.appendChild(iconDiv);
            messageContainer.appendChild(contentDiv);
        }
        
        messageDiv.appendChild(messageContainer);
        expertContent.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        expertContent.scrollTop = expertContent.scrollHeight;
        
        // Save message to expert's memory
        if (activeExpert) {
            ExpertMemory.saveMessage(activeExpert, content, isUser);
        }
    }
    
    // Function to get expert ID from name
    function getExpertId(expertName) {
        const expertMappings = {
            'Dr. Tryambakam': 'doctor',
            'Professor Tryambakam': 'teacher'
        };
        return expertMappings[expertName] || expertName.toLowerCase();
    }
    
    // Add toggle event listener in the DOMContentLoaded
    const memoryToggle = document.getElementById('memory-lane-toggle');
    if (memoryToggle) {
        memoryToggle.addEventListener('change', async function() {
            MemoryLaneAccess.enabled = this.checked;
            
            if (activeExpert) {
                // Load and display memory lane content when toggled on
                if (this.checked) {
                    const memories = await MemoryLaneAccess.loadMemoryLane(activeExpert);
                    memories.forEach(memory => {
                        addMessage(`[Memory Lane] ${memory.content}`, false);
                    });
                }
            }
            
            // Save toggle state
            localStorage.setItem('expertMemoryEnabled', this.checked);
        });
        
        // Restore toggle state
        const savedState = localStorage.getItem('expertMemoryEnabled');
        if (savedState === 'true') {
            memoryToggle.checked = true;
            MemoryLaneAccess.enabled = true;
        }
    }
    
    // Update the sendMessage function
    async function sendMessage() {
        console.log("Send message function called");
        const message = expertInput.value.trim();
        
        if (message && activeExpert) {
            console.log("Sending message:", message);
            
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input
            expertInput.value = '';
            
            // Get expert ID for API call
            const expertId = getExpertId(activeExpert);
            
            // Make API request
            fetch(`/api/experts/${expertId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    include_memory: MemoryLaneAccess.enabled // Pass toggle state
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                addMessage(data.response, false);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage("I apologize, but I encountered an error. Please try again.", false);
            });
        } else if (!activeExpert) {
            addMessage("Please select an expert first.", false);
        }
    }
    
    // Helper function to get expert's system prompt
    function getExpertPrompt(expertName) {
        switch(expertName) {
            case 'Dr. Tryambakam':
                return "You are Dr. Tryambakam, a medical expert with extensive healthcare knowledge. You provide accurate medical information and advice, while being clear about the limitations of AI medical advice. Always maintain a professional and caring tone.";
                
            case 'Professor Tryambakam':
                return "You are Professor Tryambakam, an educational expert across multiple disciplines. You excel at explaining complex concepts in simple terms and helping with learning. Use examples and analogies to make concepts clear.";
                
            default:
                return "You are an expert AI assistant. Please provide accurate and helpful information in your domain of expertise.";
        }
    }
    
    // Event listeners
    if (sendExpertBtn) {
        sendExpertBtn.addEventListener('click', function() {
            console.log("Send button clicked");
            sendMessage();
        });
    }
    
    // Handle Enter key press
    if (expertInput) {
        expertInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                console.log("Enter key pressed");
                e.preventDefault(); // Prevent default to avoid new line
                sendMessage();
            }
        });
    }
    
    // Expert selection
    if (expertItems.length > 0) {
        expertItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                expertItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Update expert header
                const expertName = this.querySelector('h3').textContent;
                if (expertHeader) {
                    expertHeader.textContent = expertName;
                }
                activeExpert = expertName;
                
                // Clear expert content
                if (expertContent) {
                    expertContent.innerHTML = '';
                    
                    // Load previous conversation
                    const conversation = ExpertMemory.getConversation(expertName);
                    
                    if (conversation.length > 0) {
                        // Display previous messages
                        conversation.forEach(msg => {
                            addMessage(msg.content, msg.isUser);
                        });
                    } else {
                        // Add welcome message based on expert
                        if (expertName === 'Dr. Tryambakam') {
                            addMessage("Hello, I'm Dr. Tryambakam. I can provide medical information and health advice. How can I assist you today?");
                        } else if (expertName === 'Professor Tryambakam') {
                            addMessage("Greetings, I'm Professor Tryambakam. I specialize in educational topics across multiple disciplines. What would you like to learn about?");
                        }
                    }
                }
            });
        });
        
        // Set the first expert as active by default if none is active
        if (!document.querySelector('.expert-item.active') && expertItems.length > 0) {
            expertItems[0].click();
        }
    }
}); 