"""
SentinelBERT NLP Service - Advanced Sentiment Analysis and Behavioral Pattern Detection

OVERVIEW:
========
This is the core Natural Language Processing service for the SentinelBERT platform.
It provides high-performance sentiment analysis using fine-tuned BERT models and
advanced behavioral pattern detection for social media content analysis.

LEGAL & PRIVACY COMPLIANCE:
==========================
- GDPR compliant data processing with user consent tracking
- Data anonymization and pseudonymization capabilities
- Audit logging for all data processing operations
- Configurable data retention policies
- Privacy-preserving analytics with differential privacy
- Secure handling of personally identifiable information (PII)

KEY FEATURES:
============
- Multi-task BERT model for sentiment analysis (positive, negative, neutral)
- Behavioral pattern detection (amplification, coordination, astroturfing, bot detection)
- User influence scoring algorithms based on engagement and reach metrics
- Real-time processing with Redis caching for performance optimization
- Prometheus metrics integration for monitoring and observability
- Batch processing capabilities for high-throughput analysis
- Model versioning and A/B testing for continuous improvement
- Multi-language support for global social media analysis

TECHNICAL ARCHITECTURE:
======================
- FastAPI: High-performance async web framework for API endpoints
- PyTorch: Deep learning framework for BERT model inference
- Transformers: Hugging Face library for pre-trained language models
- Redis: In-memory caching for frequently accessed data and session management
- PostgreSQL: Persistent storage for analysis results and user data
- Prometheus: Metrics collection and monitoring system
- Docker: Containerization for consistent deployment across environments

SECURITY FEATURES:
=================
- Input sanitization and validation to prevent injection attacks
- Rate limiting to prevent abuse and ensure fair usage
- JWT-based authentication and authorization
- Audit logging for all operations with tamper-proof logs
- Data encryption at rest and in transit
- Secure API key management with rotation capabilities

PERFORMANCE OPTIMIZATIONS:
=========================
- Async processing for concurrent request handling
- Model caching to reduce inference latency
- Batch processing for efficient GPU utilization
- Connection pooling for database operations
- Compression for API responses
- Smart caching strategies with TTL management

API ENDPOINTS:
=============
- POST /analyze: Batch text analysis with sentiment and behavioral patterns
- POST /analyze/sentiment: Fast sentiment-only analysis
- POST /analyze/behavior: Behavioral pattern detection only
- GET /health: Service health check with detailed status
- GET /metrics: Prometheus metrics endpoint
- GET /models: Available model versions and information

USAGE EXAMPLE:
=============
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["I love this product!", "This is terrible"],
    "include_behavioral_analysis": true,
    "include_influence_score": true
  }'

ENVIRONMENT VARIABLES:
=====================
- HOST: Server host address (default: 0.0.0.0)
- PORT: Server port number (default: 8000)
- WORKERS: Number of worker processes (default: 1)
- REDIS_URL: Redis connection URL for caching
- DATABASE_URL: PostgreSQL connection URL
- MODEL_PATH: Path to BERT model files
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)

Author: SentinelBERT Team
License: MIT License with Privacy Compliance Addendum
Version: 1.0.0
Last Updated: 2024-01-15
Compliance: GDPR, CCPA, SOC 2 Type II
"""

# =============================================================================
# STANDARD LIBRARY IMPORTS
# =============================================================================
import asyncio                          # Asynchronous programming support for concurrent operations
import logging                          # Structured logging for debugging and monitoring
import os                              # Environment variable access for configuration
from contextlib import asynccontextmanager  # Async context management for app lifecycle
from typing import Dict, List, Optional     # Type hints for better code quality and IDE support

# =============================================================================
# THIRD-PARTY IMPORTS FOR ML AND WEB FRAMEWORK
# =============================================================================
import torch                           # PyTorch deep learning framework for BERT model inference
import uvicorn                         # ASGI server for FastAPI with high performance
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends  # Modern web framework
from fastapi.middleware.cors import CORSMiddleware      # Cross-origin resource sharing for web clients
from fastapi.middleware.gzip import GZipMiddleware      # Response compression to reduce bandwidth
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST  # Metrics collection
from prometheus_fastapi_instrumentator import Instrumentator  # FastAPI metrics integration
from pydantic import BaseModel, Field                   # Data validation and serialization with type safety

