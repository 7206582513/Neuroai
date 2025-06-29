import requests
import json
import os
from datetime import datetime
from typing import List, Dict
import streamlit as st
from config import GROQ_API_KEY, GROQ_MODEL

class AICoach:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.conversation_file = f"user_data/{user_id}_coach_conversations.json"
        self.user_profile_file = f"user_data/{user_id}_profile.json"
        self.load_user_profile()
    
    def load_user_profile(self):
        """Load user learning profile"""
        if os.path.exists(self.user_profile_file):
            with open(self.user_profile_file, 'r') as f:
                self.user_profile = json.load(f)
        else:
            self.user_profile = {
                "learning_style": "mixed",
                "difficulty_preference": "medium",
                "topics_struggled": [],
                "topics_mastered": [],
                "preferred_explanation_style": "analogies",
                "language_preference": "English"
            }
    
    def save_user_profile(self):
        """Save updated user profile"""
        with open(self.user_profile_file, 'w') as f:
            json.dump(self.user_profile, f, indent=2)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get recent conversation history"""
        if os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'r') as f:
                conversations = json.load(f)
                return conversations[-10:]  # Last 10 exchanges
        return []
    
    def save_conversation(self, user_message: str, coach_response: str):
        """Save conversation exchange"""
        conversations = []
        if os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'r') as f:
                conversations = json.load(f)
        
        conversations.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "coach_response": coach_response
        })
        
        # Keep only last 50 conversations
        conversations = conversations[-50:]
        
        with open(self.conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def detect_emotion(self, message: str) -> str:
        """Simple emotion detection from user message"""
        frustrated_words = ["frustrated", "confused", "don't understand", "hard", "difficult", "stuck"]
        confident_words = ["got it", "understand", "clear", "easy", "makes sense"]
        curious_words = ["why", "how", "what if", "interesting", "tell me more"]
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in frustrated_words):
            return "frustrated"
        elif any(word in message_lower for word in confident_words):
            return "confident"
        elif any(word in message_lower for word in curious_words):
            return "curious"
        else:
            return "neutral"
    
    def generate_coach_response(self, user_message: str, current_topic: str = "") -> str:
        """Generate AI coach response with personality and adaptation"""
        if not self.api_key:
            return "🤖 AI Coach not available - please configure GROQ_API_KEY"
        
        emotion = self.detect_emotion(user_message)
        conversation_history = self.get_conversation_history()
        
        # Build context-aware system prompt
        system_prompt = self._build_coach_system_prompt(emotion, current_topic, conversation_history)
        
        # Create conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        for conv in conversation_history[-3:]:  # Last 3 exchanges
            messages.extend([
                {"role": "user", "content": conv["user_message"]},
                {"role": "assistant", "content": conv["coach_response"]}
            ])
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 500
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            coach_response = response.json()['choices'][0]['message']['content'].strip()
            
            # Save conversation
            self.save_conversation(user_message, coach_response)
            
            # Update user profile based on interaction
            self._update_user_profile(user_message, emotion)
            
            return coach_response
            
        except Exception as e:
            return f"🤖 Sorry, I'm having trouble right now. Error: {str(e)}"
    
    def _build_coach_system_prompt(self, emotion: str, current_topic: str, history: List[Dict]) -> str:
        """Build personalized system prompt based on user state"""
        base_prompt = """You are an empathetic AI learning coach specialized in neuro-friendly education. Your personality:
        - Patient, encouraging, and supportive
        - Uses analogies, stories, and real-world examples
        - Breaks complex concepts into digestible pieces
        - Celebrates small wins and progress
        - Adapts explanation style based on user needs
        """
        
        # Emotion-specific adaptations
        emotion_adaptations = {
            "frustrated": """
            The student seems frustrated. Your response should:
            - Acknowledge their frustration with empathy
            - Break down the concept into smaller, easier steps
            - Use encouraging language like "It's totally normal to find this challenging"
            - Offer alternative explanation methods
            - Suggest taking a short break if needed
            """,
            "confident": """
            The student seems confident. Your response should:
            - Celebrate their understanding
            - Offer slightly more advanced concepts or connections
            - Ask thoughtful questions to deepen understanding
            - Encourage them to explain concepts back to you
            """,
            "curious": """
            The student is curious and engaged. Your response should:
            - Feed their curiosity with interesting details
            - Make connections to other topics they might find fascinating
            - Use "what if" scenarios and thought experiments
            - Encourage exploration and questions
            """,
            "neutral": """
            The student seems neutral. Your response should:
            - Be engaging and try to spark interest
            - Use relatable examples and analogies
            - Check for understanding
            - Keep the energy positive
            """
        }
        
        # Add user profile information
        profile_context = f"""
        User Learning Profile:
        - Preferred explanation style: {self.user_profile.get('preferred_explanation_style', 'analogies')}
        - Learning difficulty preference: {self.user_profile.get('difficulty_preference', 'medium')}
        - Previously struggled with: {', '.join(self.user_profile.get('topics_struggled', []))}
        - Has mastered: {', '.join(self.user_profile.get('topics_mastered', []))}
        """
        
        # Add current topic context
        topic_context = f"Current topic being studied: {current_topic}" if current_topic else ""
        
        return f"{base_prompt}\n{emotion_adaptations.get(emotion, '')}\n{profile_context}\n{topic_context}"
    
    def _update_user_profile(self, user_message: str, emotion: str):
        """Update user profile based on interaction"""
        # Simple keyword-based topic extraction
        topics = ["math", "science", "history", "english", "physics", "chemistry", "biology", "literature"]
        
        message_lower = user_message.lower()
        for topic in topics:
            if topic in message_lower:
                if emotion == "frustrated" and topic not in self.user_profile["topics_struggled"]:
                    self.user_profile["topics_struggled"].append(topic)
                elif emotion == "confident" and topic not in self.user_profile["topics_mastered"]:
                    self.user_profile["topics_mastered"].append(topic)
        
        self.save_user_profile()
    
    def get_learning_suggestions(self) -> List[str]:
        """Generate personalized learning suggestions"""
        suggestions = []
        
        if self.user_profile["topics_struggled"]:
            suggestions.append(f"💡 Let's revisit {', '.join(self.user_profile['topics_struggled'][:2])} with a different approach")
        
        if self.user_profile["topics_mastered"]:
            suggestions.append(f"🚀 Since you've mastered {', '.join(self.user_profile['topics_mastered'][:2])}, let's explore advanced concepts")
        
        suggestions.extend([
            "🎯 Try a focused 15-minute learning session",
            "🧩 Generate flashcards for active recall",
            "📊 Check your focus analytics to optimize study time",
            "🎮 Take a quick quiz to test your understanding"
        ])
        
        return suggestions[:4]
    
    def generate_motivational_message(self) -> str:
        """Generate personalized motivational message"""
        messages = [
            "🌟 Every expert was once a beginner. You're making great progress!",
            "🧠 Your brain is literally rewiring itself as you learn. That's amazing!",
            "💪 Challenges are just opportunities to grow stronger mentally.",
            "🎯 Small consistent steps lead to big achievements.",
            "✨ The fact that you're here learning shows your dedication!"
        ]
        
        return messages[datetime.now().day % len(messages)]