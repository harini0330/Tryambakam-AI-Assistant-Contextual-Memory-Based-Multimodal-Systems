document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link and corresponding section
            this.classList.add('active');
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Modal handling
    const newChatModal = document.getElementById('new-chat-modal');
    const newChatBtn = document.getElementById('new-chat-btn');
    const closeBtn = document.querySelector('.close');
    
    newChatBtn.addEventListener('click', function() {
        newChatModal.style.display = 'block';
    });
    
    closeBtn.addEventListener('click', function() {
        newChatModal.style.display = 'none';
    });
    
    window.addEventListener('click', function(e) {
        if (e.target === newChatModal) {
            newChatModal.style.display = 'none';
        }
    });
    
    // Voice toggle
    const voiceToggleBtn = document.getElementById('voice-toggle-btn');
    let voiceEnabled = false;
    
    voiceToggleBtn.addEventListener('click', function() {
        voiceEnabled = !voiceEnabled;
        if (voiceEnabled) {
            voiceToggleBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            voiceToggleBtn.classList.add('active');
        } else {
            voiceToggleBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            voiceToggleBtn.classList.remove('active');
        }
        
        // Send request to toggle voice
        fetch('/api/voice/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enabled: voiceEnabled })
        });
    });
    
    // File upload handling
    const uploadFileBtn = document.getElementById('upload-file-btn');
    const fileUploadInput = document.getElementById('file-upload');
    
    uploadFileBtn.addEventListener('click', function() {
        fileUploadInput.click();
    });
    
    fileUploadInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const currentChatId = document.querySelector('.chat-list li.active')?.getAttribute('data-id');
            
            if (!currentChatId) {
                alert('Please select a chat first');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('chat_id', currentChatId);
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('File uploaded and processed successfully');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error uploading file');
            });
        }
    });
    
    // Load core functionality immediately
    initializeCore();
    
    // Lazy load other components
    setTimeout(() => {
        loadExpertsModule();
        loadVisionModule();
    }, 100);
});

function initializeCore() {
    // Core functionality that's needed immediately
    // ... existing code ...
}

function loadExpertsModule() {
    const script = document.createElement('script');
    script.src = 'js/experts.js';
    script.async = true;
    document.body.appendChild(script);
}

function loadVisionModule() {
    const script = document.createElement('script');
    script.src = 'js/vision.js';
    script.async = true;
    document.body.appendChild(script);
} 