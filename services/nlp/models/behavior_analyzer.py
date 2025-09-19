"""
Simplified behavioral pattern analyzer
"""
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class BehavioralPatternAnalyzer:
    """Simplified behavioral pattern detection"""
    
    def __init__(self):
        self.patterns = {
            'amplification': {
                'keywords': ['retweet', 'share', 'spread', 'viral', 'boost'],
                'indicators': ['excessive_sharing', 'viral_content']
            },
            'coordination': {
                'keywords': ['together', 'unite', 'join', 'organize', 'coordinate'],
                'indicators': ['coordinated_messaging', 'synchronized_posting']
            },
            'astroturfing': {
                'keywords': ['fake', 'bot', 'artificial', 'manufactured'],
                'indicators': ['artificial_engagement', 'fake_grassroots']
            },
            'influence': {
                'keywords': ['follow', 'subscribe', 'influence', 'leader', 'authority'],
                'indicators': ['influence_attempt', 'authority_claim']
            }
        }
    
    def analyze_patterns(self, text: str, user_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Analyze behavioral patterns in text"""
        patterns_found = []
        text_lower = text.lower()
        
        for pattern_type, pattern_data in self.patterns.items():
            score = 0.0
            found_keywords = []
            
            # Check for keywords
            for keyword in pattern_data['keywords']:
                if keyword in text_lower:
                    score += 0.2
                    found_keywords.append(keyword)
            
            # Simple heuristics
            if pattern_type == 'amplification':
                # Check for excessive caps or exclamation marks
                if len(re.findall(r'[A-Z]{3,}', text)) > 0:
                    score += 0.1
                if text.count('!') > 2:
                    score += 0.1
            
            elif pattern_type == 'coordination':
                # Check for time-sensitive language
                if any(word in text_lower for word in ['now', 'urgent', 'immediately', 'today']):
                    score += 0.1
            
            elif pattern_type == 'astroturfing':
                # Check for generic language
                generic_phrases = ['as a citizen', 'as a taxpayer', 'ordinary person']
                if any(phrase in text_lower for phrase in generic_phrases):
                    score += 0.15
            
            elif pattern_type == 'influence':
                # Check for authority claims
                authority_words = ['expert', 'professional', 'experienced', 'certified']
                if any(word in text_lower for word in authority_words):
                    score += 0.1
            
            # Cap the score at 1.0
            score = min(score, 1.0)
            
            if score > 0.1:  # Only include patterns with some confidence
                patterns_found.append({
                    'pattern_type': pattern_type,
                    'score': score,
                    'confidence': min(score * 2, 1.0),  # Simple confidence calculation
                    'indicators': pattern_data['indicators'][:2]  # Limit indicators
                })
        
        return patterns_found
    
    def analyze_batch(self, texts: List[str], user_metadata: List[Dict] = None) -> List[List[Dict[str, Any]]]:
        """Analyze patterns for multiple texts"""
        results = []
        for i, text in enumerate(texts):
            metadata = user_metadata[i] if user_metadata and i < len(user_metadata) else None
            patterns = self.analyze_patterns(text, metadata)
            results.append(patterns)
        return results