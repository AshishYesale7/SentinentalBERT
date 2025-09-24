#!/usr/bin/env python3
"""
InsideOut Viral Detection Service
Tracks viral content propagation and identifies original sources
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="SentinelBERT - Social Media Analytics Dashboard", version="1.0.0")

# Models
class ContentItem(BaseModel):
    id: str
    platform: str
    content: str
    author_id: str
    created_at: datetime
    engagement_count: int = 0
    is_repost: bool = False
    original_post_id: Optional[str] = None
    geographic_data: Optional[Dict] = None

class ViralCluster(BaseModel):
    cluster_id: str
    original_source: ContentItem
    propagation_chain: List[ContentItem]
    viral_score: float
    similarity_threshold: float
    geographic_spread: Dict
    influence_network: Dict

class InfluenceScore(BaseModel):
    user_id: str
    influence_score: float
    follower_count: int
    verification_status: bool
    engagement_rate: float

# Viral Detection Engine
class ViralDetectionEngine:
    def __init__(self):
        self.bert_model = AutoModel.from_pretrained('bert-base-multilingual-cased')
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.similarity_threshold = 0.85
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.bert_model.to(self.device)
        
        # Database connections
        # SECURITY FIX: Use environment variables for database credentials
        import os
        db_password = os.getenv('DB_PASSWORD')
        
        # Make database connection optional for development
        self.pg_conn = None
        self.redis_client = None
        
        if db_password:
            try:
                self.pg_conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'postgres'),
                    database=os.getenv('DB_NAME', 'insideout'),
                    user=os.getenv('DB_USER', 'insideout'),
                    password=db_password,
                    sslmode='prefer'  # Prefer SSL but allow non-SSL for development
                )
                logger.info("PostgreSQL connection established")
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed: {e}. Running in mock mode.")
                self.pg_conn = None
        
        redis_password = os.getenv('REDIS_PASSWORD')
        if redis_password:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'redis'), 
                    port=int(os.getenv('REDIS_PORT', 6379)), 
                    password=redis_password,
                    decode_responses=True,
                    ssl=True if os.getenv('REDIS_SSL', 'false').lower() == 'true' else False
                )
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Running in mock mode.")
                self.redis_client = None
        
        logger.info(f"Viral Detection Engine initialized on {self.device}")
    
    async def detect_viral_content(self, content_batch: List[ContentItem]) -> List[ViralCluster]:
        """
        Detect viral content using BERT embeddings and DBSCAN clustering
        """
        try:
            logger.info(f"Processing {len(content_batch)} content items for viral detection")
            
            # Generate embeddings
            embeddings = await self.generate_embeddings([item.content for item in content_batch])
            
            # Cluster similar content
            cluster_labels = self.cluster_similar_content(embeddings)
            
            # Build propagation chains
            viral_clusters = await self.build_propagation_chains(content_batch, cluster_labels)
            
            # Store results
            await self.store_viral_clusters(viral_clusters)
            
            logger.info(f"Detected {len(viral_clusters)} viral clusters")
            return viral_clusters
            
        except Exception as e:
            logger.error(f"Error in viral detection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Viral detection failed: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate BERT embeddings for content similarity"""
        try:
            # Tokenize texts
            encoded = self.tokenizer(
                texts, 
                padding=True, 
                truncation=True, 
                return_tensors='pt', 
                max_length=512
            )
            
            # Move to device
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.bert_model(**encoded)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def cluster_similar_content(self, embeddings: np.ndarray) -> np.ndarray:
        """Use DBSCAN to cluster similar content"""
        try:
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            distance_matrix = 1 - similarity_matrix
            
            # Apply DBSCAN clustering
            clustering = DBSCAN(
                eps=1-self.similarity_threshold, 
                metric='precomputed', 
                min_samples=2
            )
            cluster_labels = clustering.fit_predict(distance_matrix)
            
            logger.info(f"Found {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)} clusters")
            return cluster_labels
            
        except Exception as e:
            logger.error(f"Error in clustering: {str(e)}")
            raise
    
    async def build_propagation_chains(self, posts: List[ContentItem], clusters: np.ndarray) -> List[ViralCluster]:
        """Build temporal propagation chains for each cluster"""
        try:
            viral_clusters = []
            
            for cluster_id in set(clusters):
                if cluster_id == -1:  # Skip noise points
                    continue
                
                # Get posts in this cluster
                cluster_posts = [posts[i] for i, label in enumerate(clusters) if label == cluster_id]
                
                # Sort by timestamp to find original source
                cluster_posts.sort(key=lambda x: x.created_at)
                
                if len(cluster_posts) < 2:  # Need at least 2 posts for viral content
                    continue
                
                # Calculate viral score
                viral_score = await self.calculate_viral_score(cluster_posts)
                
                # Build geographic spread analysis
                geographic_spread = self.analyze_geographic_spread(cluster_posts)
                
                # Build influence network
                influence_network = await self.build_influence_network(cluster_posts)
                
                viral_cluster = ViralCluster(
                    cluster_id=str(uuid.uuid4()),
                    original_source=cluster_posts[0],
                    propagation_chain=cluster_posts,
                    viral_score=viral_score,
                    similarity_threshold=self.similarity_threshold,
                    geographic_spread=geographic_spread,
                    influence_network=influence_network
                )
                
                viral_clusters.append(viral_cluster)
            
            return viral_clusters
            
        except Exception as e:
            logger.error(f"Error building propagation chains: {str(e)}")
            raise
    
    async def calculate_viral_score(self, posts: List[ContentItem]) -> float:
        """Calculate viral score based on multiple factors"""
        try:
            if not posts:
                return 0.0
            
            # Time-based viral velocity
            time_span = (posts[-1].created_at - posts[0].created_at).total_seconds()
            if time_span == 0:
                time_span = 1
            
            velocity_score = len(posts) / (time_span / 3600)  # Posts per hour
            
            # Engagement-based score
            total_engagement = sum(post.engagement_count for post in posts)
            engagement_score = np.log10(max(total_engagement, 1))
            
            # Platform diversity score
            platforms = set(post.platform for post in posts)
            platform_diversity = len(platforms) / 5.0  # Normalize by max expected platforms
            
            # Geographic spread score
            unique_locations = len(set(
                str(post.geographic_data) for post in posts 
                if post.geographic_data
            ))
            geographic_score = min(unique_locations / 10.0, 1.0)  # Normalize
            
            # Combined viral score
            viral_score = (
                velocity_score * 0.3 +
                engagement_score * 0.3 +
                platform_diversity * 0.2 +
                geographic_score * 0.2
            )
            
            return min(viral_score, 10.0)  # Cap at 10.0
            
        except Exception as e:
            logger.error(f"Error calculating viral score: {str(e)}")
            return 0.0
    
    def analyze_geographic_spread(self, posts: List[ContentItem]) -> Dict:
        """Analyze geographic spread of viral content"""
        try:
            geographic_data = {
                'total_locations': 0,
                'states_covered': set(),
                'cities_covered': set(),
                'spread_velocity': 0.0,
                'concentration_index': 0.0
            }
            
            locations = []
            for post in posts:
                if post.geographic_data:
                    locations.append(post.geographic_data)
                    if 'state' in post.geographic_data:
                        geographic_data['states_covered'].add(post.geographic_data['state'])
                    if 'city' in post.geographic_data:
                        geographic_data['cities_covered'].add(post.geographic_data['city'])
            
            geographic_data['total_locations'] = len(locations)
            geographic_data['states_covered'] = list(geographic_data['states_covered'])
            geographic_data['cities_covered'] = list(geographic_data['cities_covered'])
            
            # Calculate spread velocity (locations per hour)
            if len(posts) > 1:
                time_span = (posts[-1].created_at - posts[0].created_at).total_seconds()
                if time_span > 0:
                    geographic_data['spread_velocity'] = len(locations) / (time_span / 3600)
            
            return geographic_data
            
        except Exception as e:
            logger.error(f"Error analyzing geographic spread: {str(e)}")
            return {}
    
    async def build_influence_network(self, posts: List[ContentItem]) -> Dict:
        """Build influence network for viral content"""
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes (users) with influence scores
            user_scores = await self.get_user_influence_scores([post.author_id for post in posts])
            
            for user_id, score_data in user_scores.items():
                G.add_node(user_id, **score_data)
            
            # Add edges (reposts/shares)
            for post in posts:
                if post.is_repost and post.original_post_id:
                    # Find original author
                    original_author = None
                    for p in posts:
                        if p.id == post.original_post_id:
                            original_author = p.author_id
                            break
                    
                    if original_author:
                        weight = self.calculate_interaction_weight(post)
                        G.add_edge(original_author, post.author_id, weight=weight)
            
            # Calculate network metrics
            network_metrics = {
                'total_nodes': G.number_of_nodes(),
                'total_edges': G.number_of_edges(),
                'density': nx.density(G),
                'key_amplifiers': self.find_key_amplifiers(G, posts)
            }
            
            return network_metrics
            
        except Exception as e:
            logger.error(f"Error building influence network: {str(e)}")
            return {}
    
    async def get_user_influence_scores(self, user_ids: List[str]) -> Dict:
        """Get influence scores for users"""
        try:
            scores = {}
            
            # Return mock data if no database connection
            if not self.pg_conn:
                return {user_id: {'follower_count': 1000, 'verification_status': False, 'influence_score': 0.5} for user_id in user_ids}
            
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, follower_count, verification_status, influence_score
                    FROM user_profiles 
                    WHERE id = ANY(%s)
                """, (user_ids,))
                
                for row in cursor.fetchall():
                    scores[row['id']] = {
                        'follower_count': row['follower_count'] or 0,
                        'verification_status': row['verification_status'] or False,
                        'influence_score': row['influence_score'] or 0.0
                    }
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting user influence scores: {str(e)}")
            return {}
    
    def calculate_interaction_weight(self, post: ContentItem) -> float:
        """Calculate weight of interaction based on engagement"""
        base_weight = 1.0
        engagement_factor = np.log10(max(post.engagement_count, 1)) / 10.0
        return base_weight + engagement_factor
    
    def find_key_amplifiers(self, graph: nx.DiGraph, posts: List[ContentItem]) -> List[Dict]:
        """Find key users who amplified the content"""
        try:
            amplifiers = []
            
            # Calculate centrality measures
            if graph.number_of_nodes() > 0:
                betweenness = nx.betweenness_centrality(graph)
                pagerank = nx.pagerank(graph)
                
                for node in graph.nodes():
                    node_data = graph.nodes[node]
                    amplifier_data = {
                        'user_id': node,
                        'influence_score': node_data.get('influence_score', 0.0),
                        'betweenness_centrality': betweenness.get(node, 0.0),
                        'pagerank_score': pagerank.get(node, 0.0),
                        'follower_count': node_data.get('follower_count', 0)
                    }
                    amplifiers.append(amplifier_data)
                
                # Sort by combined influence
                amplifiers.sort(
                    key=lambda x: x['influence_score'] * x['pagerank_score'], 
                    reverse=True
                )
            
            return amplifiers[:10]  # Top 10 amplifiers
            
        except Exception as e:
            logger.error(f"Error finding key amplifiers: {str(e)}")
            return []
    
    async def store_viral_clusters(self, clusters: List[ViralCluster]):
        """Store viral clusters in database"""
        try:
            # Skip storage if no database connection
            if not self.pg_conn:
                logger.info(f"Skipping storage of {len(clusters)} viral clusters (no database connection)")
                return
            
            with self.pg_conn.cursor() as cursor:
                for cluster in clusters:
                    # Insert viral cluster
                    cursor.execute("""
                        INSERT INTO viral_clusters 
                        (id, cluster_hash, original_post_id, similarity_threshold, 
                         viral_score, first_detected_at, total_posts, geographic_spread)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (cluster_hash) DO UPDATE SET
                        viral_score = EXCLUDED.viral_score,
                        last_updated_at = CURRENT_TIMESTAMP,
                        total_posts = EXCLUDED.total_posts
                    """, (
                        cluster.cluster_id,
                        hash(cluster.original_source.content),
                        cluster.original_source.id,
                        cluster.similarity_threshold,
                        cluster.viral_score,
                        cluster.original_source.created_at,
                        len(cluster.propagation_chain),
                        json.dumps(cluster.geographic_spread)
                    ))
                    
                    # Insert propagation chain
                    for level, post in enumerate(cluster.propagation_chain):
                        cursor.execute("""
                            INSERT INTO content_propagation
                            (cluster_id, post_id, author_id, platform, 
                             propagation_level, propagation_timestamp, reach_estimate)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (cluster_id, post_id) DO NOTHING
                        """, (
                            cluster.cluster_id,
                            post.id,
                            post.author_id,
                            post.platform,
                            level,
                            post.created_at,
                            post.engagement_count
                        ))
                
                if self.pg_conn:
                    self.pg_conn.commit()
                logger.info(f"Stored {len(clusters)} viral clusters")
                
        except Exception as e:
            logger.error(f"Error storing viral clusters: {str(e)}")
            if self.pg_conn:
                self.pg_conn.rollback()
            raise

# Initialize global engine
viral_engine = ViralDetectionEngine()

# API Endpoints
@app.post("/detect-viral", response_model=List[ViralCluster])
async def detect_viral_content(content_items: List[ContentItem]):
    """Detect viral content from a batch of posts"""
    return await viral_engine.detect_viral_content(content_items)

@app.get("/viral-clusters/{cluster_id}", response_model=ViralCluster)
async def get_viral_cluster(cluster_id: str):
    """Get details of a specific viral cluster"""
    try:
        with viral_engine.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM viral_clusters WHERE id = %s
            """, (cluster_id,))
            
            cluster_data = cursor.fetchone()
            if not cluster_data:
                raise HTTPException(status_code=404, detail="Viral cluster not found")
            
            # Get propagation chain
            cursor.execute("""
                SELECT * FROM content_propagation 
                WHERE cluster_id = %s 
                ORDER BY propagation_level
            """, (cluster_id,))
            
            propagation_data = cursor.fetchall()
            
            # Build response (simplified for example)
            return {
                "cluster_id": cluster_data['id'],
                "viral_score": cluster_data['viral_score'],
                "total_posts": len(propagation_data),
                "geographic_spread": cluster_data['geographic_spread']
            }
            
    except Exception as e:
        logger.error(f"Error getting viral cluster: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "viral-detection",
        "timestamp": datetime.utcnow(),
        "device": str(viral_engine.device)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)