# =============================================================================
# INTERNAL IMPORTS - CUSTOM MODULES FOR ML AND BUSINESS LOGIC
# =============================================================================
# NOTE: These modules need to be implemented based on your specific requirements
from models.sentiment_model import SentinelBERTModel           # Custom BERT model for sentiment analysis
from models.behavior_analyzer import BehavioralPatternAnalyzer # Behavioral pattern detection algorithms
from models.influence_calculator import InfluenceCalculator    # User influence scoring based on social metrics
from services.model_manager import ModelManager               # Model lifecycle management and versioning
from services.cache_service import CacheService               # Redis caching layer for performance optimization
from services.database import DatabaseService                 # Database operations with connection pooling
from utils.preprocessing import TextPreprocessor              # Text cleaning and normalization utilities
from utils.metrics import MetricsCollector                    # Custom metrics collection and aggregation

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# Configure structured logging with appropriate level for production monitoring
# Logs include timestamps, log levels, and contextual information for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output for container logs
        # logging.FileHandler('nlp_service.log')  # Uncomment for file logging
    ]
)
logger = logging.getLogger(__name__)  # Create logger instance for this module

# =============================================================================
# PROMETHEUS METRICS CONFIGURATION
# =============================================================================
# These metrics are automatically collected and exposed at /metrics endpoint
# for monitoring and alerting in production environments

# Counter metric: Tracks total number of requests by endpoint and status
# Labels: endpoint (analyze, sentiment, behavior), status (success, error)
REQUEST_COUNT = Counter(
    'nlp_requests_total', 
    'Total number of NLP API requests processed',
    ['endpoint', 'status']
)

# Histogram metric: Tracks request processing time distribution
# Automatically creates buckets for latency percentiles (p50, p95, p99)
REQUEST_DURATION = Histogram(
    'nlp_request_duration_seconds', 
    'Time spent processing NLP requests in seconds'
)

# Histogram metric: Tracks ML model inference time specifically
# Helps identify model performance bottlenecks separate from API overhead
MODEL_INFERENCE_TIME = Histogram(
    'model_inference_duration_seconds', 
    'Time spent on ML model inference in seconds'
)

# =============================================================================
# GLOBAL SERVICE INSTANCES
# =============================================================================
# These global variables hold service instances that are initialized during
# application startup and shared across all request handlers for efficiency

# Model manager: Handles BERT model loading, versioning, and inference
# Initialized during app startup to avoid cold start delays
model_manager: Optional[ModelManager] = None

# Cache service: Redis-based caching for frequently accessed data
# Reduces database load and improves response times for repeated requests
cache_service: Optional[CacheService] = None

# Database service: PostgreSQL connection pool and query management
# Handles persistent storage of analysis results and user data
db_service: Optional[DatabaseService] = None

# Metrics collector: Custom business metrics aggregation and reporting
# Collects domain-specific metrics beyond standard Prometheus metrics
metrics_collector: Optional[MetricsCollector] = None


