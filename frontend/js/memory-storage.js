// Optimized Memory Storage System
const MemoryStorage = (function() {
    // Cache for memory data
    let memoryCache = {
        health: null,
        work: null,
        journal: null
    };
    
    // Check if storage is initialized
    let isInitialized = false;
    
    return {
        // Initialize storage
        init: function() {
            if (isInitialized) return;
            
            if (!localStorage.getItem('healthMemory')) {
                localStorage.setItem('healthMemory', JSON.stringify([]));
            }
            if (!localStorage.getItem('workMemory')) {
                localStorage.setItem('workMemory', JSON.stringify([]));
            }
            if (!localStorage.getItem('journalMemory')) {
                localStorage.setItem('journalMemory', JSON.stringify([]));
            }
            
            // Load initial cache
            this.refreshCache();
            isInitialized = true;
        },
        
        // Refresh the memory cache
        refreshCache: function() {
            memoryCache.health = JSON.parse(localStorage.getItem('healthMemory') || '[]');
            memoryCache.work = JSON.parse(localStorage.getItem('workMemory') || '[]');
            memoryCache.journal = JSON.parse(localStorage.getItem('journalMemory') || '[]');
        },
        
        // Store memory in appropriate lane(s)
        storeMemory: function(content, memoryLanes, timestamp = new Date().toISOString(), isUser = false) {
            memoryLanes.forEach(lane => {
                const laneKey = `${lane.toLowerCase()}Memory`;
                const memories = memoryCache[lane.toLowerCase()] || JSON.parse(localStorage.getItem(laneKey) || '[]');
                
                memories.push({
                    content: content,
                    timestamp: timestamp,
                    source: 'overall',
                    isUser: isUser
                });
                
                // Update cache
                memoryCache[lane.toLowerCase()] = memories;
                
                // Update localStorage
                localStorage.setItem(laneKey, JSON.stringify(memories));
            });
        },
        
        // Get memories from a specific lane
        getMemories: function(lane) {
            const laneKey = lane.toLowerCase();
            
            // Return from cache if available
            if (memoryCache[laneKey] !== null) {
                return memoryCache[laneKey];
            }
            
            // Otherwise get from localStorage and update cache
            const memories = JSON.parse(localStorage.getItem(`${laneKey}Memory`) || '[]');
            memoryCache[laneKey] = memories;
            return memories;
        },
        
        // Get all memories
        getAllMemories: function() {
            // Ensure cache is up to date
            this.refreshCache();
            
            return {
                health: memoryCache.health,
                work: memoryCache.work,
                journal: memoryCache.journal
            };
        },
        
        // Clear memory for a specific lane
        clearMemory: function(lane) {
            const laneKey = lane.toLowerCase();
            localStorage.setItem(`${laneKey}Memory`, JSON.stringify([]));
            memoryCache[laneKey] = [];
        },
        
        // Clear all memories
        clearAllMemories: function() {
            localStorage.setItem('healthMemory', JSON.stringify([]));
            localStorage.setItem('workMemory', JSON.stringify([]));
            localStorage.setItem('journalMemory', JSON.stringify([]));
            
            memoryCache.health = [];
            memoryCache.work = [];
            memoryCache.journal = [];
        },
        
        // Add deleteMemory method to MemoryStorage
        deleteMemory: function(lane, memoryId) {
            const laneKey = lane.toLowerCase();
            const memories = this.getMemories(laneKey);
            
            // Find the memory by ID
            const memoryIndex = memories.findIndex(m => 
                generateMemoryId({...m, lane: laneKey}) === memoryId
            );
            
            if (memoryIndex !== -1) {
                // Remove the memory
                memories.splice(memoryIndex, 1);
                
                // Update cache
                memoryCache[laneKey] = memories;
                
                // Update localStorage
                localStorage.setItem(`${laneKey}Memory`, JSON.stringify(memories));
                
                return true;
            }
            
            return false;
        }
    };
})();

// Initialize memory storage
document.addEventListener('DOMContentLoaded', function() {
    MemoryStorage.init();
});

// Helper function to generate consistent memory IDs
function generateMemoryId(memory) {
    return `${memory.lane}-${memory.timestamp}-${memory.isUser ? 'user' : 'ai'}`;
} 