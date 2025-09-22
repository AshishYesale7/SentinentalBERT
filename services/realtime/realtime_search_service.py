#!/usr/bin/env python3
"""
Real-time Search Service for SentinelBERT
Integrates social media data with sentiment analysis and viral detection
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import hashlib
import time

# Import existing services
import sys
sys.path.append('/workspace/project/SentinentalBERT')

from services.realtime.social_media_connectors import SocialMediaAggregator, SocialMediaPost
from services.nlp.models.sentiment_model import SentimentAnalyzer
from services.viral_detection.main import ViralDetectionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """Search query parameters"""
    keywords: str
    region: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    max_results: int = 100
    include_sentiment: bool = True
    include_viral_analysis: bool = True
    case_number: Optional[str] = None
    officer_id: Optional[str] = None

@dataclass
class EnrichedPost:
    """Social media post enriched with analysis"""
    # Original post data
    post_id: str
    platform: str
    author_handle: str
    author_id: str
    content: str
    timestamp: datetime
    url: str
    engagement_metrics: Dict[str, int]
    metadata: Dict[str, Any]
    location_data: Optional[Dict[str, Any]] = None
    media_urls: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    
    # Enriched analysis data
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    sentiment_confidence: Optional[float] = None
    viral_potential: Optional[float] = None
    influence_score: Optional[float] = None
    amplification_data: Optional[Dict[str, Any]] = None
    risk_indicators: List[str] = None
    
    # Investigation metadata
    search_query_id: Optional[str] = None
    analysis_timestamp: Optional[datetime] = None
    confidence_scores: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        data['analysis_timestamp'] = self.analysis_timestamp.isoformat() if self.analysis_timestamp else None
        return data

@dataclass
class SearchResults:
    """Complete search results with metadata"""
    query: SearchQuery
    posts: List[EnrichedPost]
    total_found: int
    platforms_searched: List[str]
    search_duration: float
    analysis_summary: Dict[str, Any]
    viral_actors: List[Dict[str, Any]]
    timeline_data: List[Dict[str, Any]]
    export_ready: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'query': asdict(self.query),
            'posts': [post.to_dict() for post in self.posts],
            'total_found': self.total_found,
            'platforms_searched': self.platforms_searched,
            'search_duration': self.search_duration,
            'analysis_summary': self.analysis_summary,
            'viral_actors': self.viral_actors,
            'timeline_data': self.timeline_data,
            'export_ready': self.export_ready
        }

class RealTimeSearchService:
    """Main service for real-time social media search and analysis"""
    
    def __init__(self):
        # Initialize components
        self.social_aggregator = SocialMediaAggregator()
        
        # Initialize NLP services
        try:
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.info("Sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"Sentiment analyzer not available: {e}")
            self.sentiment_analyzer = None
        
        # Initialize viral detection
        try:
            self.viral_detector = ViralDetectionService()
            logger.info("Viral detection service initialized")
        except Exception as e:
            logger.warning(f"Viral detection not available: {e}")
            self.viral_detector = None
        
        # Cache for recent searches
        self.search_cache = {}
        self.cache_duration = int(os.getenv('CACHE_DURATION_MINUTES', '15')) * 60
        
        logger.info("Real-time search service initialized")
    
    async def search_and_analyze(self, query: SearchQuery) -> SearchResults:
        """Perform comprehensive search and analysis"""
        start_time = time.time()
        
        # Generate query ID for caching and tracking
        query_id = self._generate_query_id(query)
        
        # Check cache first
        if query_id in self.search_cache:
            cached_result = self.search_cache[query_id]
            if time.time() - cached_result['timestamp'] < self.cache_duration:
                logger.info(f"Returning cached results for query: {query.keywords}")
                return cached_result['results']
        
        logger.info(f"Starting search for: {query.keywords}")
        
        # Step 1: Search social media platforms
        raw_posts = await self._search_platforms(query)
        
        # Step 2: Enrich posts with analysis
        enriched_posts = await self._enrich_posts(raw_posts, query_id)
        
        # Step 3: Generate analysis summary
        analysis_summary = self._generate_analysis_summary(enriched_posts)
        
        # Step 4: Identify viral actors
        viral_actors = self._identify_viral_actors(enriched_posts)
        
        # Step 5: Create timeline data
        timeline_data = self._create_timeline_data(enriched_posts)
        
        # Create results
        search_duration = time.time() - start_time
        results = SearchResults(
            query=query,
            posts=enriched_posts,
            total_found=len(enriched_posts),
            platforms_searched=self.social_aggregator.get_available_platforms(),
            search_duration=search_duration,
            analysis_summary=analysis_summary,
            viral_actors=viral_actors,
            timeline_data=timeline_data
        )
        
        # Cache results
        self.search_cache[query_id] = {
            'timestamp': time.time(),
            'results': results
        }
        
        logger.info(f"Search completed in {search_duration:.2f}s, found {len(enriched_posts)} posts")
        return results
    
    async def _search_platforms(self, query: SearchQuery) -> List[SocialMediaPost]:
        """Search across social media platforms"""
        
        # Set default time window if not specified
        if not query.start_time:
            hours = int(os.getenv('DEFAULT_TIME_WINDOW_HOURS', '24'))
            query.start_time = datetime.now() - timedelta(hours=hours)
        
        if not query.end_time:
            query.end_time = datetime.now()
        
        # Calculate time window in hours
        time_window_hours = int((query.end_time - query.start_time).total_seconds() / 3600)
        
        # Search all platforms
        posts = await self.social_aggregator.search_all_platforms(
            keywords=query.keywords,
            max_results_per_platform=query.max_results // len(query.platforms or ['twitter', 'youtube', 'reddit']),
            time_window_hours=time_window_hours,
            location=query.region,
            platforms=query.platforms
        )
        
        # Filter by time range if specified
        if query.start_time or query.end_time:
            filtered_posts = []
            for post in posts:
                if query.start_time and post.timestamp < query.start_time:
                    continue
                if query.end_time and post.timestamp > query.end_time:
                    continue
                filtered_posts.append(post)
            posts = filtered_posts
        
        return posts[:query.max_results]
    
    async def _enrich_posts(self, posts: List[SocialMediaPost], query_id: str) -> List[EnrichedPost]:
        """Enrich posts with sentiment and viral analysis"""
        enriched_posts = []
        
        for post in posts:
            try:
                enriched_post = EnrichedPost(
                    # Copy original post data
                    post_id=post.post_id,
                    platform=post.platform,
                    author_handle=post.author_handle,
                    author_id=post.author_id,
                    content=post.content,
                    timestamp=post.timestamp,
                    url=post.url,
                    engagement_metrics=post.engagement_metrics,
                    metadata=post.metadata,
                    location_data=post.location_data,
                    media_urls=post.media_urls or [],
                    hashtags=post.hashtags or [],
                    mentions=post.mentions or [],
                    
                    # Add analysis metadata
                    search_query_id=query_id,
                    analysis_timestamp=datetime.now(),
                    risk_indicators=[],
                    confidence_scores={}
                )
                
                # Sentiment analysis
                if self.sentiment_analyzer:
                    sentiment_result = await self._analyze_sentiment(post.content)
                    enriched_post.sentiment_score = sentiment_result.get('score')
                    enriched_post.sentiment_label = sentiment_result.get('label')
                    enriched_post.sentiment_confidence = sentiment_result.get('confidence')
                    enriched_post.confidence_scores['sentiment'] = sentiment_result.get('confidence', 0.0)
                
                # Viral potential analysis
                if self.viral_detector:
                    viral_result = await self._analyze_viral_potential(post)
                    enriched_post.viral_potential = viral_result.get('potential_score')
                    enriched_post.influence_score = viral_result.get('influence_score')
                    enriched_post.amplification_data = viral_result.get('amplification_data')
                    enriched_post.confidence_scores['viral'] = viral_result.get('confidence', 0.0)
                
                # Risk assessment
                enriched_post.risk_indicators = self._assess_risk_indicators(enriched_post)
                
                enriched_posts.append(enriched_post)
                
            except Exception as e:
                logger.error(f"Error enriching post {post.post_id}: {e}")
                continue
        
        return enriched_posts
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        try:
            if not self.sentiment_analyzer:
                return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
            
            # Use existing sentiment analyzer
            result = self.sentiment_analyzer.analyze_sentiment(content)
            
            return {
                'score': result.get('compound', 0.0),
                'label': self._get_sentiment_label(result.get('compound', 0.0)),
                'confidence': abs(result.get('compound', 0.0)),
                'detailed_scores': {
                    'positive': result.get('pos', 0.0),
                    'negative': result.get('neg', 0.0),
                    'neutral': result.get('neu', 0.0)
                }
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 0.05:
            return 'positive'
        elif score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    async def _analyze_viral_potential(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Analyze viral potential of post"""
        try:
            if not self.viral_detector:
                return {'potential_score': 0.0, 'influence_score': 0.0, 'confidence': 0.0}
            
            # Calculate viral potential based on engagement and content
            engagement_score = self._calculate_engagement_score(post.engagement_metrics)
            content_score = self._calculate_content_viral_score(post.content, post.hashtags or [])
            
            # Combine scores
            potential_score = (engagement_score * 0.6 + content_score * 0.4)
            
            # Calculate influence score based on platform and metrics
            influence_score = self._calculate_influence_score(post)
            
            return {
                'potential_score': potential_score,
                'influence_score': influence_score,
                'confidence': min(0.9, potential_score + 0.1),
                'amplification_data': {
                    'engagement_score': engagement_score,
                    'content_score': content_score,
                    'platform_factor': self._get_platform_factor(post.platform)
                }
            }
        except Exception as e:
            logger.error(f"Viral analysis error: {e}")
            return {'potential_score': 0.0, 'influence_score': 0.0, 'confidence': 0.0}
    
    def _calculate_engagement_score(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement score from metrics"""
        if not metrics:
            return 0.0
        
        # Normalize engagement metrics (platform-specific)
        total_engagement = sum(metrics.values())
        
        # Log scale for large numbers
        if total_engagement > 0:
            return min(1.0, np.log10(total_engagement + 1) / 6.0)  # Max at 1M engagement
        
        return 0.0
    
    def _calculate_content_viral_score(self, content: str, hashtags: List[str]) -> float:
        """Calculate viral potential from content features"""
        score = 0.0
        
        # Length factor (optimal length gets higher score)
        length = len(content)
        if 50 <= length <= 200:
            score += 0.3
        elif 20 <= length <= 300:
            score += 0.2
        
        # Hashtag factor
        hashtag_count = len(hashtags)
        if 1 <= hashtag_count <= 5:
            score += 0.2
        elif hashtag_count > 5:
            score += 0.1
        
        # Urgency/emotion keywords
        urgent_keywords = ['breaking', 'urgent', 'alert', 'important', 'shocking', 'amazing']
        for keyword in urgent_keywords:
            if keyword.lower() in content.lower():
                score += 0.1
                break
        
        # Question or call-to-action
        if '?' in content or any(word in content.lower() for word in ['share', 'retweet', 'comment']):
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_influence_score(self, post: SocialMediaPost) -> float:
        """Calculate influence score based on author and platform"""
        score = 0.0
        
        # Platform base score
        platform_scores = {
            'twitter': 0.8,
            'youtube': 0.9,
            'reddit': 0.6,
            'facebook': 0.7,
            'instagram': 0.7
        }
        score += platform_scores.get(post.platform, 0.5)
        
        # Engagement-based influence
        engagement_total = sum(post.engagement_metrics.values())
        if engagement_total > 1000:
            score += 0.2
        elif engagement_total > 100:
            score += 0.1
        
        return min(1.0, score)
    
    def _get_platform_factor(self, platform: str) -> float:
        """Get platform-specific viral factor"""
        factors = {
            'twitter': 1.0,
            'youtube': 0.8,
            'reddit': 0.7,
            'facebook': 0.9,
            'instagram': 0.8
        }
        return factors.get(platform, 0.6)
    
    def _assess_risk_indicators(self, post: EnrichedPost) -> List[str]:
        """Assess risk indicators for the post"""
        indicators = []
        
        # High viral potential
        if post.viral_potential and post.viral_potential > 0.7:
            indicators.append('high_viral_potential')
        
        # Strong negative sentiment
        if post.sentiment_score and post.sentiment_score < -0.5:
            indicators.append('negative_sentiment')
        
        # High engagement with negative content
        if (post.sentiment_score and post.sentiment_score < -0.3 and 
            post.viral_potential and post.viral_potential > 0.5):
            indicators.append('viral_negative_content')
        
        # Suspicious patterns in content
        suspicious_patterns = ['fake', 'hoax', 'conspiracy', 'urgent share']
        if any(pattern in post.content.lower() for pattern in suspicious_patterns):
            indicators.append('suspicious_content')
        
        # High amplification with low confidence
        if (post.influence_score and post.influence_score > 0.7 and
            post.confidence_scores and post.confidence_scores.get('sentiment', 1.0) < 0.5):
            indicators.append('low_confidence_high_influence')
        
        return indicators
    
    def _generate_analysis_summary(self, posts: List[EnrichedPost]) -> Dict[str, Any]:
        """Generate summary statistics from analyzed posts"""
        if not posts:
            return {}
        
        # Sentiment distribution
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        sentiment_scores = []
        viral_scores = []
        
        for post in posts:
            if post.sentiment_label:
                sentiment_counts[post.sentiment_label] += 1
            if post.sentiment_score is not None:
                sentiment_scores.append(post.sentiment_score)
            if post.viral_potential is not None:
                viral_scores.append(post.viral_potential)
        
        # Platform distribution
        platform_counts = {}
        for post in posts:
            platform_counts[post.platform] = platform_counts.get(post.platform, 0) + 1
        
        # Risk assessment
        high_risk_posts = [p for p in posts if 'viral_negative_content' in (p.risk_indicators or [])]
        
        return {
            'total_posts': len(posts),
            'sentiment_distribution': sentiment_counts,
            'average_sentiment': np.mean(sentiment_scores) if sentiment_scores else 0.0,
            'average_viral_potential': np.mean(viral_scores) if viral_scores else 0.0,
            'platform_distribution': platform_counts,
            'high_risk_posts': len(high_risk_posts),
            'time_range': {
                'earliest': min(p.timestamp for p in posts).isoformat(),
                'latest': max(p.timestamp for p in posts).isoformat()
            }
        }
    
    def _identify_viral_actors(self, posts: List[EnrichedPost]) -> List[Dict[str, Any]]:
        """Identify accounts that are driving viral content"""
        author_metrics = {}
        
        for post in posts:
            author_id = post.author_id
            if author_id not in author_metrics:
                author_metrics[author_id] = {
                    'handle': post.author_handle,
                    'platform': post.platform,
                    'post_count': 0,
                    'total_engagement': 0,
                    'total_viral_score': 0.0,
                    'avg_sentiment': 0.0,
                    'risk_indicators': set()
                }
            
            metrics = author_metrics[author_id]
            metrics['post_count'] += 1
            metrics['total_engagement'] += sum(post.engagement_metrics.values())
            
            if post.viral_potential:
                metrics['total_viral_score'] += post.viral_potential
            
            if post.sentiment_score:
                metrics['avg_sentiment'] += post.sentiment_score
            
            if post.risk_indicators:
                metrics['risk_indicators'].update(post.risk_indicators)
        
        # Calculate final scores and rank
        viral_actors = []
        for author_id, metrics in author_metrics.items():
            if metrics['post_count'] > 0:
                avg_viral_score = metrics['total_viral_score'] / metrics['post_count']
                avg_sentiment = metrics['avg_sentiment'] / metrics['post_count']
                
                # Calculate influence score
                influence_score = (
                    avg_viral_score * 0.4 +
                    (metrics['total_engagement'] / 1000) * 0.3 +  # Normalize engagement
                    metrics['post_count'] * 0.3
                )
                
                viral_actors.append({
                    'author_id': author_id,
                    'handle': metrics['handle'],
                    'platform': metrics['platform'],
                    'post_count': metrics['post_count'],
                    'total_engagement': metrics['total_engagement'],
                    'avg_viral_score': avg_viral_score,
                    'avg_sentiment': avg_sentiment,
                    'influence_score': min(1.0, influence_score),
                    'risk_indicators': list(metrics['risk_indicators'])
                })
        
        # Sort by influence score
        viral_actors.sort(key=lambda x: x['influence_score'], reverse=True)
        
        return viral_actors[:20]  # Top 20 viral actors
    
    def _create_timeline_data(self, posts: List[EnrichedPost]) -> List[Dict[str, Any]]:
        """Create chronological timeline data"""
        # Sort posts by timestamp
        sorted_posts = sorted(posts, key=lambda x: x.timestamp)
        
        timeline = []
        for post in sorted_posts:
            timeline.append({
                'timestamp': post.timestamp.isoformat(),
                'platform': post.platform,
                'author': post.author_handle,
                'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'sentiment_label': post.sentiment_label,
                'sentiment_score': post.sentiment_score,
                'viral_potential': post.viral_potential,
                'engagement_total': sum(post.engagement_metrics.values()),
                'url': post.url,
                'risk_indicators': post.risk_indicators or [],
                'hashtags': post.hashtags or [],
                'location': post.location_data.get('place_id') if post.location_data else None
            })
        
        return timeline
    
    def _generate_query_id(self, query: SearchQuery) -> str:
        """Generate unique ID for query caching"""
        query_string = f"{query.keywords}_{query.region}_{query.start_time}_{query.end_time}_{query.platforms}"
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def export_results(self, results: SearchResults, format: str = 'json') -> str:
        """Export search results in specified format"""
        if format == 'json':
            return json.dumps(results.to_dict(), indent=2, default=str)
        elif format == 'csv':
            # Convert to DataFrame for CSV export
            posts_data = []
            for post in results.posts:
                posts_data.append({
                    'timestamp': post.timestamp.isoformat(),
                    'platform': post.platform,
                    'author': post.author_handle,
                    'content': post.content,
                    'sentiment_label': post.sentiment_label,
                    'sentiment_score': post.sentiment_score,
                    'viral_potential': post.viral_potential,
                    'engagement_total': sum(post.engagement_metrics.values()),
                    'url': post.url,
                    'risk_indicators': ','.join(post.risk_indicators or [])
                })
            
            df = pd.DataFrame(posts_data)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Example usage
async def main():
    """Test the real-time search service"""
    service = RealTimeSearchService()
    
    # Create test query
    query = SearchQuery(
        keywords="climate change",
        region="India",
        max_results=20,
        case_number="TEST_001",
        officer_id="test_officer"
    )
    
    # Perform search
    results = await service.search_and_analyze(query)
    
    print(f"Search completed: {results.total_found} posts found")
    print(f"Analysis summary: {results.analysis_summary}")
    print(f"Top viral actors: {len(results.viral_actors)}")

if __name__ == "__main__":
    asyncio.run(main())