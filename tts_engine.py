import pyttsx3
import time
import tempfile
import os
from gtts import gTTS
import streamlit as st
from config import TTS_RATE, TTS_PAUSE_DURATION
import threading
import queue

class NeuroTTSEngine:
    def __init__(self):
        self.engine = None
        self.setup_engine()
    
    def setup_engine(self):
        """Initialize TTS engine with neuro-friendly settings"""
        try:
            self.engine = pyttsx3.init()
            # Set slower rate for better comprehension
            self.engine.setProperty('rate', TTS_RATE)
            # Set voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available (often clearer)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            st.warning(f"TTS Engine warning: {str(e)}")
    
    def speak_with_pauses(self, text: str, pause_sentences: bool = True):
        """Speak text with strategic pauses for neuro-friendly learning"""
        if not self.engine:
            st.error("TTS Engine not available")
            return
        
        try:
            if pause_sentences:
                # Split by sentences and add pauses
                sentences = text.split('.')
                for sentence in sentences:
                    if sentence.strip():
                        self.engine.say(sentence.strip())
                        self.engine.runAndWait()
                        time.sleep(TTS_PAUSE_DURATION)
            else:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            st.error(f"TTS Error: {str(e)}")
    
    def create_audio_file(self, text: str, filename: str = None) -> str:
        """Create audio file using gTTS for better quality"""
        try:
            if not filename:
                filename = f"audio_{int(time.time())}.mp3"
            
            filepath = os.path.join("audio", filename)
            
            # Use gTTS for better quality
            tts = gTTS(text=text, lang='en', slow=True)  # slow=True for neuro-friendly pace
            tts.save(filepath)
            
            return filepath
        except Exception as e:
            st.error(f"Audio file creation error: {str(e)}")
            return None
    
    def speak_async(self, text: str):
        """Speak text asynchronously without blocking UI"""
        def speak_worker():
            self.speak_with_pauses(text)
        
        thread = threading.Thread(target=speak_worker)
        thread.daemon = True
        thread.start()
    
    def create_summary_audio(self, summaries: dict, selected_mode: str) -> str:
        """Create audio file for selected summary mode"""
        if selected_mode not in summaries:
            return None
        
        # Add intro based on mode
        intros = {
            'basic': "Here's your basic summary: ",
            'story': "Let me tell you this as a story: ",
            'visual': "Here's your visual summary: "
        }
        
        full_text = intros.get(selected_mode, "") + summaries[selected_mode]
        return self.create_audio_file(full_text, f"summary_{selected_mode}.mp3")