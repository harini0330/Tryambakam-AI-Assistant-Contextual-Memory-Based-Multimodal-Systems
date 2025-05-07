document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const newChatBtn = document.getElementById('new-chat-btn');
    const modal = document.getElementById('new-chat-modal');
    const closeBtn = document.querySelector('.close-btn');
    const cancelBtn = document.querySelector('.cancel-btn');
    const chatForm = document.getElementById('new-chat-form');
    const chatItems = document.querySelectorAll('.chat-item');
    const chatArea = document.querySelector('.chat-area');
    
    console.log("General.js loaded");
    console.log("Chat input:", chatInput);
    console.log("Send button:", sendBtn);
    
    // Update the API endpoint to connect to Llama 3.1 405B via OpenAI-compatible API
    const API_ENDPOINT = 'https://glhf.chat/api/openai/v1/chat/completions';
    const API_KEY = 'glhf_4bcabf37973c831859edc8b224c682f4';
    
    // Current chat ID
    let currentChatId = 'general-chat';
    
    // Set to false to use the actual API
    const USE_SIMULATED_RESPONSES = false;
    
    // Chat history for context
    let chatHistory = [];
    
    // Memory for each chat (to remember things like names)
    let chatMemories = JSON.parse(localStorage.getItem('chatMemories') || '{}');
    
    // Add chat sidebar toggle button - append it to the chat-area instead of chat-main
    const sidebarToggleBtn = document.createElement('button');
    sidebarToggleBtn.classList.add('chat-sidebar-toggle');
    sidebarToggleBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    chatArea.appendChild(sidebarToggleBtn);
    
    // Check if sidebar was hidden in previous session
    if (localStorage.getItem('chatSidebarHidden') === 'true') {
        chatArea.classList.add('sidebar-hidden');
    }
    
    // Add event listener for sidebar toggle
    sidebarToggleBtn.addEventListener('click', function() {
        console.log("Toggle button clicked");
        chatArea.classList.toggle('sidebar-hidden');
        localStorage.setItem('chatSidebarHidden', chatArea.classList.contains('sidebar-hidden'));
    });
    
    // Add chat pages toggle button
    const chatPagesToggleBtn = document.createElement('div');
    chatPagesToggleBtn.classList.add('chat-pages-toggle');
    chatPagesToggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i> <span>Collapse Chat Pages</span>';
    document.querySelector('.chat-sidebar').appendChild(chatPagesToggleBtn);
    
    // Check if chat pages were collapsed in previous session
    if (localStorage.getItem('chatPagesCollapsed') === 'true') {
        document.querySelector('.chat-sidebar').classList.add('pages-collapsed');
        chatPagesToggleBtn.classList.add('collapsed');
        chatPagesToggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i> <span>Expand Chat Pages</span>';
    }
    
    // Add event listener for chat pages toggle
    chatPagesToggleBtn.addEventListener('click', function() {
        const chatSidebar = document.querySelector('.chat-sidebar');
        chatSidebar.classList.toggle('pages-collapsed');
        this.classList.toggle('collapsed');
        
        if (chatSidebar.classList.contains('pages-collapsed')) {
            this.innerHTML = '<i class="fas fa-chevron-down"></i> <span>Expand Chat Pages</span>';
            localStorage.setItem('chatPagesCollapsed', 'true');
        } else {
            this.innerHTML = '<i class="fas fa-chevron-up"></i> <span>Collapse Chat Pages</span>';
            localStorage.setItem('chatPagesCollapsed', 'false');
        }
    });
    
    // Add chat page toggle button at the right edge
    const chatPageToggleBtn = document.createElement('button');
    chatPageToggleBtn.classList.add('chat-page-toggle');
    chatPageToggleBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    document.querySelector('.chat-sidebar').appendChild(chatPageToggleBtn);
    
    // Add event listener for chat page toggle
    chatPageToggleBtn.addEventListener('click', function() {
        const chatSidebar = document.querySelector('.chat-sidebar');
        chatSidebar.classList.toggle('collapsed');
        
        if (chatSidebar.classList.contains('collapsed')) {
            this.innerHTML = '<i class="fas fa-chevron-left"></i>';
        } else {
            this.innerHTML = '<i class="fas fa-chevron-right"></i>';
        }
    });
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        
        const iconDiv = document.createElement('div');
        iconDiv.classList.add('message-icon');
        
        const icon = document.createElement('i');
        icon.className = isUser ? 'fas fa-user' : 'fas fa-robot';
        iconDiv.appendChild(icon);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Format AI responses with code blocks
        if (!isUser) {
            // Check if content contains code (looks for triple backticks)
            if (content.includes('```')) {
                // Format code blocks with copy buttons
                contentDiv.innerHTML = formatCodeBlocks(content);
                
                // Add event listeners to copy buttons
                setTimeout(() => {
                    const copyButtons = contentDiv.querySelectorAll('.copy-code-btn');
                    copyButtons.forEach(button => {
                        button.addEventListener('click', function() {
                            const codeBlock = this.parentNode.nextElementSibling;
                            const codeText = codeBlock.textContent;
                            copyToClipboard(codeText);
                            
                            // Change button text temporarily
                            const originalText = this.textContent;
                            this.textContent = 'Copied!';
                            setTimeout(() => {
                                this.textContent = originalText;
                            }, 2000);
                        });
                    });
                }, 0);
            } else {
                contentDiv.textContent = content;
            }
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(iconDiv);
        messageDiv.appendChild(contentDiv);
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save chat history to localStorage
        saveChatHistory(currentChatId, messagesContainer.innerHTML);
        
        // Add to context history
        chatHistory.push({
            role: isUser ? "user" : "assistant",
            content: content
        });
        
        // Extract and save memory information (like names)
        if (!isUser) {
            updateChatMemory(content);
        }
        
        return messageDiv;
    }
    
    // Function to format code blocks with copy buttons
    function formatCodeBlocks(content) {
        console.log("Formatting code blocks for:", content);
        
        // Check if there are any code blocks
        if (!content.includes('```')) {
            return content;
        }
        
        // Split by code blocks with improved regex
        const codeBlockRegex = /```([\w]*)\n([\s\S]*?)```/g;
        let formattedContent = content;
        let match;
        
        while ((match = codeBlockRegex.exec(content)) !== null) {
            const fullMatch = match[0];
            const language = match[1] || 'code';
            const code = match[2].trim();
            
            const replacement = `<div class="code-block-container">
                                  <div class="code-block-header">
                                      <span class="code-language">${language}</span>
                                      <button class="copy-code-btn">Copy code</button>
                                  </div>
                                  <pre class="code-block"><code class="${language}">${escapeHtml(code)}</code></pre>
                                </div>`;
            
            formattedContent = formattedContent.replace(fullMatch, replacement);
        }
        
        return formattedContent;
    }
    
    // Helper function to escape HTML
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // Function to copy text to clipboard
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
    
    // Function to update chat memory with important information
    function updateChatMemory(aiResponse) {
        // Initialize memory for current chat if it doesn't exist
        if (!chatMemories[currentChatId]) {
            chatMemories[currentChatId] = {
                userName: null,
                preferences: [],
                topics: []
            };
        }
        
        // Check for name mentions in the conversation
        const nameRegex = /my name is (\w+\s?\w*)/i;
        const nameMatch = chatHistory.find(msg => msg.role === 'user' && nameRegex.test(msg.content));
        
        if (nameMatch) {
            const match = nameRegex.exec(nameMatch.content);
            if (match && match[1]) {
                chatMemories[currentChatId].userName = match[1].trim();
                console.log(`Remembered name: ${chatMemories[currentChatId].userName}`);
            }
        }
        
        // Save updated memories
        localStorage.setItem('chatMemories', JSON.stringify(chatMemories));
    }
    
    // Function to save chat history
    function saveChatHistory(chatId, content) {
        const savedHistory = JSON.parse(localStorage.getItem('chatHistory') || '{}');
        savedHistory[chatId] = content;
        localStorage.setItem('chatHistory', JSON.stringify(savedHistory));
    }
    
    // Function to load chat history
    function loadChatHistory(chatId) {
        const savedHistory = JSON.parse(localStorage.getItem('chatHistory') || '{}');
        if (savedHistory[chatId]) {
            messagesContainer.innerHTML = savedHistory[chatId];
            
            // Rebuild the chatHistory array for context
            chatHistory = [];
            const messages = messagesContainer.querySelectorAll('.message');
            messages.forEach(msg => {
                const isUser = msg.classList.contains('user-message');
                const content = msg.querySelector('.message-content').textContent;
                chatHistory.push({
                    role: isUser ? "user" : "assistant",
                    content: content
                });
            });
        } else {
            // Add default welcome message for new chats
            messagesContainer.innerHTML = '';
            chatHistory = [];
            
            // Personalized welcome if we know the user's name
            if (chatMemories[chatId] && chatMemories[chatId].userName) {
                addMessage(`Hello ${chatMemories[chatId].userName}! Welcome back to Tryambakam. How can I help you today?`);
            } else {
                addMessage("Hello! I'm Tryambakam's general intelligence. How can I help you today?");
            }
        }
    }
    
    // Function to handle sending a message
    function sendMessage() {
        console.log("Send message function called");
        const message = chatInput.value.trim();
        
        if (message) {
            console.log("Sending message:", message);
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input
            chatInput.value = '';
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('typing-indicator');
            typingIndicator.innerHTML = '<span></span><span></span><span></span>';
            messagesContainer.appendChild(typingIndicator);
            
            if (USE_SIMULATED_RESPONSES) {
                // Simulate API response for testing UI
                setTimeout(() => {
                    // Remove typing indicator
                    const indicator = document.querySelector('.typing-indicator');
                    if (indicator) indicator.remove();
                    
                    const responses = [
                        `I understand your question about "${message}". Let me think about that...`,
                        `That's an interesting point about "${message}". Here's what I know...`,
                        `Regarding "${message}", I can provide the following information...`,
                        `I've analyzed your query about "${message}" and here's my response...`
                    ];
                    
                    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                    addMessage(randomResponse);
                }, 1500);
                return;
            }
            
            // Prepare messages for the API
            const messages = [
                {
                    role: "system",
                    content: createSystemPrompt()
                }
            ];
            
            // Add chat history for context (limit to last 10 messages)
            const recentHistory = chatHistory.slice(-10);
            messages.push(...recentHistory);
            
            // Try to connect to Llama 3.1 API via OpenAI-compatible endpoint
            fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEY}`
                },
                body: JSON.stringify({
                    model: "hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 800
                }),
            })
            .then(response => {
                console.log("API Response status:", response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        console.error("API Error Response:", text);
                        throw new Error(`API request failed with status ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                // Remove typing indicator
                const indicator = document.querySelector('.typing-indicator');
                if (indicator) indicator.remove();
                
                // Add AI response from API
                console.log("API Success Response:", data);
                
                // Extract the response content from the OpenAI-compatible format
                const responseContent = data.choices[0].message.content;
                addMessage(responseContent);
            })
            .catch(error => {
                console.error('Error connecting to API:', error);
                
                // Remove typing indicator
                const indicator = document.querySelector('.typing-indicator');
                if (indicator) indicator.remove();
                
                // Fallback to simulated response
                setTimeout(() => {
                    addMessage(`I'm having trouble connecting to the Llama 3.1 405B model right now. Error: ${error.message}`);
                }, 1000);
            });
        }
    }
    
    // Function to create a system prompt with memory information
    function createSystemPrompt() {
        let systemPrompt = "You are Tryambakam, an advanced AI assistant. Be helpful, concise, and friendly.";
        
        // Add memory information if available
        if (chatMemories[currentChatId]) {
            const memory = chatMemories[currentChatId];
            
            if (memory.userName) {
                systemPrompt += ` The user's name is ${memory.userName}. Always remember to address them by name when appropriate.`;
            }
            
            if (memory.preferences && memory.preferences.length > 0) {
                systemPrompt += ` The user has expressed preferences for: ${memory.preferences.join(', ')}.`;
            }
            
            if (memory.topics && memory.topics.length > 0) {
                systemPrompt += ` Previous conversation topics include: ${memory.topics.join(', ')}.`;
            }
        }
        
        return systemPrompt;
    }
    
    // Event listeners
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            console.log("Send button clicked");
            sendMessage();
        });
    }
    
    // Handle Enter key press
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                console.log("Enter key pressed");
                e.preventDefault(); // Prevent default to avoid new line
                sendMessage();
            }
        });
    }
    
    // Chat item selection
    if (chatItems.length > 0) {
        chatItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                chatItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Get chat ID from data attribute or create one
                const chatTitle = this.querySelector('h3').textContent;
                currentChatId = this.getAttribute('data-chat-id') || chatTitle.toLowerCase().replace(/\s+/g, '-');
                
                // Load chat history
                loadChatHistory(currentChatId);
            });
        });
    }
    
    // Modal handling
    if (newChatBtn && modal) {
        newChatBtn.addEventListener('click', function() {
            modal.style.display = 'flex';
        });
    }
    
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    if (cancelBtn && modal) {
        cancelBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    if (chatForm && modal) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const chatTitle = document.getElementById('chat-title').value.trim();
            
            if (chatTitle) {
                // Create new chat ID
                const chatId = chatTitle.toLowerCase().replace(/\s+/g, '-');
                currentChatId = chatId;
                
                // Create new chat item
                const chatItem = document.createElement('div');
                chatItem.classList.add('chat-item');
                chatItem.setAttribute('data-chat-id', chatId);
                
                chatItem.innerHTML = `
                    <h3>${chatTitle}</h3>
                    <p>New conversation</p>
                `;
                
                // Add click event to new chat item
                chatItem.addEventListener('click', function() {
                    chatItems.forEach(i => i.classList.remove('active'));
                    this.classList.add('active');
                    currentChatId = chatId;
                    loadChatHistory(currentChatId);
                });
                
                // Add to sidebar
                document.querySelector('.chat-sidebar').appendChild(chatItem);
                
                // Clear existing messages
                messagesContainer.innerHTML = '';
                chatHistory = [];
                
                // Initialize memory for new chat
                if (!chatMemories[chatId]) {
                    chatMemories[chatId] = {
                        userName: null,
                        preferences: [],
                        topics: []
                    };
                    
                    // If we know the user's name from other chats, use it here too
                    for (const existingChatId in chatMemories) {
                        if (chatMemories[existingChatId].userName) {
                            chatMemories[chatId].userName = chatMemories[existingChatId].userName;
                            break;
                        }
                    }
                    
                    localStorage.setItem('chatMemories', JSON.stringify(chatMemories));
                }
                
                // Add welcome message
                if (chatMemories[chatId].userName) {
                    addMessage(`Hello ${chatMemories[chatId].userName}! Welcome to your new chat: "${chatTitle}"`);
                } else {
                    addMessage(`Hello! I'm Tryambakam's general intelligence. How can I help you today?`);
                }
            }
        });
    }

    // Add this CSS to style the delete button
    document.head.insertAdjacentHTML('beforeend', `
    <style>
    .chat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .chat-item-content {
        display: flex;
        align-items: center;
        flex: 1;
    }

    .chat-item-actions {
        display: flex;
        align-items: center;
    }

    .delete-chat-btn {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 5px;
        border-radius: 4px;
        transition: all 0.2s ease;
        opacity: 0.6;
    }

    .delete-chat-btn:hover {
        color: #ff4d4d;
        background-color: rgba(255, 77, 77, 0.1);
        opacity: 1;
    }

    .chat-item:hover .delete-chat-btn {
        opacity: 1;
    }
    </style>
    `);

    // Update the loadChats function to ensure the template is used correctly
    function loadChats() {
        fetch('/api/chats')
            .then(response => response.json())
            .then(chats => {
                chatSidebar.innerHTML = '';
                
                chats.forEach(chat => {
                    // Create the chat item directly instead of using the template
                    const chatItem = document.createElement('div');
                    chatItem.className = 'chat-item';
                    chatItem.setAttribute('data-id', chat.id);
                    
                    chatItem.innerHTML = `
                        <div class="chat-item-content">
                            <i class="fas fa-comments"></i>
                            <span class="chat-title">${chat.title}</span>
                        </div>
                        <div class="chat-item-actions">
                            <button class="delete-chat-btn" title="Delete chat">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                    
                    chatSidebar.appendChild(chatItem);
                });
                
                // Add click event listeners to chat items
                document.querySelectorAll('.chat-item').forEach(item => {
                    item.addEventListener('click', function(e) {
                        // Only trigger if the click wasn't on the delete button
                        if (!e.target.closest('.delete-chat-btn')) {
                            const chatId = this.getAttribute('data-id');
                            loadChat(chatId);
                        }
                    });
                });
                
                // Add click event listeners to delete buttons
                document.querySelectorAll('.delete-chat-btn').forEach(button => {
                    button.addEventListener('click', function(e) {
                        e.stopPropagation(); // Prevent triggering the chat item click
                        const chatId = this.closest('.chat-item').getAttribute('data-id');
                        deleteChat(chatId);
                    });
                });
                
                // Load the first chat if available
                if (chats.length > 0 && !currentChatId) {
                    loadChat(chats[0].id);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Add the deleteChat function
    function deleteChat(chatId) {
        if (confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
            fetch(`/api/chats/${chatId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the chat from the sidebar
                    const chatItem = document.querySelector(`.chat-item[data-id="${chatId}"]`);
                    if (chatItem) {
                        chatItem.remove();
                    }
                    
                    // If the deleted chat was the current chat, load another chat
                    if (currentChatId === chatId) {
                        const firstChat = document.querySelector('.chat-item');
                        if (firstChat) {
                            const firstChatId = firstChat.getAttribute('data-id');
                            loadChat(firstChatId);
                        } else {
                            // No chats left, clear the chat area
                            messagesContainer.innerHTML = '';
                            currentChatId = null;
                        }
                    }
                    
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'success-message';
                    successMessage.textContent = 'Chat deleted successfully';
                    document.body.appendChild(successMessage);
                    
                    // Remove success message after 3 seconds
                    setTimeout(() => {
                        successMessage.remove();
                    }, 3000);
                } else {
                    alert('Error deleting chat: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting chat');
            });
        }
    }

    // Improved function to toggle the main sidebar
    function toggleMainSidebar() {
        const appContainer = document.querySelector('.app-container');
        appContainer.classList.toggle('sidebar-collapsed');
        
        // Log the state to verify it's working
        console.log('Main sidebar collapsed:', appContainer.classList.contains('sidebar-collapsed'));
        
        // Force a reflow to ensure the CSS changes take effect
        void appContainer.offsetWidth;
        
        // Check if the chat sidebar toggle position is updating
        const chatToggle = document.querySelector('.chat-sidebar-toggle');
        if (chatToggle) {
            console.log('Chat toggle position:', window.getComputedStyle(chatToggle).left);
        }
    }

    // Make sure the main sidebar toggle button exists and has the correct event listener
    const mainSidebarToggle = document.querySelector('.main-sidebar-toggle');
    
    if (mainSidebarToggle) {
        console.log('Main sidebar toggle button found');
        
        // Remove any existing event listeners
        mainSidebarToggle.removeEventListener('click', toggleMainSidebar);
        
        // Add the event listener
        mainSidebarToggle.addEventListener('click', toggleMainSidebar);
    } else {
        console.error('Main sidebar toggle button not found');
        
        // If the button doesn't exist, let's create it
        const leftNav = document.querySelector('.left-nav');
        if (leftNav) {
            const toggleButton = document.createElement('button');
            toggleButton.className = 'main-sidebar-toggle';
            toggleButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
            toggleButton.setAttribute('title', 'Toggle Main Sidebar');
            
            toggleButton.addEventListener('click', toggleMainSidebar);
            
            document.body.appendChild(toggleButton);
            console.log('Created main sidebar toggle button');
        }
    }
});