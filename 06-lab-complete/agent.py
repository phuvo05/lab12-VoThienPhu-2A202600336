import os
from typing import List, Dict
import re

class ConversationalAgent:
    def __init__(self):
        self.use_openai = os.getenv("OPENAI_API_KEY") is not None
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 3
        
        if self.use_openai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            except ImportError:
                print("OpenAI package not installed. Falling back to rule-based responses.")
                self.use_openai = False
    
    def get_response(self, user_message: str) -> str:
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Keep only last N messages
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
        
        if self.use_openai:
            response = self._get_openai_response(user_message)
        else:
            response = self._get_rule_based_response(user_message)
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _get_openai_response(self, user_message: str) -> str:
        try:
            messages = [
                {"role": "system", "content": "You are a helpful and friendly AI assistant."}
            ] + self.conversation_history
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._get_rule_based_response(user_message)
    
    def _get_rule_based_response(self, user_message: str) -> str:
        message_lower = user_message.lower().strip()
        
        # Greetings
        if re.search(r'\b(hi|hello|hey|greetings)\b', message_lower):
            return "Hello! How can I help you today?"
        
        # How are you
        if re.search(r'\bhow are you\b', message_lower):
            return "I'm doing great, thank you for asking! How can I assist you?"
        
        # Name questions
        if re.search(r'\b(your name|who are you)\b', message_lower):
            return "I'm a conversational AI agent built with FastAPI. I'm here to chat with you!"
        
        # Help
        if re.search(r'\b(help|what can you do)\b', message_lower):
            return "I'm a simple chatbot. You can chat with me about anything! Try asking me questions or just say hello."
        
        # Goodbye
        if re.search(r'\b(bye|goodbye|see you|farewell)\b', message_lower):
            return "Goodbye! It was nice chatting with you. Come back anytime!"
        
        # Thank you
        if re.search(r'\b(thank|thanks)\b', message_lower):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Weather
        if re.search(r'\bweather\b', message_lower):
            return "I don't have access to real-time weather data, but I hope it's nice where you are!"
        
        # Time
        if re.search(r'\b(time|date)\b', message_lower):
            return "I don't have access to the current time, but you can check your device's clock!"
        
        # Default response
        responses = [
            "That's interesting! Tell me more.",
            "I see. Can you elaborate on that?",
            "Interesting point! What else would you like to discuss?",
            "I understand. How can I help you further?",
            "That's a good question! While I'm a simple bot, I'm here to chat with you."
        ]
        
        # Simple hash-based selection for consistency
        index = sum(ord(c) for c in message_lower) % len(responses)
        return responses[index]
