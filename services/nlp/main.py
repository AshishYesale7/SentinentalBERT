"""
SentinelBERT NLP Service - Simplified Sentiment Analysis and Behavioral Pattern Detection

This is a simplified version of the SentinelBERT NLP service that provides:
- BERT-based sentiment analysis
- Basic behavioral pattern detection
- User influence scoring
- REST API with FastAPI
- Cross-platform compatibility (Linux/macOS)

Author: SentinelBERT Team
License: MIT
Version: 1.0.0-simplified
"""

# Standard library imports
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

# Third-party imports
import torch
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
import jwt
import hashlib
import hmac

# Internal imports
from models.sentiment_model import SentinelBERTModel
from models.behavior_analyzer import BehavioralPatternAnalyzer
from models.influence_calculator import InfluenceCalculator
from services.model_manager import ModelManager
from services.cache_service import CacheService
from services.database import DatabaseService
from utils.preprocessing import TextPreprocessor
from utils.metrics import MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SECURITY FIX: Add authentication
security = HTTPBearer()
JWT_SECRET = os.getenv('JWT_SECRET', 'insecure-default-change-in-production')
if JWT_SECRET == 'insecure-default-change-in-production':
    logger.warning("⚠️  Using default JWT secret - CHANGE IN PRODUCTION!")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for authentication"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        officer_id = payload.get('officer_id')
        if not officer_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing officer_id")
        
        # Check token expiration
        import time
        if payload.get('exp', 0) < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return {
            'officer_id': officer_id,
            'role': payload.get('role', 'user'),
            'permissions': payload.get('permissions', [])
        }
    except jwt.PyJWTError:
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

# Simplified metrics (avoid conflicts)
try:
    REQUEST_COUNT = Counter('nlp_requests_total', 'Total NLP requests', ['endpoint', 'status'])
    REQUEST_DURATION = Histogram('nlp_request_duration_seconds', 'Request duration')
    MODEL_INFERENCE_TIME = Histogram('model_inference_duration_seconds', 'Model inference time')
except ValueError:
    # Metrics already exist, use existing ones
    from prometheus_client import REGISTRY
    REQUEST_COUNT = None
    REQUEST_DURATION = None
    MODEL_INFERENCE_TIME = None

# Global services
model_manager: Optional[ModelManager] = None
cache_service: Optional[CacheService] = None
db_service: Optional[DatabaseService] = None
metrics_collector: Optional[MetricsCollector] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model_manager, cache_service, db_service, metrics_collector
    
    logger.info("Starting SentinelBERT NLP Service...")
    
    # Initialize services
    model_manager = ModelManager()
    await model_manager.initialize()
    
    cache_service = CacheService()
    await cache_service.initialize()
    
    db_service = DatabaseService()
    await db_service.initialize()
    
    metrics_collector = MetricsCollector()
    
    logger.info("NLP Service initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down NLP Service...")
    if cache_service:
        await cache_service.close()
    if db_service:
        await db_service.close()
    logger.info("NLP Service shutdown complete")


