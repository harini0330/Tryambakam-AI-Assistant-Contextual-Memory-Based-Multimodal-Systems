document.addEventListener('DOMContentLoaded', function() {
    // Chat functionality
    const chatList = document.getElementById('chat-list');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendMessageBtn = document.getElementById('send-message-btn');
    const currentChatTitle = document.getElementById('current-chat-title');
    const createChatBtn = document.getElementById('create-chat-btn');
    const newChatTitle = document.getElementById('new-chat-title');
    const newChatModal = document.getElementById('new-chat-modal');
    
    let currentChatId = null;
    
    // Load chat list
    function loadChats() {
        fetch('/api/chats')
            .then(response => response.json())
            .then(chats => {
                chatList.innerHTML = '';
                chats.forEach(chat => {
                    const li = document.createElement('li');
                    li.textContent = chat.title;
                    li.setAttribute('data-id', chat.id);
                    if (chat.id === currentChatId) {
                        li.classList.add('active');
                    }
                    li.addEventListener('click', () => switchChat(chat.id));
                    chatList.appendChild(li);
                });
            })
            .catch(error => console.error('Error loading chats:', error));
    }
    
    // Switch to a different chat
    function switchChat(chatId) {
        currentChatId = chatId;
        
        // Update active chat in list
        const chatItems = document.querySelectorAll('.chat-list li');
        chatItems.forEach(item => {
            if (item.getAttribute('data-id') === chatId) {
                item.classList.add('active');
                currentChatTitle.textContent = item.textContent;
            } else {
                item.classList.remove('active');
            }
        });
        
        // Load chat messages
        loadChatMessages(chatId);
    }
    
    // Load messages for a chat
    function loadChatMessages(chatId) {
        chatMessages.innerHTML = '';
        
        fetch(`/api/chats/${chatId}/messages`)
            .then(response => response.json())
            .then(messages => {
                messages.forEach(msg => {
                    addMessageToChat(msg.human, 'user');
                    addMessageToChat(msg.ai, 'ai');
                });
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => console.error('Error loading messages:', error));
    }
    
    // Add a message to the chat display
    function addMessageToChat(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Send a message
    function sendMessage() {
        if (!currentChatId) {
            alert('Please select or create a chat first');
            return;
        }
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat(message, 'user');
        
        // Clear input
        chatInput.value = '';
        
        // Send to API
        fetch(`/api/chats/${currentChatId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // Add AI response to chat
            addMessageToChat(data.response, 'ai');
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('Error: Could not get response', 'ai');
        });
    }
    
    // Create a new chat
    function createNewChat() {
        const title = newChatTitle.value.trim() || 'New Chat';
        
        fetch('/api/chats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title })
        })
        .then(response => response.json())
        .then(data => {
            // Close modal
            newChatModal.style.display = 'none';
            newChatTitle.value = '';
            
            // Reload chats and switch to new one
            loadChats();
            setTimeout(() => switchChat(data.id), 100);
        })
        .catch(error => console.error('Error creating chat:', error));
    }
    
    // Event listeners
    sendMessageBtn.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    createChatBtn.addEventListener('click', createNewChat);
    
    // Initial load
    loadChats();

    // Optimize chat initialization
    initializeChat();

    // Add a sidebar toggle button
    addSidebarToggle();
});

// Optimize chat initialization
function initializeChat() {
    // Use requestAnimationFrame for UI updates
    requestAnimationFrame(() => {
        // ... existing chat initialization code ...
    });
    
    // Fetch chat history asynchronously
    fetchChatHistory().then(history => {
        displayChatHistory(history);
    }).catch(error => {
        console.error('Failed to load chat history:', error);
    });
}

// Fetch chat history from the server
async function fetchChatHistory() {
    try {
        const response = await fetch(`/api/chats/${currentChatId}/messages`);
        if (!response.ok) {
            throw new Error('Failed to fetch chat history');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return [];
    }
}

// Display chat history in the UI
function displayChatHistory(history) {
    // Clear existing messages
    messagesContainer.innerHTML = '';
    
    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();
    
    history.forEach(msg => {
        if (msg.human) {
            addMessageToFragment(msg.human, 'user', fragment);
        }
        if (msg.ai) {
            addMessageToFragment(msg.ai, 'ai', fragment);
        }
    });
    
    // Add all messages at once
    messagesContainer.appendChild(fragment);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Helper function to add a message to DocumentFragment
function addMessageToFragment(text, sender, fragment) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    
    const iconDiv = document.createElement('div');
    iconDiv.classList.add('message-icon');
    
    const icon = document.createElement('i');
    icon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    iconDiv.appendChild(icon);
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    contentDiv.textContent = text;
    
    messageDiv.appendChild(iconDiv);
    messageDiv.appendChild(contentDiv);
    
    fragment.appendChild(messageDiv);
}

// Add a sidebar toggle button
function addSidebarToggle() {
    // Remove any existing toggle buttons
    const existingToggle = document.querySelector('.chat-sidebar-toggle');
    if (existingToggle) {
        existingToggle.remove();
    }
    
    // Create the toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'chat-sidebar-toggle';
    toggleButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
    toggleButton.setAttribute('title', 'Toggle Sidebar');
    
    // Add event listener to toggle the sidebar
    toggleButton.addEventListener('click', function() {
        const chatArea = document.querySelector('.chat-area');
        chatArea.classList.toggle('sidebar-hidden');
        
        // Update the icon based on sidebar state
        const icon = this.querySelector('i');
        if (chatArea.classList.contains('sidebar-hidden')) {
            icon.className = 'fas fa-chevron-right';
        } else {
            icon.className = 'fas fa-chevron-left';
        }
    });
    
    // Add to the chat sidebar
    const chatSidebar = document.querySelector('.chat-sidebar');
    if (chatSidebar) {
        chatSidebar.appendChild(toggleButton);
    }
}

// Replace the addChatContainerToggle function with this
function addChatContainerToggle() {
    // We're using the sidebar toggle instead
    addSidebarToggle();
} 