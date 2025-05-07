document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Check if sidebar was collapsed in previous session
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
    
    // Vision functionality
    const uploadBtn = document.getElementById('upload-image-btn');
    const webcamBtn = document.getElementById('webcam-btn');
    const imageContainer = document.getElementById('image-container');
    const webcamContainer = document.getElementById('webcam-container');
    const captureBtn = document.getElementById('capture-btn');
    const webcamElement = document.getElementById('webcam');
    const visionInput = document.getElementById('vision-input');
    const sendVisionBtn = document.getElementById('send-vision-btn');
    const messagesContainer = document.getElementById('vision-messages');
    const uploadModal = document.getElementById('upload-modal');
    const closeModalBtn = document.querySelector('.close-btn');
    const cancelModalBtn = document.querySelector('.cancel-btn');
    const uploadForm = document.getElementById('upload-form');
    const analysisButtons = document.querySelectorAll('.analysis-btn');
    
    let imageUploaded = false;
    let webcamActive = false;
    let currentImageBase64 = null;
    
    // OpenAI API Key
    const OPENAI_API_KEY = '';
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false, isFormatted = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        
        const iconDiv = document.createElement('div');
        iconDiv.classList.add('message-icon');
        
        const icon = document.createElement('i');
        icon.className = isUser ? 'fas fa-user' : 'fas fa-eye';
        iconDiv.appendChild(icon);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        if (isFormatted) {
            // Process content to identify and format code blocks
            let processedContent = content;
            
            // Check if content contains code (looks for triple backticks)
            if (!isUser && content.includes('```')) {
                // Format code blocks with copy buttons
                processedContent = formatCodeBlocks(content);
            } else if (!isUser && content.includes('**')) {
                // Convert markdown-style formatting to HTML
                processedContent = content
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br>');
            }
            
            contentDiv.innerHTML = processedContent;
            
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
        
        messageDiv.appendChild(iconDiv);
        messageDiv.appendChild(contentDiv);
        
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return messageDiv;
    }
    
    // Function to format code blocks with copy buttons
    function formatCodeBlocks(content) {
        // Split by code blocks
        const parts = content.split(/```(\w*)/);
        let result = '';
        let inCodeBlock = false;
        let language = '';
        
        for (let i = 0; i < parts.length; i++) {
            if (i % 2 === 0) {
                // Regular text content
                if (!inCodeBlock) {
                    // Convert markdown in regular text
                    result += parts[i].replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
                } else {
                    // This is code content
                    const code = parts[i].replace(/```\s*$/, '').trim();
                    result += `<div class="code-block-container">
                                <div class="code-block-header">
                                    <span class="code-language">${language || 'code'}</span>
                                    <button class="copy-code-btn">Copy code</button>
                                </div>
                                <pre class="code-block"><code class="${language}">${escapeHtml(code)}</code></pre>
                              </div>`;
                    inCodeBlock = false;
                }
            } else {
                // Language identifier
                language = parts[i];
                inCodeBlock = true;
            }
        }
        
        return result;
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
    
    // Function to handle sending a message
    function sendMessage(customPrompt = null) {
        const message = customPrompt || visionInput.value.trim();
        
        if (message && currentImageBase64) {
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input if not a custom prompt
            if (!customPrompt) {
                visionInput.value = '';
            }
            
            // Show loading indicator
            const loadingMessage = addMessage("Analyzing image...", false);
            
            // Prepare the prompt based on the type of analysis
            let enhancedPrompt = message;
            if (customPrompt) {
                // For standard analysis buttons, add structure to the prompt
                enhancedPrompt += ". Format your response with clear sections using ** for headings and organize information in a structured way.";
            }
            
            // Make direct request to OpenAI API
            fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${OPENAI_API_KEY}`
                },
                body: JSON.stringify({
                    model: "gpt-4o",
                    messages: [
                        {
                            role: "user",
                            content: [
                                { type: "text", text: enhancedPrompt },
                                {
                                    type: "image_url",
                                    image_url: {
                                        url: `data:image/jpeg;base64,${currentImageBase64}`
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens: 500
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error?.message || 'OpenAI API error');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Remove loading indicator
                loadingMessage.remove();
                
                if (data.error) {
                    console.error("API Error:", data.error);
                    addMessage("Error: " + data.error.message, false);
                } else {
                    // Add AI response with formatting
                    const responseText = data.choices[0].message.content;
                    addMessage(responseText, false, true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingMessage.remove();
                addMessage("I apologize, but I encountered an error analyzing the image: " + error.message, false);
            });
        } else if (!currentImageBase64) {
            addMessage("Please upload or capture an image first.", false);
        } else if (!message) {
            addMessage("Please enter a question about the image.", false);
        }
    }
    
    // Event listeners for sending messages
    sendVisionBtn.addEventListener('click', function() {
        sendMessage();
    });
    
    // Handle Enter key press
    visionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Add event listeners for the analysis buttons
    analysisButtons.forEach(button => {
        button.addEventListener('click', function() {
            const prompt = this.getAttribute('data-prompt');
            if (prompt) {
                sendMessage(prompt);
            }
        });
    });
    
    // Upload button - now styled as a card
    uploadBtn.addEventListener('click', function() {
        uploadModal.style.display = 'block';
    });
    
    // Close modal
    closeModalBtn.addEventListener('click', function() {
        uploadModal.style.display = 'none';
    });
    
    // Cancel button
    cancelModalBtn.addEventListener('click', function() {
        uploadModal.style.display = 'none';
    });
    
    // Handle image upload
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('image-input');
        const file = fileInput.files[0];
        
        if (file) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                
                // Clear container and add image
                imageContainer.innerHTML = '';
                imageContainer.appendChild(img);
                
                // Get base64 data (remove data:image/jpeg;base64, prefix)
                const base64Data = e.target.result.split(',')[1];
                currentImageBase64 = base64Data;
                
                imageUploaded = true;
                webcamActive = false;
                
                // Show image container, hide webcam container
                imageContainer.style.display = 'block';
                webcamContainer.style.display = 'none';
                
                // Add system message
                addMessage("Image uploaded successfully. What would you like to know about this image?");
                
                // Close modal
                uploadModal.style.display = 'none';
            };
            
            reader.readAsDataURL(file);
        }
    });
    
    // Webcam button
    webcamBtn.addEventListener('click', function() {
        if (webcamActive) {
            stopWebcam();
            webcamActive = false;
            webcamContainer.style.display = 'none';
            imageContainer.style.display = 'block';
        } else {
            startWebcam();
        }
    });
    
    // Start webcam
    function startWebcam() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    webcamElement.srcObject = stream;
                    webcamActive = true;
                    imageUploaded = false;
                    
                    // Show webcam container, hide image container
                    webcamContainer.style.display = 'block';
                    imageContainer.style.display = 'none';
                    
                    // Add system message
                    addMessage("Webcam activated. You can capture an image or ask questions about what the webcam sees.");
                })
                .catch(function(error) {
                    console.error("Error accessing webcam:", error);
                    addMessage("Error accessing webcam. Please check your permissions and try again.");
                });
        } else {
            addMessage("Your browser doesn't support webcam access.");
        }
    }
    
    // Stop webcam
    function stopWebcam() {
        if (webcamElement.srcObject) {
            const tracks = webcamElement.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            webcamElement.srcObject = null;
            webcamActive = false;
        }
    }
    
    // Capture image from webcam
    captureBtn.addEventListener('click', function() {
        if (webcamActive) {
            const canvas = document.createElement('canvas');
            canvas.width = webcamElement.videoWidth;
            canvas.height = webcamElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcamElement, 0, 0, canvas.width, canvas.height);
            
            const imageUrl = canvas.toDataURL('image/jpeg');
            
            // Get base64 data (remove data:image/jpeg;base64, prefix)
            currentImageBase64 = imageUrl.split(',')[1];
            
            // Hide webcam, show captured image
            webcamContainer.style.display = 'none';
            imageContainer.style.display = 'block';
            imageContainer.innerHTML = `<img src="${imageUrl}" alt="Captured image">`;
            
            imageUploaded = true;
            
            // Add system message
            addMessage("Image captured. What would you like to know about this image?");
        }
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === uploadModal) {
            uploadModal.style.display = 'none';
        }
    });
}); 