# FastAPI app
app = FastAPI(
    title="SentinelBERT NLP Service",
    description="Advanced sentiment analysis and behavioral pattern detection for social media content",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Simplified metrics (no instrumentator for now)


# Request/Response Models
class TextAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    user_metadata: Optional[Dict] = None
    include_behavioral_analysis: bool = True
    include_influence_score: bool = True
    model_version: Optional[str] = None


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


# Dependency injection
async def get_model_manager() -> ModelManager:
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return model_manager


async def get_cache_service() -> CacheService:
    if cache_service is None:
        raise HTTPException(status_code=503, detail="Cache service not initialized")
    return cache_service


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    gpu_available = torch.cuda.is_available()
    memory_usage = torch.cuda.memory_allocated() / 1024 / 1024 if gpu_available else 0
    
    return HealthResponse(
        status="healthy",
        model_loaded=model_manager is not None and model_manager.is_loaded(),
        gpu_available=gpu_available,
        memory_usage_mb=memory_usage,
        active_requests=0  # TODO: Implement active request tracking
    )


@app.post("/analyze", response_model=BatchAnalysisResponse)
async def analyze_texts(
    request: TextAnalysisRequest,
    background_tasks: BackgroundTasks,
    model_mgr: ModelManager = Depends(get_model_manager),
    cache_svc: CacheService = Depends(get_cache_service),
    user_info: dict = Depends(require_permission('nlp:analyze'))
):
    """Analyze texts for sentiment and behavioral patterns"""
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Validate input
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        # Check cache for existing results
        cache_results = await cache_svc.get_batch_results(request.texts)
        cache_hits = len([r for r in cache_results if r is not None])
        cache_misses = len(request.texts) - cache_hits
        
        # Process uncached texts
        uncached_texts = [
            (i, text) for i, (text, cached) in enumerate(zip(request.texts, cache_results))
            if cached is None
        ]
        
        results = []
        
        # Process cached results
        for i, (text, cached_result) in enumerate(zip(request.texts, cache_results)):
            if cached_result:
                results.append(cached_result)
        
        # Process uncached texts
        if uncached_texts:
            if MODEL_INFERENCE_TIME:
                with MODEL_INFERENCE_TIME.time():
                    new_results = await model_mgr.analyze_batch(
                        [text for _, text in uncached_texts],
                        include_behavioral=request.include_behavioral_analysis,
                        include_influence=request.include_influence_score,
                        user_metadata=request.user_metadata
                    )
            else:
                new_results = await model_mgr.analyze_batch(
                    [text for _, text in uncached_texts],
                    include_behavioral=request.include_behavioral_analysis,
                    include_influence=request.include_influence_score,
                    user_metadata=request.user_metadata
                )
            
            # Cache new results
            background_tasks.add_task(
                cache_svc.cache_batch_results,
                [text for _, text in uncached_texts],
                new_results
            )
            
            # Merge results
            for (original_idx, _), result in zip(uncached_texts, new_results):
                result.text_id = original_idx
                results.append(result)
        
        # Sort results by original text order
        results.sort(key=lambda x: x.text_id)
        
        total_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Update metrics
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="analyze", status="success").inc()
        if REQUEST_DURATION:
            REQUEST_DURATION.observe(total_time / 1000)
        
        # Log metrics
        background_tasks.add_task(
            metrics_collector.record_batch_analysis,
            len(request.texts),
            total_time,
            cache_hits,
            cache_misses
        )
        
        return BatchAnalysisResponse(
            results=[result.to_dict() for result in results],
            total_processing_time_ms=total_time,
            model_version=model_mgr.get_current_version(),
            cache_hits=cache_hits,
            cache_misses=cache_misses
        )
        
    except Exception as e:
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="analyze", status="error").inc()
        logger.error(f"Error in analyze_texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/sentiment")
async def analyze_sentiment_only(
    request: TextAnalysisRequest,
    model_mgr: ModelManager = Depends(get_model_manager),
    user_info: dict = Depends(require_permission('nlp:sentiment'))
):
    """Analyze texts for sentiment only (faster endpoint)"""
    try:
        results = await model_mgr.analyze_sentiment_batch(request.texts)
        
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="sentiment", status="success").inc()
        
        return {
            "results": results,
            "model_version": model_mgr.get_current_version()
        }
        
    except Exception as e:
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="sentiment", status="error").inc()
        logger.error(f"Error in analyze_sentiment_only: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@app.post("/analyze/behavior")
async def analyze_behavior_patterns(
    request: TextAnalysisRequest,
    model_mgr: ModelManager = Depends(get_model_manager),
    user_info: dict = Depends(require_permission('nlp:behavior'))
):
    """Analyze texts for behavioral patterns only"""
    try:
        results = await model_mgr.analyze_behavior_batch(
            request.texts,
            user_metadata=request.user_metadata
        )
        
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="behavior", status="success").inc()
        
        return {
            "results": results,
            "model_version": model_mgr.get_current_version()
        }
        
    except Exception as e:
        if REQUEST_COUNT:
            REQUEST_COUNT.labels(endpoint="behavior", status="error").inc()
        logger.error(f"Error in analyze_behavior_patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Behavior analysis failed: {str(e)}")


@app.get("/models")
async def list_models(
    model_mgr: ModelManager = Depends(get_model_manager),
    user_info: dict = Depends(require_permission('admin:models'))
):
    """List available model versions"""
    return {
        "current_version": model_mgr.get_current_version(),
        "available_versions": model_mgr.list_available_versions(),
        "model_info": model_mgr.get_model_info()
    }


@app.post("/models/{version}/load")
async def load_model_version(
    version: str,
    model_mgr: ModelManager = Depends(get_model_manager),
    user_info: dict = Depends(require_permission('admin:models'))
):
    """Load a specific model version"""
    try:
        await model_mgr.load_version(version)
        return {"message": f"Model version {version} loaded successfully"}
    except Exception as e:
        logger.error(f"Error loading model version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    if metrics_collector:
        stats = await metrics_collector.get_stats()
        return stats
    return {"error": "Metrics collector not available"}


if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    
    # Run server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        access_log=True,
        log_level="info"
    )