"""
Simplified influence score calculator
"""
import logging
from typing import Dict, Any
import math

logger = logging.getLogger(__name__)

class InfluenceCalculator:
    """Calculate user influence scores"""
    
    def __init__(self):
        pass
    
    def calculate_influence(self, text: str, user_metadata: Dict = None) -> float:
        """Calculate influence score for a user/text"""
        if not user_metadata:
            user_metadata = {}
        
        score = 0.0
        
        # Base score from text characteristics
        text_length = len(text)
        if text_length > 100:
            score += 0.1
        if text_length > 280:
            score += 0.1
        
        # Check for engagement indicators in text
        engagement_words = ['like', 'share', 'comment', 'follow', 'subscribe']
        for word in engagement_words:
            if word in text.lower():
                score += 0.05
        
        # Check for authority indicators
        authority_words = ['expert', 'professional', 'official', 'verified']
        for word in authority_words:
            if word in text.lower():
                score += 0.1
        
        # Metadata-based scoring (if available)
        if user_metadata:
            followers = user_metadata.get('followers', 0)
            if followers > 1000:
                score += 0.2
            if followers > 10000:
                score += 0.2
            if followers > 100000:
                score += 0.3
            
            # Account age factor
            account_age_days = user_metadata.get('account_age_days', 0)
            if account_age_days > 365:
                score += 0.1
            if account_age_days > 365 * 3:
                score += 0.1
            
            # Verification status
            if user_metadata.get('verified', False):
                score += 0.2
        
        # Normalize score to 0-1 range
        score = min(score, 1.0)
        
        return score
    
    def calculate_batch(self, texts: list, user_metadata_list: list = None) -> list:
        """Calculate influence scores for multiple texts"""
        results = []
        for i, text in enumerate(texts):
            metadata = user_metadata_list[i] if user_metadata_list and i < len(user_metadata_list) else None
            influence = self.calculate_influence(text, metadata)
            results.append(influence)
        return results