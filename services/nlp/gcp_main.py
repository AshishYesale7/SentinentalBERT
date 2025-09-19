"""
SentinelBERT NLP Service - GCP Integration Version
Enhanced with Vertex AI, Pub/Sub, and BigQuery integration

This version integrates with Google Cloud Platform services:
- Vertex AI for model hosting and inference
- Pub/Sub for message processing
- BigQuery for analytics storage
- Cloud Storage for model artifacts
- Secret Manager for configuration
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import pubsub_v1
from google.cloud import secretmanager
from google.cloud import storage
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PROJECT_ID = os.environ.get('GCP_PROJECT')
REGION = os.environ.get('VERTEX_AI_REGION', 'us-central1')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
PUBSUB_SUBSCRIPTION = os.environ.get('PUBSUB_SUBSCRIPTION', f'nlp-analysis-sub-{ENVIRONMENT}')
BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET', f'sentinelbert_{ENVIRONMENT}')
MODEL_BUCKET = os.environ.get('MODEL_BUCKET', f'{PROJECT_ID}-sentinelbert-models-{ENVIRONMENT}')

# Initialize GCP clients
aiplatform.init(project=PROJECT_ID, location=REGION)
bigquery_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
secret_client = secretmanager.SecretManagerServiceClient()
subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

# Prometheus metrics
REQUEST_COUNT = Counter('nlp_requests_total', 'Total NLP requests', ['endpoint', 'status'])
REQUEST_DURATION = Histogram('nlp_request_duration_seconds', 'Request duration')
VERTEX_AI_CALLS = Counter('vertex_ai_calls_total', 'Total Vertex AI API calls', ['model', 'status'])
PUBSUB_MESSAGES = Counter('pubsub_messages_total', 'Total Pub/Sub messages', ['topic', 'status'])

# Global services
vertex_ai_model = None
pubsub_subscription_path = None


class VertexAIModelManager:
    """Manages Vertex AI model endpoints and predictions"""
    
    def __init__(self):
        self.sentiment_endpoint = None
        self.behavior_endpoint = None
        self.influence_endpoint = None
    
    async def initialize(self):
        """Initialize Vertex AI model endpoints"""
        try:
            # Get model endpoint IDs from Secret Manager
            sentiment_endpoint_id = await self.get_secret(f'sentiment-model-endpoint-{ENVIRONMENT}')
            behavior_endpoint_id = await self.get_secret(f'behavior-model-endpoint-{ENVIRONMENT}')
            influence_endpoint_id = await self.get_secret(f'influence-model-endpoint-{ENVIRONMENT}')
            
            # Initialize endpoints
            if sentiment_endpoint_id:
                self.sentiment_endpoint = aiplatform.Endpoint(sentiment_endpoint_id)
                logger.info(f"Initialized sentiment model endpoint: {sentiment_endpoint_id}")
            
            if behavior_endpoint_id:
                self.behavior_endpoint = aiplatform.Endpoint(behavior_endpoint_id)
                logger.info(f"Initialized behavior model endpoint: {behavior_endpoint_id}")
            
            if influence_endpoint_id:
                self.influence_endpoint = aiplatform.Endpoint(influence_endpoint_id)
                logger.info(f"Initialized influence model endpoint: {influence_endpoint_id}")
                
        except Exception as e:
            logger.error(f"Error initializing Vertex AI models: {e}")
            # Fall back to local models if available
            await self.initialize_local_models()
    
    async def get_secret(self, secret_id: str) -> str:
        """Get secret from Secret Manager"""
        try:
            name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
            response = secret_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Could not retrieve secret {secret_id}: {e}")
            return None
    
    async def initialize_local_models(self):
        """Initialize local models as fallback"""
        try:
            # Download models from Cloud Storage if needed
            bucket = storage_client.bucket(MODEL_BUCKET)
            
            # Check if models exist locally, if not download them
            model_files = ['sentiment_model.pt', 'behavior_model.pt', 'influence_model.pt']
            for model_file in model_files:
                local_path = f'/app/models/{model_file}'
                if not os.path.exists(local_path):
                    blob = bucket.blob(f'models/{model_file}')
                    if blob.exists():
                        os.makedirs('/app/models', exist_ok=True)
                        blob.download_to_filename(local_path)
                        logger.info(f"Downloaded {model_file} from Cloud Storage")
            
            logger.info("Local models initialized as fallback")
            
        except Exception as e:
            logger.error(f"Error initializing local models: {e}")
    
    async def predict_sentiment(self, texts: List[str]) -> List[Dict]:
        """Predict sentiment using Vertex AI or local model"""
        try:
            if self.sentiment_endpoint:
                # Use Vertex AI endpoint
                instances = [{"text": text} for text in texts]
                predictions = self.sentiment_endpoint.predict(instances=instances)
                
                VERTEX_AI_CALLS.labels(model='sentiment', status='success').inc()
                
                return [
                    {
                        'positive': pred['positive'],
                        'negative': pred['negative'],
                        'neutral': pred['neutral'],
                        'confidence': pred['confidence']
                    }
                    for pred in predictions.predictions
                ]
            else:
                # Use local model fallback
                return await self.predict_sentiment_local(texts)
                
        except Exception as e:
            VERTEX_AI_CALLS.labels(model='sentiment', status='error').inc()
            logger.error(f"Error in sentiment prediction: {e}")
            # Fall back to local model
            return await self.predict_sentiment_local(texts)
    
    async def predict_sentiment_local(self, texts: List[str]) -> List[Dict]:
        """Local sentiment prediction fallback"""
        # Simplified local prediction - in production, load actual model
        results = []
        for text in texts:
            # Simple rule-based sentiment for fallback
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                results.append({'positive': 0.7, 'negative': 0.1, 'neutral': 0.2, 'confidence': 0.6})
            elif neg_count > pos_count:
                results.append({'positive': 0.1, 'negative': 0.7, 'neutral': 0.2, 'confidence': 0.6})
            else:
                results.append({'positive': 0.2, 'negative': 0.2, 'neutral': 0.6, 'confidence': 0.5})
        
        return results
    
    async def predict_behavior(self, texts: List[str], user_metadata: Dict = None) -> List[Dict]:
        """Predict behavioral patterns"""
        try:
            if self.behavior_endpoint:
                instances = [{"text": text, "metadata": user_metadata or {}} for text in texts]
                predictions = self.behavior_endpoint.predict(instances=instances)
                
                VERTEX_AI_CALLS.labels(model='behavior', status='success').inc()
                
                return predictions.predictions
            else:
                return await self.predict_behavior_local(texts, user_metadata)
                
        except Exception as e:
            VERTEX_AI_CALLS.labels(model='behavior', status='error').inc()
            logger.error(f"Error in behavior prediction: {e}")
            return await self.predict_behavior_local(texts, user_metadata)
    
    async def predict_behavior_local(self, texts: List[str], user_metadata: Dict = None) -> List[Dict]:
        """Local behavior prediction fallback"""
        results = []
        for text in texts:
            # Simple pattern detection
            patterns = []
            
            # Check for amplification patterns
            if any(word in text.lower() for word in ['retweet', 'share', 'spread']):
                patterns.append({
                    'pattern_type': 'amplification',
                    'score': 0.6,
                    'confidence': 0.5,
                    'indicators': ['amplification_keywords']
                })
            
            # Check for coordination patterns
            if len(text.split()) < 10 and any(char in text for char in ['#', '@']):
                patterns.append({
                    'pattern_type': 'coordination',
                    'score': 0.4,
                    'confidence': 0.4,
                    'indicators': ['short_text_with_tags']
                })
            
            results.append(patterns)
        
        return results
    
    async def predict_influence(self, user_metadata: Dict) -> float:
        """Predict user influence score"""
        try:
            if self.influence_endpoint and user_metadata:
                instances = [user_metadata]
                predictions = self.influence_endpoint.predict(instances=instances)
                
                VERTEX_AI_CALLS.labels(model='influence', status='success').inc()
                
                return predictions.predictions[0]['influence_score']
            else:
                return self.calculate_influence_local(user_metadata)
                
        except Exception as e:
            VERTEX_AI_CALLS.labels(model='influence', status='error').inc()
            logger.error(f"Error in influence prediction: {e}")
            return self.calculate_influence_local(user_metadata)
    
    def calculate_influence_local(self, user_metadata: Dict) -> float:
        """Local influence calculation fallback"""
        if not user_metadata:
            return 0.0
        
        # Simple influence calculation based on followers and engagement
        followers = user_metadata.get('followers_count', 0)
        verified = user_metadata.get('verified', False)
        engagement_rate = user_metadata.get('engagement_rate', 0.0)
        
        # Normalize followers (log scale)
        import math
        follower_score = math.log10(max(followers, 1)) / 7  # Max score at 10M followers
        verified_bonus = 0.2 if verified else 0.0
        engagement_score = min(engagement_rate * 10, 1.0)  # Cap at 10% engagement rate
        
        influence_score = (follower_score + verified_bonus + engagement_score) / 3
        return min(influence_score, 1.0)


class PubSubProcessor:
    """Processes Pub/Sub messages for NLP analysis"""
    
    def __init__(self, model_manager: VertexAIModelManager):
        self.model_manager = model_manager
        self.subscription_path = subscriber.subscription_path(PROJECT_ID, PUBSUB_SUBSCRIPTION)
    
    async def start_processing(self):
        """Start processing Pub/Sub messages"""
        try:
            logger.info(f"Starting Pub/Sub processing on {self.subscription_path}")
            
            # Configure subscriber
            flow_control = pubsub_v1.types.FlowControl(max_messages=100)
            
            # Start pulling messages
            streaming_pull_future = subscriber.subscribe(
                self.subscription_path,
                callback=self.process_message,
                flow_control=flow_control
            )
            
            logger.info("Pub/Sub subscriber started")
            
            # Keep the subscriber running
            try:
                streaming_pull_future.result()
            except KeyboardInterrupt:
                streaming_pull_future.cancel()
                
        except Exception as e:
            logger.error(f"Error in Pub/Sub processing: {e}")
    
    def process_message(self, message):
        """Process individual Pub/Sub message"""
        try:
            # Parse message data
            data = json.loads(message.data.decode('utf-8'))
            
            # Process the social media post
            asyncio.create_task(self.analyze_post(data))
            
            # Acknowledge message
            message.ack()
            
            PUBSUB_MESSAGES.labels(topic='nlp-analysis', status='success').inc()
            
        except Exception as e:
            logger.error(f"Error processing Pub/Sub message: {e}")
            message.nack()
            PUBSUB_MESSAGES.labels(topic='nlp-analysis', status='error').inc()
    
    async def analyze_post(self, post_data: Dict):
        """Analyze a social media post"""
        try:
            post_id = post_data.get('post_id')
            content = post_data.get('content', '')
            user_metadata = post_data.get('author_info', {})
            
            if not content:
                logger.warning(f"No content found for post {post_id}")
                return
            
            # Perform sentiment analysis
            sentiment_results = await self.model_manager.predict_sentiment([content])
            sentiment = sentiment_results[0] if sentiment_results else {}
            
            # Perform behavioral analysis
            behavior_results = await self.model_manager.predict_behavior([content], user_metadata)
            behaviors = behavior_results[0] if behavior_results else []
            
            # Calculate influence score
            influence_score = await self.model_manager.predict_influence(user_metadata)
            
            # Prepare analysis result
            analysis_result = {
                'analysis_id': f"{post_id}_{int(datetime.utcnow().timestamp())}",
                'post_id': post_id,
                'model_version': 'vertex-ai-v1',
                'sentiment_score': sentiment.get('positive', 0) - sentiment.get('negative', 0),
                'sentiment_label': self.get_sentiment_label(sentiment),
                'confidence_score': sentiment.get('confidence', 0),
                'emotion_scores': {
                    'anger': sentiment.get('negative', 0) * 0.8,
                    'fear': sentiment.get('negative', 0) * 0.6,
                    'joy': sentiment.get('positive', 0) * 0.9,
                    'sadness': sentiment.get('negative', 0) * 0.7,
                    'surprise': sentiment.get('neutral', 0) * 0.5,
                    'disgust': sentiment.get('negative', 0) * 0.5,
                    'trust': sentiment.get('positive', 0) * 0.7,
                    'anticipation': sentiment.get('positive', 0) * 0.6
                },
                'topics': [],  # TODO: Implement topic extraction
                'keywords': [],  # TODO: Implement keyword extraction
                'analyzed_at': datetime.utcnow().isoformat(),
                'processing_time_ms': 0  # TODO: Track processing time
            }
            
            # Store results in BigQuery
            await self.store_analysis_result(analysis_result)
            
            # Store behavioral patterns if found
            if behaviors:
                await self.store_behavioral_patterns(post_id, behaviors, user_metadata)
            
            # Store influence score
            if influence_score > 0:
                await self.store_influence_score(user_metadata, influence_score)
            
            logger.info(f"Completed analysis for post {post_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
    
    def get_sentiment_label(self, sentiment: Dict) -> str:
        """Convert sentiment scores to label"""
        if not sentiment:
            return 'neutral'
        
        pos = sentiment.get('positive', 0)
        neg = sentiment.get('negative', 0)
        neu = sentiment.get('neutral', 0)
        
        if pos > neg and pos > neu:
            return 'positive'
        elif neg > pos and neg > neu:
            return 'negative'
        else:
            return 'neutral'
    
    async def store_analysis_result(self, result: Dict):
        """Store sentiment analysis result in BigQuery"""
        try:
            table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.sentiment_analysis"
            
            # Insert row
            errors = bigquery_client.insert_rows_json(
                bigquery_client.get_table(table_id),
                [result]
            )
            
            if errors:
                logger.error(f"Error inserting sentiment analysis: {errors}")
            else:
                logger.debug(f"Stored sentiment analysis for post {result['post_id']}")
                
        except Exception as e:
            logger.error(f"Error storing analysis result: {e}")
    
    async def store_behavioral_patterns(self, post_id: str, patterns: List[Dict], user_metadata: Dict):
        """Store behavioral patterns in BigQuery"""
        try:
            table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.behavioral_patterns"
            
            rows = []
            for pattern in patterns:
                row = {
                    'pattern_id': f"{post_id}_{pattern['pattern_type']}_{int(datetime.utcnow().timestamp())}",
                    'author_id': user_metadata.get('id', ''),
                    'platform': 'twitter',  # TODO: Get from post data
                    'pattern_type': pattern['pattern_type'],
                    'pattern_data': pattern,
                    'confidence_score': pattern.get('confidence', 0),
                    'time_window': {
                        'start_date': datetime.utcnow().date().isoformat(),
                        'end_date': datetime.utcnow().date().isoformat()
                    },
                    'detected_at': datetime.utcnow().isoformat(),
                    'is_anomaly': pattern.get('score', 0) > 0.8,
                    'risk_score': pattern.get('score', 0)
                }
                rows.append(row)
            
            if rows:
                errors = bigquery_client.insert_rows_json(
                    bigquery_client.get_table(table_id),
                    rows
                )
                
                if errors:
                    logger.error(f"Error inserting behavioral patterns: {errors}")
                else:
                    logger.debug(f"Stored {len(rows)} behavioral patterns")
                    
        except Exception as e:
            logger.error(f"Error storing behavioral patterns: {e}")
    
    async def store_influence_score(self, user_metadata: Dict, influence_score: float):
        """Store influence score in BigQuery"""
        try:
            table_id = f"{PROJECT_ID}.{BIGQUERY_DATASET}.influence_scores"
            
            row = {
                'author_id': user_metadata.get('id', ''),
                'platform': 'twitter',  # TODO: Get from post data
                'influence_score': influence_score * 100,  # Scale to 0-100
                'reach_score': min(user_metadata.get('followers_count', 0) / 10000, 100),
                'engagement_rate': user_metadata.get('engagement_rate', 0),
                'content_quality_score': 50.0,  # TODO: Calculate
                'network_centrality': 50.0,  # TODO: Calculate
                'follower_quality_score': 50.0,  # TODO: Calculate
                'posting_consistency': 50.0,  # TODO: Calculate
                'topic_authority': [],  # TODO: Calculate
                'calculated_at': datetime.utcnow().isoformat(),
                'calculation_period': {
                    'start_date': datetime.utcnow().date().isoformat(),
                    'end_date': datetime.utcnow().date().isoformat()
                }
            }
            
            errors = bigquery_client.insert_rows_json(
                bigquery_client.get_table(table_id),
                [row]
            )
            
            if errors:
                logger.error(f"Error inserting influence score: {errors}")
            else:
                logger.debug(f"Stored influence score for user {row['author_id']}")
                
        except Exception as e:
            logger.error(f"Error storing influence score: {e}")


# Global instances
model_manager: Optional[VertexAIModelManager] = None
pubsub_processor: Optional[PubSubProcessor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model_manager, pubsub_processor
    
    logger.info("Starting SentinelBERT NLP Service (GCP Version)...")
    
    # Initialize Vertex AI model manager
    model_manager = VertexAIModelManager()
    await model_manager.initialize()
    
    # Initialize Pub/Sub processor
    pubsub_processor = PubSubProcessor(model_manager)
    
    # Start Pub/Sub processing in background
    asyncio.create_task(pubsub_processor.start_processing())
    
    logger.info("NLP Service (GCP Version) initialized successfully")
    
    yield
    
    logger.info("Shutting down NLP Service...")


# FastAPI app
app = FastAPI(
    title="SentinelBERT NLP Service (GCP)",
    description="Advanced sentiment analysis with Google Cloud Platform integration",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


class SentimentResult(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0)
    negative: float = Field(..., ge=0.0, le=1.0)
    neutral: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class TextAnalysisResult(BaseModel):
    text_id: int
    sentiment: SentimentResult
    behavioral_patterns: List[Dict]
    influence_score: Optional[float] = None
    processing_time_ms: float


class BatchAnalysisResponse(BaseModel):
    results: List[TextAnalysisResult]
    total_processing_time_ms: float
    model_version: str


class HealthResponse(BaseModel):
    status: str
    vertex_ai_available: bool
    pubsub_connected: bool
    bigquery_connected: bool


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    vertex_ai_available = model_manager is not None and (
        model_manager.sentiment_endpoint is not None or
        model_manager.behavior_endpoint is not None
    )
    
    return HealthResponse(
        status="healthy",
        vertex_ai_available=vertex_ai_available,
        pubsub_connected=pubsub_processor is not None,
        bigquery_connected=True  # TODO: Add actual check
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Model manager not ready")
    
    return {"status": "ready"}


@app.post("/analyze", response_model=BatchAnalysisResponse)
async def analyze_texts(request: TextAnalysisRequest):
    """Analyze texts for sentiment and behavioral patterns"""
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        results = []
        
        # Analyze sentiment
        sentiment_results = await model_manager.predict_sentiment(request.texts)
        
        # Analyze behavior if requested
        behavior_results = []
        if request.include_behavioral_analysis:
            behavior_results = await model_manager.predict_behavior(
                request.texts, request.user_metadata
            )
        
        # Calculate influence if requested
        influence_score = None
        if request.include_influence_score and request.user_metadata:
            influence_score = await model_manager.predict_influence(request.user_metadata)
        
        # Combine results
        for i, text in enumerate(request.texts):
            sentiment = sentiment_results[i] if i < len(sentiment_results) else {}
            behaviors = behavior_results[i] if i < len(behavior_results) else []
            
            result = TextAnalysisResult(
                text_id=i,
                sentiment=SentimentResult(
                    positive=sentiment.get('positive', 0),
                    negative=sentiment.get('negative', 0),
                    neutral=sentiment.get('neutral', 0),
                    confidence=sentiment.get('confidence', 0)
                ),
                behavioral_patterns=behaviors,
                influence_score=influence_score,
                processing_time_ms=0  # TODO: Track individual processing time
            )
            results.append(result)
        
        total_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        REQUEST_COUNT.labels(endpoint="analyze", status="success").inc()
        REQUEST_DURATION.observe(total_time / 1000)
        
        return BatchAnalysisResponse(
            results=results,
            total_processing_time_ms=total_time,
            model_version="vertex-ai-v1"
        )
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint="analyze", status="error").inc()
        logger.error(f"Error in analyze_texts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # Run server
    uvicorn.run(
        "gcp_main:app",
        host=host,
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )