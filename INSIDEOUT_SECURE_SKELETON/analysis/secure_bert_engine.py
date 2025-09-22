"""
InsideOut Platform - Secure BERT Analysis Engine
Implements secure pattern detection, regional analysis, and chronological analysis
"""

import asyncio
import logging
import numpy as np
import torch
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer
import geopy.distance
from geopy.geocoders import Nominatim
import pandas as pd
from collections import defaultdict, Counter
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analysis that can be performed"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PATTERN_DETECTION = "pattern_detection"
    VIRAL_DETECTION = "viral_detection"
    INFLUENCE_ANALYSIS = "influence_analysis"
    GEOGRAPHIC_ANALYSIS = "geographic_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    NETWORK_ANALYSIS = "network_analysis"

class PatternType(Enum):
    """Types of patterns that can be detected"""
    COORDINATED_BEHAVIOR = "coordinated_behavior"
    VIRAL_CONTENT = "viral_content"
    INFLUENCE_CAMPAIGN = "influence_campaign"
    MISINFORMATION = "misinformation"
    HATE_SPEECH = "hate_speech"
    TERRORIST_CONTENT = "terrorist_content"
    CRIMINAL_ACTIVITY = "criminal_activity"

@dataclass
class SocialMediaPost:
    """Social media post data structure"""
    post_id: str
    platform: str
    author_id: str
    author_username: str
    content: str
    timestamp: datetime
    location: Optional[Dict] = None  # {'lat': float, 'lng': float, 'place': str}
    engagement: Optional[Dict] = None  # {'likes': int, 'shares': int, 'comments': int}
    metadata: Optional[Dict] = None
    language: Optional[str] = None

@dataclass
class AnalysisScope:
    """Defines the scope of analysis within legal boundaries"""
    warrant_id: str
    geographic_bounds: Dict  # Geographic limitations from warrant
    temporal_bounds: Dict    # Time range limitations
    platform_scope: List[str]  # Allowed platforms
    content_types: List[str]    # Allowed content types
    keywords: List[str]         # Specific keywords to analyze
    legal_constraints: List[str]  # Legal constraints to observe

@dataclass
class PatternMatch:
    """Detected pattern match"""
    pattern_id: str
    pattern_type: PatternType
    confidence_score: float
    posts: List[SocialMediaPost]
    similarity_scores: List[float]
    geographic_spread: Dict
    temporal_spread: Dict
    influence_metrics: Dict
    evidence_strength: float

@dataclass
class GeographicCluster:
    """Geographic cluster of posts"""
    cluster_id: str
    center_location: Dict  # {'lat': float, 'lng': float}
    radius_km: float
    posts: List[SocialMediaPost]
    dominant_patterns: List[PatternMatch]
    influence_score: float
    population_density: Optional[float] = None

@dataclass
class TemporalPattern:
    """Temporal pattern in content"""
    pattern_id: str
    time_range: Dict  # {'start': datetime, 'end': datetime}
    posts: List[SocialMediaPost]
    pattern_evolution: List[Dict]  # How pattern changes over time
    viral_acceleration: float
    peak_activity: datetime
    decay_rate: float

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    analysis_id: str
    warrant_id: str
    analysis_type: AnalysisType
    scope: AnalysisScope
    patterns: List[PatternMatch]
    geographic_clusters: List[GeographicCluster]
    temporal_patterns: List[TemporalPattern]
    confidence_scores: Dict[str, float]
    legal_compliance: Dict[str, bool]
    processing_metadata: Dict
    created_at: datetime

