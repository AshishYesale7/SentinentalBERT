#!/usr/bin/env python3
"""
Simplified SentinelBERT NLP Service for Testing
Provides basic API endpoints without heavy ML dependencies
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv('JWT_SECRET', 'insecure-default-change-in-production')

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for authentication"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        officer_id = payload.get('officer_id')
        if not officer_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing officer_id")
        
        return {
            'officer_id': officer_id,
            'role': payload.get('role', 'user'),
            'permissions': payload.get('permissions', [])
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(user_info: dict = Depends(verify_token)):
        if permission not in user_info.get('permissions', []):
            raise HTTPException(
                status_code=403, 
                detail=f"Permission required: {permission}"
            )
        return user_info
    return permission_checker

# FastAPI app
app = FastAPI(
    title="SentinelBERT NLP Service (Simplified)",
    description="Simplified sentiment analysis service for testing",
    version="1.0.0-simple"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class TextAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    user_metadata: Optional[Dict] = None
    include_behavioral_analysis: bool = True
    include_influence_score: bool = True

class SentimentResult(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0)
    negative: float = Field(..., ge=0.0, le=1.0)
    neutral: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

class BehavioralPattern(BaseModel):
    pattern_type: str
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    indicators: List[str]

class TextAnalysisResult(BaseModel):
    text_id: int
    sentiment: SentimentResult
    behavioral_patterns: List[BehavioralPattern]
    influence_score: Optional[float] = None
    language: Optional[str] = None
    processing_time_ms: float

class BatchAnalysisResponse(BaseModel):
    results: List[Dict]
    total_processing_time_ms: float
    model_version: str
    cache_hits: int
    cache_misses: int

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    memory_usage_mb: float
    active_requests: int

# Mock analysis functions
def mock_sentiment_analysis(text: str) -> SentimentResult:
    """Mock sentiment analysis"""
    # Simple rule-based sentiment for testing
    text_lower = text.lower()
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible']
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return SentimentResult(positive=0.7, negative=0.1, neutral=0.2, confidence=0.8)
    elif neg_count > pos_count:
        return SentimentResult(positive=0.1, negative=0.7, neutral=0.2, confidence=0.8)
    else:
        return SentimentResult(positive=0.3, negative=0.3, neutral=0.4, confidence=0.6)

def mock_behavioral_analysis(text: str) -> List[BehavioralPattern]:
    """Mock behavioral pattern analysis"""
    patterns = []
    
    # Check for aggressive language
    aggressive_indicators = ['!', 'CAPS', 'angry', 'fight']
    if any(indicator in text for indicator in aggressive_indicators):
        patterns.append(BehavioralPattern(
            pattern_type="aggressive",
            score=0.6,
            confidence=0.7,
            indicators=["exclamation_marks", "caps_usage"]
        ))
    
    # Check for influence patterns
    influence_indicators = ['follow', 'share', 'retweet', 'like']
    if any(indicator in text.lower() for indicator in influence_indicators):
        patterns.append(BehavioralPattern(
            pattern_type="influence_seeking",
            score=0.5,
            confidence=0.6,
            indicators=["social_engagement_requests"]
        ))
    
    return patterns

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=True,  # Mock
        gpu_available=False,  # No GPU in simplified version
        memory_usage_mb=50.0,  # Mock
        active_requests=0
    )

@app.post("/analyze", response_model=BatchAnalysisResponse)
async def analyze_texts(
    request: TextAnalysisRequest,
    user_info: dict = Depends(require_permission('nlp:analyze'))
):
    """Analyze texts for sentiment and behavioral patterns"""
    start_time = datetime.now()
    
    try:
        results = []
        
        for i, text in enumerate(request.texts):
            # Mock analysis
            sentiment = mock_sentiment_analysis(text)
            behavioral_patterns = mock_behavioral_analysis(text) if request.include_behavioral_analysis else []
            influence_score = 0.5 if request.include_influence_score else None
            
            result = TextAnalysisResult(
                text_id=i,
                sentiment=sentiment,
                behavioral_patterns=behavioral_patterns,
                influence_score=influence_score,
                language="en",  # Mock
                processing_time_ms=10.0  # Mock
            )
            results.append(result.dict())
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BatchAnalysisResponse(
            results=results,
            total_processing_time_ms=total_time,
            model_version="simplified-1.0.0",
            cache_hits=0,
            cache_misses=len(request.texts)
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/sentiment")
async def analyze_sentiment_only(
    request: TextAnalysisRequest,
    user_info: dict = Depends(require_permission('nlp:sentiment'))
):
    """Analyze texts for sentiment only"""
    try:
        results = []
        for text in request.texts:
            sentiment = mock_sentiment_analysis(text)
            results.append(sentiment.dict())
        
        return {
            "results": results,
            "model_version": "simplified-1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_sentiment_only: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@app.get("/models")
async def list_models(
    user_info: dict = Depends(require_permission('admin:models'))
):
    """List available model versions"""
    return {
        "current_version": "simplified-1.0.0",
        "available_versions": ["simplified-1.0.0"],
        "model_info": {
            "type": "mock",
            "description": "Simplified mock model for testing"
        }
    }

@app.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    return {
        "requests_processed": 0,
        "average_processing_time_ms": 10.0,
        "cache_hit_rate": 0.0,
        "model_version": "simplified-1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting simplified NLP service on {host}:{port}")
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )