document.addEventListener('DOMContentLoaded', function() {
    console.log("Memory.js loaded");
    
    // Get DOM elements
    const memoryContainer = document.getElementById('memory-container');
    const laneButtons = document.querySelectorAll('.lane-filter-btn');
    const clearCurrentBtn = document.querySelector('.clear-memory-btn[data-lane="current"]');
    
    // Current active lane
    let activeLane = 'all';
    
    // Function to load memories directly from the server
    function loadMemories(lane = 'all') {
        console.log(`Loading memories for lane: ${lane}`);
        
        // Show loading indicator
        memoryContainer.innerHTML = '<div class="loading">Loading memories...</div>';
        
        // Fetch memories from the server
        fetch(`/api/memory/${lane === 'all' ? 'all' : lane}`)
            .then(response => response.json())
            .then(data => {
                // Clear container
                memoryContainer.innerHTML = '';
                
                if (data.length === 0) {
                    memoryContainer.innerHTML = '<div class="no-memories">No memories found in this lane.</div>';
                    return;
                }
                
                // Sort memories by timestamp (newest first)
                data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                
                // Create memory cards
                data.forEach(memory => {
                    createMemoryCard(memory, lane);
                });
            })
            .catch(error => {
                console.error('Error loading memories:', error);
                memoryContainer.innerHTML = '<div class="error">Error loading memories. Please try again.</div>';
            });
    }
    
    // Function to create a memory card
    function createMemoryCard(memory, lane) {
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.setAttribute('data-id', memory.timestamp);
        card.setAttribute('data-lane', memory.lane || lane);
        
        // Format date
        const date = new Date(memory.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        // Get lane display name (capitalize first letter)
        const laneDisplay = (memory.lane || lane).charAt(0).toUpperCase() + (memory.lane || lane).slice(1);
        
        // Create card content with tabs - User Query first, then AI Response
        card.innerHTML = `
            <div class="memory-header">
                <span class="memory-date">${formattedDate}</span>
            </div>
            <span class="lane-badge ${memory.lane || lane}">${laneDisplay}</span>
            <button class="memory-delete-btn" title="Delete memory">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="memory-tabs">
                <button class="memory-tab active" data-tab="user">User Query</button>
                <button class="memory-tab" data-tab="ai">AI Response</button>
            </div>
            
            <div class="memory-content">
                <div class="memory-tab-content active" data-tab="user">
                    ${memory.human ? `<div class="memory-human">${memory.human}</div>` : '<div class="no-content">No user query</div>'}
                </div>
                <div class="memory-tab-content" data-tab="ai">
                    ${memory.ai ? `<div class="memory-ai">${memory.ai}</div>` : '<div class="no-content">No AI response</div>'}
                </div>
            </div>
        `;
        
        // Add event listener to delete button
        const deleteBtn = card.querySelector('.memory-delete-btn');
        deleteBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent card click event
            deleteMemory(memory.timestamp, memory.lane || lane);
        });
        
        // Add event listeners to tabs
        const tabs = card.querySelectorAll('.memory-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Hide all tab content
                const tabContents = card.querySelectorAll('.memory-tab-content');
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Show selected tab content
                const tabName = this.getAttribute('data-tab');
                card.querySelector(`.memory-tab-content[data-tab="${tabName}"]`).classList.add('active');
            });
        });
        
        memoryContainer.appendChild(card);
    }
    
    // Add function to delete a memory
    function deleteMemory(timestamp, lane) {
        if (confirm('Are you sure you want to delete this memory? This action cannot be undone.')) {
            fetch(`/api/memory/${lane}/${timestamp}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the card from the UI
                    const card = document.querySelector(`.memory-card[data-id="${timestamp}"]`);
                    if (card) {
                        card.remove();
                    }
                    
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'success-message';
                    successMessage.textContent = 'Memory deleted successfully';
                    document.body.appendChild(successMessage);
                    
                    // Remove success message after 3 seconds
                    setTimeout(() => {
                        successMessage.remove();
                    }, 3000);
                } else {
                    alert('Error deleting memory: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting memory');
            });
        }
    }
    
    // Add event listeners to lane filter buttons
    laneButtons.forEach(button => {
        button.addEventListener('click', function() {
            const lane = this.getAttribute('data-lane');
            
            // Update active button
            laneButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update active lane
            activeLane = lane;
            
            // Load memories for the selected lane
            loadMemories(lane);
        });
    });
    
    // Load all memories by default
    loadMemories();
});

// Animation keyframes
document.head.insertAdjacentHTML('beforeend', `
<style>
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    max-width: 80%;
    animation: fadeIn 0.3s ease-out;
}

.message.user {
    background-color: var(--primary-color);
    color: white;
    align-self: flex-end;
    margin-left: auto;
    border-bottom-right-radius: 0;
}

.message.ai {
    background-color: rgba(255, 255, 255, 0.1);
    border-bottom-left-radius: 0;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
`); 