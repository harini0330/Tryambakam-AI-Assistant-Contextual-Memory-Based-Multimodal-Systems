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
        self.enabled = False
        self.voice_engine = None
        self.init_voice_engine()
        
    def init_voice_engine(self):
        try:
            import pyttsx3
            self.voice_engine = pyttsx3.init()
            self.voice_engine.setProperty('rate', 150)
            self.voice_engine.setProperty('volume', 0.8)
            self.enabled = True
        except Exception as e:
            print(f"Warning: Could not initialize voice engine: {e}")
            self.enabled = False
            
    def toggle(self, enabled=None):
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = not self.enabled
        return self.enabled
        
    def speak(self, text):
        if not self.enabled or not self.voice_engine:
            return False
            
        # Use threading to avoid blocking
        def speak_thread():
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                print(f"Error in voice output: {e}")
                
        threading.Thread(target=speak_thread).start()
        return True

# Create a singleton instance
voice_output = VoiceOutput()

def create_voice_output():
    return voice_output 