class SecureBERTModel:
    """Secure BERT model wrapper with access controls"""
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Security: Track model usage
        self.usage_log = []
        
        logger.info(f"BERT model loaded: {model_name} on {self.device}")
    
    def log_usage(self, warrant_id: str, officer_id: str, analysis_type: str):
        """Log model usage for audit purposes"""
        self.usage_log.append({
            'timestamp': datetime.utcnow(),
            'warrant_id': warrant_id,
            'officer_id': officer_id,
            'analysis_type': analysis_type,
            'model_name': self.model_name
        })
    
    async def generate_embeddings(self, texts: List[str], 
                                warrant_id: str, officer_id: str) -> np.ndarray:
        """Generate BERT embeddings with security logging"""
        self.log_usage(warrant_id, officer_id, "embedding_generation")
        
        embeddings = []
        batch_size = 32
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings)
    
    async def calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity matrix"""
        return cosine_similarity(embeddings)

class LegalScopeValidator:
    """Validates analysis operations against legal scope"""
    
    def __init__(self):
        self.protected_keywords = [
            'religion', 'political', 'protest', 'demonstration',
            'opinion', 'belief', 'criticism', 'dissent'
        ]
    
    async def validate_analysis_scope(self, scope: AnalysisScope) -> Dict[str, bool]:
        """Validate analysis scope against legal constraints"""
        validation_results = {
            'geographic_valid': True,
            'temporal_valid': True,
            'platform_valid': True,
            'content_valid': True,
            'keyword_valid': True,
            'constitutional_compliant': True
        }
        
        # Check temporal bounds
        time_range = scope.temporal_bounds.get('end') - scope.temporal_bounds.get('start')
        if time_range > timedelta(days=365):
            validation_results['temporal_valid'] = False
            logger.warning("Temporal scope exceeds 1 year limit")
        
        # Check for protected speech keywords
        protected_found = any(
            keyword.lower() in [k.lower() for k in scope.keywords]
            for keyword in self.protected_keywords
        )
        if protected_found:
            validation_results['constitutional_compliant'] = False
            logger.warning("Analysis may impact protected speech")
        
        # Check geographic scope reasonableness
        if 'radius_km' in scope.geographic_bounds:
            if scope.geographic_bounds['radius_km'] > 1000:  # 1000km radius
                validation_results['geographic_valid'] = False
                logger.warning("Geographic scope too broad")
        
        return validation_results
    
    async def filter_content_by_scope(self, posts: List[SocialMediaPost], 
                                    scope: AnalysisScope) -> List[SocialMediaPost]:
        """Filter posts to only those within legal scope"""
        filtered_posts = []
        
        for post in posts:
            # Check temporal bounds
            if not self._is_within_temporal_bounds(post, scope.temporal_bounds):
                continue
            
            # Check geographic bounds
            if not self._is_within_geographic_bounds(post, scope.geographic_bounds):
                continue
            
            # Check platform scope
            if post.platform not in scope.platform_scope:
                continue
            
            # Check keyword relevance
            if not self._contains_relevant_keywords(post, scope.keywords):
                continue
            
            filtered_posts.append(post)
        
        logger.info(f"Filtered {len(posts)} posts to {len(filtered_posts)} within scope")
        return filtered_posts
    
    def _is_within_temporal_bounds(self, post: SocialMediaPost, bounds: Dict) -> bool:
        """Check if post is within temporal bounds"""
        return bounds['start'] <= post.timestamp <= bounds['end']
    
    def _is_within_geographic_bounds(self, post: SocialMediaPost, bounds: Dict) -> bool:
        """Check if post is within geographic bounds"""
        if not post.location or not bounds:
            return True  # No location data or bounds
        
        if 'center' in bounds and 'radius_km' in bounds:
            center = (bounds['center']['lat'], bounds['center']['lng'])
            post_location = (post.location['lat'], post.location['lng'])
            distance = geopy.distance.distance(center, post_location).kilometers
            return distance <= bounds['radius_km']
        
        return True
    
    def _contains_relevant_keywords(self, post: SocialMediaPost, keywords: List[str]) -> bool:
        """Check if post contains relevant keywords"""
        if not keywords:
            return True
        
        content_lower = post.content.lower()
        return any(keyword.lower() in content_lower for keyword in keywords)

class PatternDetectionEngine:
    """Advanced pattern detection using BERT embeddings"""
    
    def __init__(self, bert_model: SecureBERTModel):
        self.bert_model = bert_model
        self.similarity_threshold = 0.85
        self.min_cluster_size = 3
    
    async def detect_coordinated_behavior(self, posts: List[SocialMediaPost],
                                        warrant_id: str, officer_id: str) -> List[PatternMatch]:
        """Detect coordinated behavior patterns"""
        if len(posts) < self.min_cluster_size:
            return []
        
        # Generate embeddings
        texts = [post.content for post in posts]
        embeddings = await self.bert_model.generate_embeddings(texts, warrant_id, officer_id)
        
        # Cluster similar content
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=self.min_cluster_size,
            metric='cosine'
        )
        cluster_labels = clustering.fit_predict(embeddings)
        
        patterns = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise cluster
                continue
            
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_posts = [posts[i] for i in cluster_indices]
            
            # Calculate pattern metrics
            pattern = await self._analyze_cluster_pattern(
                cluster_posts, embeddings[cluster_indices], PatternType.COORDINATED_BEHAVIOR
            )
            patterns.append(pattern)
        
        return patterns
    
    async def detect_viral_content(self, posts: List[SocialMediaPost],
                                 warrant_id: str, officer_id: str) -> List[PatternMatch]:
        """Detect viral content patterns"""
        # Sort posts by engagement metrics
        posts_with_engagement = [p for p in posts if p.engagement]
        if len(posts_with_engagement) < self.min_cluster_size:
            return []
        
        # Calculate viral score
        viral_posts = []
        for post in posts_with_engagement:
            viral_score = self._calculate_viral_score(post)
            if viral_score > 0.7:  # Threshold for viral content
                viral_posts.append(post)
        
        if len(viral_posts) < self.min_cluster_size:
            return []
        
        # Generate embeddings for viral posts
        texts = [post.content for post in viral_posts]
        embeddings = await self.bert_model.generate_embeddings(texts, warrant_id, officer_id)
        
        # Find similar viral content
        similarity_matrix = await self.bert_model.calculate_similarity_matrix(embeddings)
        
        patterns = []
        processed = set()
        
        for i, post in enumerate(viral_posts):
            if i in processed:
                continue
            
            # Find similar posts
            similar_indices = np.where(similarity_matrix[i] > self.similarity_threshold)[0]
            if len(similar_indices) >= self.min_cluster_size:
                similar_posts = [viral_posts[j] for j in similar_indices]
                pattern = await self._analyze_cluster_pattern(
                    similar_posts, embeddings[similar_indices], PatternType.VIRAL_CONTENT
                )
                patterns.append(pattern)
                processed.update(similar_indices)
        
        return patterns
    
    async def detect_influence_campaigns(self, posts: List[SocialMediaPost],
                                       warrant_id: str, officer_id: str) -> List[PatternMatch]:
        """Detect influence campaign patterns"""
        # Group posts by author
        author_posts = defaultdict(list)
        for post in posts:
            author_posts[post.author_id].append(post)
        
        # Find authors with suspicious posting patterns
        suspicious_authors = []
        for author_id, author_post_list in author_posts.items():
            if self._is_suspicious_posting_pattern(author_post_list):
                suspicious_authors.append(author_id)
        
        if not suspicious_authors:
            return []
        
        # Analyze content from suspicious authors
        suspicious_posts = []
        for author_id in suspicious_authors:
            suspicious_posts.extend(author_posts[author_id])
        
        # Generate embeddings
        texts = [post.content for post in suspicious_posts]
        embeddings = await self.bert_model.generate_embeddings(texts, warrant_id, officer_id)
        
        # Cluster similar influence content
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=2,  # Lower threshold for influence campaigns
            metric='cosine'
        )
        cluster_labels = clustering.fit_predict(embeddings)
        
        patterns = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:
                continue
            
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_posts = [suspicious_posts[i] for i in cluster_indices]
            
            pattern = await self._analyze_cluster_pattern(
                cluster_posts, embeddings[cluster_indices], PatternType.INFLUENCE_CAMPAIGN
            )
            patterns.append(pattern)
        
        return patterns
    
    async def _analyze_cluster_pattern(self, posts: List[SocialMediaPost],
                                     embeddings: np.ndarray,
                                     pattern_type: PatternType) -> PatternMatch:
        """Analyze a cluster of posts to create pattern match"""
        pattern_id = hashlib.md5(
            ''.join([p.post_id for p in posts]).encode()
        ).hexdigest()[:16]
        
        # Calculate similarity scores
        similarity_matrix = cosine_similarity(embeddings)
        avg_similarity = np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
        
        # Calculate geographic spread
        geographic_spread = self._calculate_geographic_spread(posts)
        
        # Calculate temporal spread
        temporal_spread = self._calculate_temporal_spread(posts)
        
        # Calculate influence metrics
        influence_metrics = self._calculate_influence_metrics(posts)
        
        # Calculate evidence strength
        evidence_strength = self._calculate_evidence_strength(
            posts, avg_similarity, geographic_spread, temporal_spread
        )
        
        return PatternMatch(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            confidence_score=avg_similarity,
            posts=posts,
            similarity_scores=similarity_matrix.flatten().tolist(),
            geographic_spread=geographic_spread,
            temporal_spread=temporal_spread,
            influence_metrics=influence_metrics,
            evidence_strength=evidence_strength
        )
    
    def _calculate_viral_score(self, post: SocialMediaPost) -> float:
        """Calculate viral score based on engagement metrics"""
        if not post.engagement:
            return 0.0
        
        likes = post.engagement.get('likes', 0)
        shares = post.engagement.get('shares', 0)
        comments = post.engagement.get('comments', 0)
        
        # Weighted viral score
        viral_score = (likes * 0.3 + shares * 0.5 + comments * 0.2) / 1000
        return min(viral_score, 1.0)  # Cap at 1.0
    
    def _is_suspicious_posting_pattern(self, posts: List[SocialMediaPost]) -> bool:
        """Check if posting pattern is suspicious for influence campaigns"""
        if len(posts) < 10:
            return False
        
        # Check posting frequency
        posts_sorted = sorted(posts, key=lambda p: p.timestamp)
        time_diffs = []
        for i in range(1, len(posts_sorted)):
            diff = posts_sorted[i].timestamp - posts_sorted[i-1].timestamp
            time_diffs.append(diff.total_seconds())
        
        # Suspicious if posting too frequently (less than 1 minute average)
        avg_time_diff = np.mean(time_diffs)
        if avg_time_diff < 60:
            return True
        
        # Check content similarity (potential bot behavior)
        unique_content = set(post.content for post in posts)
        if len(unique_content) / len(posts) < 0.5:  # Less than 50% unique content
            return True
        
        return False
    
    def _calculate_geographic_spread(self, posts: List[SocialMediaPost]) -> Dict:
        """Calculate geographic spread of posts"""
        locations = [p.location for p in posts if p.location]
        if not locations:
            return {'spread_km': 0, 'locations_count': 0, 'countries': [], 'cities': []}
        
        # Calculate maximum distance between locations
        max_distance = 0
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                distance = geopy.distance.distance(
                    (loc1['lat'], loc1['lng']),
                    (loc2['lat'], loc2['lng'])
                ).kilometers
                max_distance = max(max_distance, distance)
        
        # Count unique locations
        countries = set(loc.get('country', '') for loc in locations if loc.get('country'))
        cities = set(loc.get('city', '') for loc in locations if loc.get('city'))
        
        return {
            'spread_km': max_distance,
            'locations_count': len(locations),
            'countries': list(countries),
            'cities': list(cities)
        }
    
    def _calculate_temporal_spread(self, posts: List[SocialMediaPost]) -> Dict:
        """Calculate temporal spread of posts"""
        timestamps = [p.timestamp for p in posts]
        if not timestamps:
            return {'duration_hours': 0, 'posts_per_hour': 0}
        
        min_time = min(timestamps)
        max_time = max(timestamps)
        duration = max_time - min_time
        
        return {
            'duration_hours': duration.total_seconds() / 3600,
            'posts_per_hour': len(posts) / max(duration.total_seconds() / 3600, 1),
            'start_time': min_time.isoformat(),
            'end_time': max_time.isoformat()
        }
    
    def _calculate_influence_metrics(self, posts: List[SocialMediaPost]) -> Dict:
        """Calculate influence metrics for posts"""
        total_engagement = 0
        unique_authors = set()
        
        for post in posts:
            if post.engagement:
                total_engagement += sum(post.engagement.values())
            unique_authors.add(post.author_id)
        
        return {
            'total_engagement': total_engagement,
            'unique_authors': len(unique_authors),
            'avg_engagement_per_post': total_engagement / len(posts) if posts else 0,
            'author_diversity': len(unique_authors) / len(posts) if posts else 0
        }
    
    def _calculate_evidence_strength(self, posts: List[SocialMediaPost],
                                   similarity: float, geo_spread: Dict,
                                   temporal_spread: Dict) -> float:
        """Calculate overall evidence strength score"""
        # Factors that increase evidence strength
        similarity_score = similarity * 0.4
        volume_score = min(len(posts) / 10, 1.0) * 0.2  # More posts = stronger
        geographic_score = min(geo_spread['spread_km'] / 1000, 1.0) * 0.2  # Wider spread = stronger
        temporal_score = min(temporal_spread['duration_hours'] / 24, 1.0) * 0.2  # Longer duration = stronger
        
        return similarity_score + volume_score + geographic_score + temporal_score

class GeographicAnalysisEngine:
    """Geographic analysis of social media patterns"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="insideout-platform")
    
    async def analyze_regional_patterns(self, posts: List[SocialMediaPost],
                                      patterns: List[PatternMatch]) -> List[GeographicCluster]:
        """Analyze patterns by geographic region"""
        # Filter posts with location data
        located_posts = [p for p in posts if p.location]
        if len(located_posts) < 3:
            return []
        
        # Extract coordinates
        coordinates = np.array([
            [p.location['lat'], p.location['lng']] for p in located_posts
        ])
        
        # Cluster by geographic proximity (DBSCAN with haversine metric)
        clustering = DBSCAN(eps=0.1, min_samples=3, metric='haversine')
        cluster_labels = clustering.fit_predict(np.radians(coordinates))
        
        clusters = []
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise
                continue
            
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_posts = [located_posts[i] for i in cluster_indices]
            cluster_coords = coordinates[cluster_indices]
            
            # Calculate cluster center and radius
            center_lat = np.mean(cluster_coords[:, 0])
            center_lng = np.mean(cluster_coords[:, 1])
            
            # Calculate radius (maximum distance from center)
            center = (center_lat, center_lng)
            max_distance = 0
            for coord in cluster_coords:
                distance = geopy.distance.distance(center, tuple(coord)).kilometers
                max_distance = max(max_distance, distance)
            
            # Find patterns relevant to this cluster
            cluster_patterns = []
            for pattern in patterns:
                pattern_post_ids = set(p.post_id for p in pattern.posts)
                cluster_post_ids = set(p.post_id for p in cluster_posts)
                if pattern_post_ids.intersection(cluster_post_ids):
                    cluster_patterns.append(pattern)
            
            # Calculate influence score
            influence_score = self._calculate_cluster_influence(cluster_posts)
            
            cluster = GeographicCluster(
                cluster_id=f"geo_cluster_{cluster_id}",
                center_location={'lat': center_lat, 'lng': center_lng},
                radius_km=max_distance,
                posts=cluster_posts,
                dominant_patterns=cluster_patterns,
                influence_score=influence_score
            )
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_cluster_influence(self, posts: List[SocialMediaPost]) -> float:
        """Calculate influence score for geographic cluster"""
        total_engagement = 0
        for post in posts:
            if post.engagement:
                total_engagement += sum(post.engagement.values())
        
        # Normalize by number of posts
        return total_engagement / len(posts) if posts else 0

