"""
Simplified BERT-based sentiment analysis model
"""
import logging
from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import numpy as np
import re

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Simple sentiment analyzer for real-time analysis"""
    
    def __init__(self):
        # Simple keyword-based sentiment analysis
        self.positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'love', 'like', 'happy', 'joy', 'success', 'win', 'best', 'perfect',
            'beautiful', 'brilliant', 'outstanding', 'superb', 'magnificent'
        ]
        
        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry',
            'sad', 'disappointed', 'fail', 'worst', 'disgusting', 'pathetic',
            'stupid', 'ridiculous', 'annoying', 'frustrating', 'outrageous'
        ]
        
        logger.info("Sentiment analyzer initialized")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            if not text:
                return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}
            
            # Clean and tokenize text
            words = re.findall(r'\b\w+\b', text.lower())
            
            if not words:
                return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}
            
            # Count positive and negative words
            pos_count = sum(1 for word in words if word in self.positive_words)
            neg_count = sum(1 for word in words if word in self.negative_words)
            
            total_words = len(words)
            
            # Calculate scores
            pos_score = pos_count / total_words if total_words > 0 else 0.0
            neg_score = neg_count / total_words if total_words > 0 else 0.0
            neu_score = max(0.0, 1.0 - pos_score - neg_score)
            
            # Calculate compound score
            compound = pos_score - neg_score
            
            # Normalize compound score to [-1, 1]
            compound = max(-1.0, min(1.0, compound * 2))
            
            return {
                'compound': compound,
                'pos': pos_score,
                'neg': neg_score,
                'neu': neu_score
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}

class SentinelBERTModel:
    """Simplified BERT model for sentiment analysis"""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def initialize(self):
        """Initialize the model"""
        try:
            logger.info(f"Loading model {self.model_name} on {self.device}")
            
            # Use pipeline for simplicity
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fallback to a smaller model
            try:
                logger.info("Falling back to distilbert model")
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=0 if self.device == "cuda" else -1,
                    return_all_scores=True
                )
                return True
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                return False
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        if not self.pipeline:
            raise RuntimeError("Model not initialized")
        
        try:
            # Clean text
            text = text.strip()[:512]  # Limit length
            if not text:
                return {
                    "positive": 0.33,
                    "negative": 0.33,
                    "neutral": 0.34,
                    "confidence": 0.0
                }
            
            results = self.pipeline(text)
            
            # Convert to our format
            sentiment_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
            
            for result in results[0]:  # results is a list of lists
                label = result['label'].lower()
                score = result['score']
                
                if 'pos' in label or label == 'label_2':
                    sentiment_scores['positive'] = score
                elif 'neg' in label or label == 'label_0':
                    sentiment_scores['negative'] = score
                else:
                    sentiment_scores['neutral'] = score
            
            # If we only have positive/negative, calculate neutral
            if sentiment_scores['neutral'] == 0.0:
                sentiment_scores['neutral'] = 1.0 - sentiment_scores['positive'] - sentiment_scores['negative']
                sentiment_scores['neutral'] = max(0.0, sentiment_scores['neutral'])
            
            # Calculate confidence as the highest score
            confidence = max(sentiment_scores.values())
            
            return {
                **sentiment_scores,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34,
                "confidence": 0.0
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        return results