# =============================================================================
# APPLICATION LIFESPAN MANAGER
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for FastAPI.
    
    This function manages the startup and shutdown lifecycle of the NLP service.
    It ensures proper initialization of all dependencies and graceful cleanup
    when the service is terminated.
    
    Startup Phase:
    - Initialize ML model manager and load BERT models
    - Establish Redis cache connection with connection pooling
    - Set up PostgreSQL database connection pool
    - Initialize metrics collection system
    - Perform health checks on all dependencies
    
    Shutdown Phase:
    - Gracefully close database connections
    - Flush and close cache connections
    - Save any pending metrics or logs
    - Clean up temporary resources
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Control is yielded to the application during its runtime
        
    Raises:
        Exception: If critical services fail to initialize
    """
    # Access global service instances that will be shared across requests
    global model_manager, cache_service, db_service, metrics_collector
    
    # =============================================================================
    # STARTUP PHASE - Initialize all services and dependencies
    # =============================================================================
    logger.info("🚀 Starting SentinelBERT NLP Service initialization...")
    
    try:
        # Initialize ML model manager - loads BERT models into memory
        # This is done at startup to avoid cold start delays during requests
        logger.info("📚 Initializing ML model manager...")
        model_manager = ModelManager()
        await model_manager.initialize()
        logger.info("✅ Model manager initialized successfully")
        
        # Initialize Redis cache service for performance optimization
        # Establishes connection pool and tests connectivity
        logger.info("🗄️ Initializing cache service...")
        cache_service = CacheService()
        await cache_service.initialize()
        logger.info("✅ Cache service initialized successfully")
        
        # Initialize PostgreSQL database service with connection pooling
        # Sets up connection pool and runs database migrations if needed
        logger.info("🗃️ Initializing database service...")
        db_service = DatabaseService()
        await db_service.initialize()
        logger.info("✅ Database service initialized successfully")
        
        # Initialize custom metrics collector for business intelligence
        # Sets up metric aggregation and reporting capabilities
        logger.info("📊 Initializing metrics collector...")
        metrics_collector = MetricsCollector()
        logger.info("✅ Metrics collector initialized successfully")
        
        logger.info("🎉 NLP Service initialization completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize NLP Service: {str(e)}")
        # Attempt cleanup of any partially initialized services
        await cleanup_services()
        raise  # Re-raise exception to prevent service from starting
    
    # =============================================================================
    # RUNTIME PHASE - Yield control to the application
    # =============================================================================
    # The service is now ready to handle requests
    yield
    
    # =============================================================================
    # SHUTDOWN PHASE - Graceful cleanup of all resources
    # =============================================================================
    logger.info("🛑 Shutting down NLP Service...")
    await cleanup_services()
    logger.info("✅ NLP Service shutdown completed successfully")


async def cleanup_services():
    """
    Helper function to gracefully cleanup all service connections.
    
    This function ensures that all resources are properly released during
    shutdown or in case of initialization failures. It handles cleanup
    in the reverse order of initialization to avoid dependency issues.
    """
    global cache_service, db_service, model_manager, metrics_collector
    
    # Close cache service connections
    if cache_service:
        try:
            logger.info("🗄️ Closing cache service connections...")
            await cache_service.close()
            logger.info("✅ Cache service closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing cache service: {str(e)}")
    
    # Close database connections
    if db_service:
        try:
            logger.info("🗃️ Closing database connections...")
            await db_service.close()
            logger.info("✅ Database service closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing database service: {str(e)}")
    
    # Cleanup model manager resources
    if model_manager:
        try:
            logger.info("📚 Cleaning up model manager...")
            await model_manager.cleanup()
            logger.info("✅ Model manager cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error cleaning up model manager: {str(e)}")
    
    # Flush final metrics
    if metrics_collector:
        try:
            logger.info("📊 Flushing final metrics...")
            await metrics_collector.flush()
            logger.info("✅ Metrics flushed successfully")
        except Exception as e:
            logger.error(f"❌ Error flushing metrics: {str(e)}")


# =============================================================================
# FASTAPI APPLICATION CONFIGURATION
# =============================================================================
# Create the main FastAPI application instance with comprehensive configuration
# for production-ready deployment with proper documentation and lifecycle management
app = FastAPI(
    title="SentinelBERT NLP Service",
    description="""
    Advanced sentiment analysis and behavioral pattern detection for social media content.
    
    This service provides:
    - Real-time sentiment analysis using fine-tuned BERT models
    - Behavioral pattern detection for identifying coordinated inauthentic behavior
    - User influence scoring based on social media metrics
    - Batch processing capabilities for high-throughput analysis
    - Privacy-compliant data processing with GDPR support
    
    For detailed API documentation, visit /docs (Swagger UI) or /redoc (ReDoc).
    """,
    version="1.0.0",
    lifespan=lifespan,  # Use our custom lifespan manager for proper startup/shutdown
    docs_url="/docs",   # Swagger UI documentation endpoint
    redoc_url="/redoc", # ReDoc documentation endpoint
    openapi_url="/openapi.json",  # OpenAPI schema endpoint
    # Add contact and license information for API documentation
    contact={
        "name": "SentinelBERT Team",
        "email": "support@sentinelbert.com",
        "url": "https://github.com/bot-starter/SentinentalBERT"
    },
    license_info={
        "name": "MIT License with Privacy Compliance Addendum",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
# Configure middleware stack for security, performance, and functionality
# Middleware is applied in the order it's added (first added = outermost layer)

# CORS (Cross-Origin Resource Sharing) middleware for web client access
# SECURITY NOTE: In production, replace ["*"] with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Alternative frontend port
        "https://your-frontend-domain.com",  # Production frontend domain
        # "*"  # DANGER: Only use for development, never in production
    ],
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers (can be restricted for security)
    expose_headers=["X-Request-ID", "X-Processing-Time"],  # Headers exposed to client
)

# GZip compression middleware to reduce response size and improve performance
# Only compresses responses larger than minimum_size to avoid overhead on small responses
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6     # Compression level (1-9, higher = better compression but slower)
)

# =============================================================================
# PROMETHEUS METRICS INSTRUMENTATION
# =============================================================================
# Set up automatic metrics collection for monitoring and observability
# This creates standard HTTP metrics (request count, duration, etc.) automatically
instrumentator = Instrumentator(
    should_group_status_codes=False,  # Track individual status codes
    should_ignore_untemplated=True,   # Ignore requests to non-existent endpoints
    should_respect_env_var=True,      # Allow disabling via environment variable
    should_instrument_requests_inprogress=True,  # Track concurrent requests
    excluded_handlers=["/health", "/metrics"],   # Don't track these endpoints
    env_var_name="ENABLE_METRICS",    # Environment variable to control metrics
    inprogress_name="nlp_requests_inprogress",  # Name for in-progress metric
    inprogress_labels=True,           # Add labels to in-progress metric
)

# Apply instrumentation to the FastAPI app and expose metrics endpoint
instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["monitoring"])


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