class TemporalAnalysisEngine:
    """Temporal analysis of social media patterns"""
    
    def __init__(self):
        pass
    
    async def analyze_chronological_patterns(self, posts: List[SocialMediaPost],
                                           patterns: List[PatternMatch]) -> List[TemporalPattern]:
        """Analyze how patterns evolve over time"""
        if not posts:
            return []
        
        # Sort posts chronologically
        sorted_posts = sorted(posts, key=lambda p: p.timestamp)
        
        # Create time windows (e.g., hourly, daily)
        time_windows = self._create_time_windows(sorted_posts)
        
        temporal_patterns = []
        for pattern in patterns:
            pattern_posts = sorted(pattern.posts, key=lambda p: p.timestamp)
            
            # Analyze pattern evolution
            evolution = self._analyze_pattern_evolution(pattern_posts, time_windows)
            
            # Calculate viral acceleration
            viral_acceleration = self._calculate_viral_acceleration(pattern_posts)
            
            # Find peak activity
            peak_activity = self._find_peak_activity(pattern_posts)
            
            # Calculate decay rate
            decay_rate = self._calculate_decay_rate(pattern_posts)
            
            temporal_pattern = TemporalPattern(
                pattern_id=f"temporal_{pattern.pattern_id}",
                time_range={
                    'start': pattern_posts[0].timestamp,
                    'end': pattern_posts[-1].timestamp
                },
                posts=pattern_posts,
                pattern_evolution=evolution,
                viral_acceleration=viral_acceleration,
                peak_activity=peak_activity,
                decay_rate=decay_rate
            )
            temporal_patterns.append(temporal_pattern)
        
        return temporal_patterns
    
    def _create_time_windows(self, posts: List[SocialMediaPost], 
                           window_size_hours: int = 1) -> List[Dict]:
        """Create time windows for analysis"""
        if not posts:
            return []
        
        start_time = posts[0].timestamp
        end_time = posts[-1].timestamp
        
        windows = []
        current_time = start_time
        
        while current_time < end_time:
            window_end = current_time + timedelta(hours=window_size_hours)
            window_posts = [
                p for p in posts 
                if current_time <= p.timestamp < window_end
            ]
            
            windows.append({
                'start': current_time,
                'end': window_end,
                'posts': window_posts,
                'count': len(window_posts)
            })
            
            current_time = window_end
        
        return windows
    
    def _analyze_pattern_evolution(self, posts: List[SocialMediaPost],
                                 time_windows: List[Dict]) -> List[Dict]:
        """Analyze how pattern evolves over time windows"""
        evolution = []
        
        for window in time_windows:
            window_posts = [
                p for p in posts 
                if window['start'] <= p.timestamp < window['end']
            ]
            
            if window_posts:
                # Calculate metrics for this time window
                engagement = sum(
                    sum(p.engagement.values()) if p.engagement else 0
                    for p in window_posts
                )
                
                unique_authors = len(set(p.author_id for p in window_posts))
                
                evolution.append({
                    'time_window': window['start'].isoformat(),
                    'post_count': len(window_posts),
                    'total_engagement': engagement,
                    'unique_authors': unique_authors,
                    'avg_engagement': engagement / len(window_posts)
                })
        
        return evolution
    
    def _calculate_viral_acceleration(self, posts: List[SocialMediaPost]) -> float:
        """Calculate how quickly content goes viral"""
        if len(posts) < 2:
            return 0.0
        
        # Calculate posting rate over time
        time_diffs = []
        for i in range(1, len(posts)):
            diff = posts[i].timestamp - posts[i-1].timestamp
            time_diffs.append(diff.total_seconds())
        
        # Viral acceleration = decreasing time between posts
        if len(time_diffs) < 2:
            return 0.0
        
        early_avg = np.mean(time_diffs[:len(time_diffs)//2])
        late_avg = np.mean(time_diffs[len(time_diffs)//2:])
        
        if late_avg == 0:
            return float('inf')
        
        return early_avg / late_avg  # Higher = more acceleration
    
    def _find_peak_activity(self, posts: List[SocialMediaPost]) -> datetime:
        """Find time of peak activity"""
        if not posts:
            return datetime.utcnow()
        
        # Group posts by hour
        hourly_counts = defaultdict(int)
        for post in posts:
            hour_key = post.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        # Find hour with maximum posts
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0]
        return peak_hour
    
    def _calculate_decay_rate(self, posts: List[SocialMediaPost]) -> float:
        """Calculate how quickly activity decays after peak"""
        if len(posts) < 3:
            return 0.0
        
        peak_time = self._find_peak_activity(posts)
        
        # Count posts before and after peak
        before_peak = [p for p in posts if p.timestamp <= peak_time]
        after_peak = [p for p in posts if p.timestamp > peak_time]
        
        if not after_peak:
            return 0.0
        
        # Calculate decay as ratio of post-peak to pre-peak activity
        before_rate = len(before_peak)
        after_rate = len(after_peak)
        
        return before_rate / after_rate if after_rate > 0 else float('inf')

class SecureBERTAnalysisEngine:
    """Main analysis engine coordinating all components"""
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        self.bert_model = SecureBERTModel(model_name)
        self.scope_validator = LegalScopeValidator()
        self.pattern_detector = PatternDetectionEngine(self.bert_model)
        self.geographic_analyzer = GeographicAnalysisEngine()
        self.temporal_analyzer = TemporalAnalysisEngine()
    
    async def analyze_content_patterns(self, posts: List[SocialMediaPost],
                                     analysis_scope: AnalysisScope,
                                     officer_id: str) -> AnalysisResult:
        """Perform comprehensive content analysis within legal scope"""
        analysis_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Validate legal scope
        scope_validation = await self.scope_validator.validate_analysis_scope(analysis_scope)
        if not all(scope_validation.values()):
            raise ValueError(f"Analysis scope validation failed: {scope_validation}")
        
        # Filter posts to legal scope
        filtered_posts = await self.scope_validator.filter_content_by_scope(posts, analysis_scope)
        
        if not filtered_posts:
            logger.warning("No posts remain after scope filtering")
            return AnalysisResult(
                analysis_id=analysis_id,
                warrant_id=analysis_scope.warrant_id,
                analysis_type=AnalysisType.PATTERN_DETECTION,
                scope=analysis_scope,
                patterns=[],
                geographic_clusters=[],
                temporal_patterns=[],
                confidence_scores={},
                legal_compliance=scope_validation,
                processing_metadata={'filtered_posts': 0, 'processing_time_ms': 0},
                created_at=start_time
            )
        
        # Detect patterns
        logger.info(f"Detecting patterns in {len(filtered_posts)} posts")
        
        coordinated_patterns = await self.pattern_detector.detect_coordinated_behavior(
            filtered_posts, analysis_scope.warrant_id, officer_id
        )
        
        viral_patterns = await self.pattern_detector.detect_viral_content(
            filtered_posts, analysis_scope.warrant_id, officer_id
        )
        
        influence_patterns = await self.pattern_detector.detect_influence_campaigns(
            filtered_posts, analysis_scope.warrant_id, officer_id
        )
        
        all_patterns = coordinated_patterns + viral_patterns + influence_patterns
        
        # Geographic analysis
        geographic_clusters = await self.geographic_analyzer.analyze_regional_patterns(
            filtered_posts, all_patterns
        )
        
        # Temporal analysis
        temporal_patterns = await self.temporal_analyzer.analyze_chronological_patterns(
            filtered_posts, all_patterns
        )
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(all_patterns)
        
        # Processing metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        processing_metadata = {
            'original_posts': len(posts),
            'filtered_posts': len(filtered_posts),
            'processing_time_ms': processing_time,
            'patterns_detected': len(all_patterns),
            'geographic_clusters': len(geographic_clusters),
            'temporal_patterns': len(temporal_patterns)
        }
        
        return AnalysisResult(
            analysis_id=analysis_id,
            warrant_id=analysis_scope.warrant_id,
            analysis_type=AnalysisType.PATTERN_DETECTION,
            scope=analysis_scope,
            patterns=all_patterns,
            geographic_clusters=geographic_clusters,
            temporal_patterns=temporal_patterns,
            confidence_scores=confidence_scores,
            legal_compliance=scope_validation,
            processing_metadata=processing_metadata,
            created_at=start_time
        )
    
    def _calculate_confidence_scores(self, patterns: List[PatternMatch]) -> Dict[str, float]:
        """Calculate overall confidence scores"""
        if not patterns:
            return {'overall': 0.0}
        
        pattern_confidences = [p.confidence_score for p in patterns]
        evidence_strengths = [p.evidence_strength for p in patterns]
        
        return {
            'overall': np.mean(pattern_confidences),
            'max_confidence': np.max(pattern_confidences),
            'min_confidence': np.min(pattern_confidences),
            'avg_evidence_strength': np.mean(evidence_strengths),
            'pattern_count': len(patterns)
        }

# Example usage
async def main():
    """Example usage of secure BERT analysis engine"""
    
    # Initialize analysis engine
    engine = SecureBERTAnalysisEngine()
    
    # Create sample posts
    sample_posts = [
        SocialMediaPost(
            post_id="post_1",
            platform="twitter",
            author_id="user_1",
            author_username="@user1",
            content="This is a test post about current events",
            timestamp=datetime.utcnow() - timedelta(hours=2),
            location={'lat': 28.6139, 'lng': 77.2090, 'place': 'Delhi'},
            engagement={'likes': 10, 'shares': 5, 'comments': 3}
        ),
        SocialMediaPost(
            post_id="post_2",
            platform="twitter",
            author_id="user_2",
            author_username="@user2",
            content="Similar test post about current events",
            timestamp=datetime.utcnow() - timedelta(hours=1),
            location={'lat': 28.6129, 'lng': 77.2095, 'place': 'Delhi'},
            engagement={'likes': 15, 'shares': 8, 'comments': 5}
        )
    ]
    
    # Create analysis scope
    analysis_scope = AnalysisScope(
        warrant_id="WR-2024-001",
        geographic_bounds={
            'center': {'lat': 28.6139, 'lng': 77.2090},
            'radius_km': 50
        },
        temporal_bounds={
            'start': datetime.utcnow() - timedelta(days=7),
            'end': datetime.utcnow()
        },
        platform_scope=['twitter', 'facebook'],
        content_types=['posts', 'comments'],
        keywords=['test', 'events'],
        legal_constraints=['fourth_amendment_compliant']
    )
    
    # Perform analysis
    result = await engine.analyze_content_patterns(
        sample_posts, analysis_scope, "officer_123"
    )
    
    print(f"Analysis completed: {result.analysis_id}")
    print(f"Patterns detected: {len(result.patterns)}")
    print(f"Geographic clusters: {len(result.geographic_clusters)}")
    print(f"Temporal patterns: {len(result.temporal_patterns)}")
    print(f"Overall confidence: {result.confidence_scores.get('overall', 0):.2f}")

if __name__ == "__main__":
    asyncio.run(main())