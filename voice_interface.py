# Try to import required libraries, but provide fallbacks if not available
try:
    import pyttsx3
    import threading
    import queue
    import re
    import time
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Warning: pyttsx3 module not found. Voice output will be disabled.")
    print("To enable voice, install with: pip install pyttsx3")

class VoiceEngine(threading.Thread):
    """A dedicated thread for handling text-to-speech conversion"""
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.queue = queue.Queue()
        self.running = True
        self.speaking = False
        
    def run(self):
        """Main thread loop that processes speech requests"""
        while self.running:
            try:
                # Get the next text to speak (wait up to 0.1 seconds)
                try:
                    text = self.queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process the speech
                try:
                    self.speaking = True
                    
                    # Create a completely new engine for each speech request
                    # This is key to fixing the issue with subsequent responses
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 300)
                    engine.setProperty('volume', 1.0)
                    
                    # For maximum speed, process the entire text at once
                    if text.strip():
                        engine.say(text)
                        engine.runAndWait()
                    
                    # Explicitly stop and dispose of the engine
                    engine.stop()
                    del engine
                    
                    # Add a small delay to ensure complete cleanup
                    time.sleep(0.1)
                    
                finally:
                    self.speaking = False
                    self.queue.task_done()
                    
            except Exception as e:
                print(f"Error in speech engine: {e}")
                time.sleep(0.5)  # Add delay on error
                
    def speak(self, text):
        """Add text to the speech queue"""
        if not text:
            return
            
        # Clean and optimize text for faster speech
        text = self._optimize_text(text)
            
        # Clear any pending speech to start the new one immediately
        with self.queue.mutex:
            self.queue.queue.clear()
            
        self.queue.put(text)
        
    def _optimize_text(self, text):
        """Optimize text for faster speech by removing unnecessary parts"""
        if not text:
            return ""
            
        # Remove markdown and special characters
        text = re.sub(r'[*_#]', '', text)
        
        # Remove parenthetical content (often not essential)
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Shorten very long text by keeping only the first part
        if len(text) > 1000:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) > 10:
                text = ' '.join(sentences[:10]) + '...'
                
        return text.strip()
        
    def stop(self):
        """Stop the speech engine thread"""
        self.running = False
        # Clear the queue
        with self.queue.mutex:
            self.queue.queue.clear()

class VoiceOutput:
    def __init__(self):
        self.voice_enabled = False
        self.engine_thread = None
        
        if VOICE_AVAILABLE:
            try:
                # Test if we can initialize the engine
                test_engine = pyttsx3.init()
                test_engine.stop()
                del test_engine
                
                # Start the voice engine thread
                self.engine_thread = VoiceEngine()
                self.engine_thread.start()
                self.voice_enabled = True
                print("Voice output initialized successfully")
            except Exception as e:
                print(f"Error initializing voice output: {e}")
    
    def speak(self, text, block=False):
        """Convert text to speech"""
        if not VOICE_AVAILABLE or not self.voice_enabled or not self.engine_thread:
            return False
        
        # Clean up text for better speech
        text = self._clean_text(text)
        
        # Send to speech engine
        self.engine_thread.speak(text)
        
        # If blocking mode requested, wait for speech to complete
        if block:
            while not self.engine_thread.queue.empty() or self.engine_thread.speaking:
                time.sleep(0.1)
        
        return True
    
    def _clean_text(self, text):
        """Clean text for better speech synthesis"""
        if not text:
            return ""
            
        # Quick replacements for better speech
        replacements = {
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Misses',
            'Ms.': 'Miss',
            'Prof.': 'Professor',
            '(': '',
            ')': '',
            '*': '',
            '_': '',
            '#': '',
            '...': '',
            '…': '',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def toggle_voice(self):
        """Enable or disable voice output"""
        if not VOICE_AVAILABLE:
            print("Voice output not available. Install pyttsx3 to enable voice.")
            return False
            
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        print(f"Voice output {status}")
        return self.voice_enabled

# Create a singleton instance
voice_output = VoiceOutput()

def create_voice_output():
    return voice_output 