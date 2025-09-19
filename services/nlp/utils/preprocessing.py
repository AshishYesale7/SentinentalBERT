"""
Text preprocessing utilities
"""
import re
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Simple text preprocessing"""
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags for sentiment analysis (keep the text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Clean up extra spaces
        text = text.strip()
        
        return text
    
    def preprocess_batch(self, texts: list) -> list:
        """Preprocess a batch of texts"""
        return [self.clean_text(text) for text in texts]