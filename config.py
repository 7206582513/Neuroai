config.py:# Configuration settings for EduVoice.AI
import os


# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"


# Directories
DATA_DIR = "chapters"
UPLOADS_DIR = "uploads"
AUDIO_DIR = "audio"
USER_DATA_DIR = "user_data"


# User Settings
DEFAULT_USER_ID = "demo_user"
TTS_RATE = 120  # Slower for neuro-friendly learning
TTS_PAUSE_DURATION = 0.5


# Learning Settings
FLASHCARD_DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
QUIZ_QUESTION_COUNT = 3
FOCUS_TIME_THRESHOLD = 10  # seconds
STREAK_GOALS = [3, 7, 14, 30]


# Supported Languages
SUPPORTED_LANGUAGES = {
   "English": "en",
   "Hindi": "hi",
   "Spanish": "es",
   "French": "fr"
}


# Mood Options
MOOD_OPTIONS = {
   "😊": "Happy",
   "😐": "Neutral",
   "😔": "Sad",
   "😤": "Frustrated",
   "🤔": "Confused",
   "😴": "Tired"
}


# Create directories if they don't exist
for dir_name in [DATA_DIR, UPLOADS_DIR, AUDIO_DIR, USER_DATA_DIR]:
   os.makedirs(dir_name, exist_ok=True)

