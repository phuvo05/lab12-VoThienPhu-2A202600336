"""
Mock LLM for testing without OpenAI API
"""
import random
import re

class MockLLM:
    """Mock Language Model for testing"""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! I'm here to assist you.",
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! Feel free to come back anytime.",
            ],
            "thanks": [
                "You're welcome!",
                "Happy to help!",
                "Anytime! Let me know if you need anything else.",
            ],
            "help": [
                "I'm a conversational AI assistant. I can chat with you, answer questions, and help with various tasks.",
                "I'm here to help! You can ask me questions, have a conversation, or just chat.",
            ],
            "default": [
                "That's interesting! Tell me more.",
                "I see. Can you elaborate on that?",
                "Interesting point! What else would you like to discuss?",
                "I understand. How can I help you further?",
            ]
        }
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response based on the prompt
        
        Args:
            prompt: User input
            
        Returns:
            str: Generated response
        """
        prompt_lower = prompt.lower().strip()
        
        # Greetings
        if re.search(r'\b(hi|hello|hey|greetings)\b', prompt_lower):
            return random.choice(self.responses["greeting"])
        
        # Farewells
        if re.search(r'\b(bye|goodbye|see you|farewell)\b', prompt_lower):
            return random.choice(self.responses["farewell"])
        
        # Thanks
        if re.search(r'\b(thank|thanks)\b', prompt_lower):
            return random.choice(self.responses["thanks"])
        
        # Help
        if re.search(r'\b(help|what can you do)\b', prompt_lower):
            return random.choice(self.responses["help"])
        
        # Default
        return random.choice(self.responses["default"])
