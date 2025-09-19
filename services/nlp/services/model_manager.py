"""
Model manager for handling ML models
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from models.sentiment_model import SentinelBERTModel
from models.behavior_analyzer import BehavioralPatternAnalyzer
from models.influence_calculator import InfluenceCalculator

logger = logging.getLogger(__name__)

class TextAnalysisResult:
    """Result container for text analysis"""
    def __init__(self, text_id: int = 0):
        self.text_id = text_id
        self.sentiment = None
        self.behavioral_patterns = []
        self.influence_score = None
        self.language = "en"
        self.processing_time_ms = 0.0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "text_id": self.text_id,
            "sentiment": self.sentiment,
            "behavioral_patterns": self.behavioral_patterns,
            "influence_score": self.influence_score,
            "language": self.language,
            "processing_time_ms": self.processing_time_ms
        }

class ModelManager:
    """Manages all ML models and analysis pipeline"""
    
    def __init__(self):
        self.sentiment_model = SentinelBERTModel()
        self.behavior_analyzer = BehavioralPatternAnalyzer()
        self.influence_calculator = InfluenceCalculator()
        self.model_version = "1.0.0-simplified"
        self.initialized = False
    
    async def initialize(self):
        """Initialize all models"""
        try:
            logger.info("Initializing model manager...")
            success = await self.sentiment_model.initialize()
            if success:
                self.initialized = True
                logger.info("Model manager initialized successfully")
            else:
                logger.error("Failed to initialize sentiment model")
        except Exception as e:
            logger.error(f"Error initializing model manager: {e}")
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return self.initialized
    
    def get_current_version(self) -> str:
        """Get current model version"""
        return self.model_version
    
    def list_available_versions(self) -> List[str]:
        """List available model versions"""
        return [self.model_version]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "version": self.model_version,
            "type": "simplified-bert",
            "capabilities": ["sentiment", "behavioral_patterns", "influence_scoring"],
            "status": "loaded" if self.initialized else "not_loaded"
        }
    
    async def load_version(self, version: str):
        """Load a specific model version"""
        if version == self.model_version:
            logger.info(f"Version {version} already loaded")
            return
        else:
            raise ValueError(f"Version {version} not available")
    
    async def analyze_batch(
        self, 
        texts: List[str], 
        include_behavioral: bool = True,
        include_influence: bool = True,
        user_metadata: Optional[List[Dict]] = None
    ) -> List[TextAnalysisResult]:
        """Analyze a batch of texts"""
        if not self.initialized:
            raise RuntimeError("Model manager not initialized")
        
        results = []
        start_time = asyncio.get_event_loop().time()
        
        # Analyze sentiment
        sentiment_results = self.sentiment_model.analyze_batch(texts)
        
        # Analyze behavioral patterns
        behavioral_results = []
        if include_behavioral:
            behavioral_results = self.behavior_analyzer.analyze_batch(texts, user_metadata)
        
        # Calculate influence scores
        influence_results = []
        if include_influence:
            influence_results = self.influence_calculator.calculate_batch(texts, user_metadata)
        
        # Combine results
        for i, text in enumerate(texts):
            result = TextAnalysisResult(text_id=i)
            result.sentiment = sentiment_results[i]
            
            if include_behavioral and i < len(behavioral_results):
                result.behavioral_patterns = behavioral_results[i]
            
            if include_influence and i < len(influence_results):
                result.influence_score = influence_results[i]
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            result.processing_time_ms = processing_time / len(texts)  # Average per text
            
            results.append(result)
        
        return results
    
    async def analyze_sentiment_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment only"""
        if not self.initialized:
            raise RuntimeError("Model manager not initialized")
        
        return self.sentiment_model.analyze_batch(texts)
    
    async def analyze_behavior_batch(self, texts: List[str], user_metadata: Optional[List[Dict]] = None) -> List[List[Dict[str, Any]]]:
        """Analyze behavioral patterns only"""
        return self.behavior_analyzer.analyze_batch(texts, user_metadata)