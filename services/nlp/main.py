"""
SentinelBERT NLP Service - Advanced Sentiment Analysis and Behavioral Pattern Detection

This is the core Natural Language Processing service for the SentinelBERT platform.
It provides high-performance sentiment analysis using fine-tuned BERT models and
advanced behavioral pattern detection for social media content analysis.

Key Features:
- Multi-task BERT model for sentiment analysis
- Behavioral pattern detection (amplification, coordination, astroturfing, etc.)
- User influence scoring algorithms
- Real-time processing with caching
- Prometheus metrics integration
- Batch processing capabilities
- Model versioning and A/B testing

Architecture:
- FastAPI for high-performance async API
- PyTorch for deep learning inference
- Redis for caching and session management
- PostgreSQL for persistent storage
- Prometheus for monitoring and metrics

Privacy & Security:
- Input sanitization and validation
- Rate limiting and authentication
- Audit logging for all operations
- Data anonymization capabilities

Author: SentinelBERT Team
License: MIT
Version: 1.0.0
"""

# Standard library imports
import asyncio                          # Asynchronous programming support
import logging                          # Structured logging
import os                              # Environment variable access
from contextlib import asynccontextmanager  # Async context management
from typing import Dict, List, Optional     # Type hints for better code quality

# Third-party imports for ML and web framework
import torch                           # PyTorch deep learning framework
import uvicorn                         # ASGI server for FastAPI
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends  # Web framework
from fastapi.middleware.cors import CORSMiddleware      # Cross-origin resource sharing
from fastapi.middleware.gzip import GZipMiddleware      # Response compression
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST  # Metrics
from prometheus_fastapi_instrumentator import Instrumentator  # FastAPI metrics integration
from pydantic import BaseModel, Field                   # Data validation and serialization

# Internal imports - custom modules for ML and business logic
from models.sentiment_model import SentinelBERTModel           # Custom BERT model
from models.behavior_analyzer import BehavioralPatternAnalyzer # Behavioral analysis
from models.influence_calculator import InfluenceCalculator    # User influence scoring
from services.model_manager import ModelManager               # Model lifecycle management
from services.cache_service import CacheService               # Redis caching layer
from services.database import DatabaseService                 # Database operations
from utils.preprocessing import TextPreprocessor              # Text cleaning and normalization
from utils.metrics import MetricsCollector                    # Custom metrics collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('nlp_requests_total', 'Total NLP requests', ['endpoint', 'status'])
REQUEST_DURATION = Histogram('nlp_request_duration_seconds', 'Request duration')
MODEL_INFERENCE_TIME = Histogram('model_inference_duration_seconds', 'Model inference time')

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

# Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


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
    results: List[TextAnalysisResult]
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
    cache_svc: CacheService = Depends(get_cache_service)
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
            with MODEL_INFERENCE_TIME.time():
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
        REQUEST_COUNT.labels(endpoint="analyze", status="success").inc()
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
            results=results,
            total_processing_time_ms=total_time,
            model_version=model_mgr.get_current_version(),
            cache_hits=cache_hits,
            cache_misses=cache_misses
        )
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="analyze", status="error").inc()
        logger.error(f"Error in analyze_texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/sentiment")
async def analyze_sentiment_only(
    request: TextAnalysisRequest,
    model_mgr: ModelManager = Depends(get_model_manager)
):
    """Analyze texts for sentiment only (faster endpoint)"""
    try:
        results = await model_mgr.analyze_sentiment_batch(request.texts)
        
        REQUEST_COUNT.labels(endpoint="sentiment", status="success").inc()
        
        return {
            "results": results,
            "model_version": model_mgr.get_current_version()
        }
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="sentiment", status="error").inc()
        logger.error(f"Error in analyze_sentiment_only: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@app.post("/analyze/behavior")
async def analyze_behavior_patterns(
    request: TextAnalysisRequest,
    model_mgr: ModelManager = Depends(get_model_manager)
):
    """Analyze texts for behavioral patterns only"""
    try:
        results = await model_mgr.analyze_behavior_batch(
            request.texts,
            user_metadata=request.user_metadata
        )
        
        REQUEST_COUNT.labels(endpoint="behavior", status="success").inc()
        
        return {
            "results": results,
            "model_version": model_mgr.get_current_version()
        }
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="behavior", status="error").inc()
        logger.error(f"Error in analyze_behavior_patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Behavior analysis failed: {str(e)}")


@app.get("/models")
async def list_models(model_mgr: ModelManager = Depends(get_model_manager)):
    """List available model versions"""
    return {
        "current_version": model_mgr.get_current_version(),
        "available_versions": model_mgr.list_available_versions(),
        "model_info": model_mgr.get_model_info()
    }


@app.post("/models/{version}/load")
async def load_model_version(
    version: str,
    model_mgr: ModelManager = Depends(get_model_manager)
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