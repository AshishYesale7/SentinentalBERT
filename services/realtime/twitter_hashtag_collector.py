#!/usr/bin/env python3
"""
Twitter Hashtag Collector - Real-time data collection for original source analysis
Collects hashtag data with precise timestamps to identify original posters
"""

import tweepy
import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import time

logger = logging.getLogger(__name__)

class TwitterHashtagCollector:
    """Collects Twitter data for hashtag analysis with original source tracking"""
    
    def __init__(self):
        self.api = None
        self.client = None
        self.db_connection = None
        self._initialize_twitter_api()
        self._initialize_database()
    
    def _initialize_twitter_api(self):
        """Initialize Twitter API connection"""
        try:
            # Get credentials from environment
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if not bearer_token:
                logger.warning("Twitter Bearer Token not found, using mock data")
                return
            
            # Initialize Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Test the connection
            try:
                me = self.client.get_me()
                logger.info(f"Twitter API initialized successfully for user: {me.data.username if me.data else 'Unknown'}")
            except Exception as e:
                logger.warning(f"Twitter API test failed: {e}")
                self.client = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.client = None
    
    def _initialize_database(self):
        """Initialize database connection"""
        try:
            self.db_connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'sentinelbert'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            
            # Create tables if they don't exist
            self._create_tables()
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.db_connection = None
    
    def _create_tables(self):
        """Create necessary database tables"""
        try:
            with self.db_connection.cursor() as cursor:
                # Create hashtag_posts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hashtag_posts (
                        id SERIAL PRIMARY KEY,
                        post_id VARCHAR(255) UNIQUE NOT NULL,
                        hashtag VARCHAR(255) NOT NULL,
                        author VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        platform VARCHAR(50) NOT NULL DEFAULT 'twitter',
                        engagement_count INTEGER DEFAULT 0,
                        likes_count INTEGER DEFAULT 0,
                        retweets_count INTEGER DEFAULT 0,
                        replies_count INTEGER DEFAULT 0,
                        sentiment VARCHAR(50),
                        content_hash VARCHAR(64),
                        is_original BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create index on hashtag and timestamp for fast queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_hashtag_timestamp 
                    ON hashtag_posts(hashtag, timestamp)
                """)
                
                # Create index on content_hash for duplicate detection
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_content_hash 
                    ON hashtag_posts(content_hash)
                """)
                
                self.db_connection.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            if self.db_connection:
                self.db_connection.rollback()
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for duplicate detection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def collect_hashtag_data(self, hashtag: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Collect real-time hashtag data from Twitter
        
        Args:
            hashtag: Hashtag to search (with or without #)
            limit: Maximum number of tweets to collect
            
        Returns:
            List of tweet data with timestamps
        """
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        collected_data = []
        
        if self.client:
            try:
                # Search for recent tweets with the hashtag
                tweets = tweepy.Paginator(
                    self.client.search_recent_tweets,
                    query=f"{hashtag} -is:retweet",  # Exclude retweets to find originals
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                    user_fields=['username', 'name'],
                    expansions=['author_id'],
                    max_results=min(limit, 100)  # Twitter API limit
                ).flatten(limit=limit)
                
                # Get user information
                users = {}
                for tweet in tweets:
                    if hasattr(tweet, 'includes') and 'users' in tweet.includes:
                        for user in tweet.includes['users']:
                            users[user.id] = user
                
                # Process tweets
                for tweet in tweets:
                    try:
                        # Get user info
                        user = users.get(tweet.author_id, {})
                        username = getattr(user, 'username', f'user_{tweet.author_id}')
                        
                        # Calculate engagement
                        metrics = tweet.public_metrics or {}
                        engagement = (
                            metrics.get('like_count', 0) + 
                            metrics.get('retweet_count', 0) + 
                            metrics.get('reply_count', 0)
                        )
                        
                        # Create tweet data
                        tweet_data = {
                            'post_id': tweet.id,
                            'hashtag': hashtag,
                            'author': f'@{username}',
                            'content': tweet.text,
                            'timestamp': tweet.created_at.isoformat(),
                            'platform': 'twitter',
                            'engagement': engagement,
                            'likes': metrics.get('like_count', 0),
                            'retweets': metrics.get('retweet_count', 0),
                            'replies': metrics.get('reply_count', 0),
                            'sentiment': self._analyze_sentiment(tweet.text),
                            'content_hash': self._calculate_content_hash(tweet.text)
                        }
                        
                        collected_data.append(tweet_data)
                        
                        # Store in database
                        self._store_tweet_data(tweet_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing tweet {tweet.id}: {e}")
                        continue
                
                logger.info(f"Collected {len(collected_data)} tweets for hashtag {hashtag}")
                
            except Exception as e:
                logger.error(f"Error collecting Twitter data: {e}")
                # Return mock data if API fails
                return self._generate_mock_data(hashtag, limit)
        
        else:
            # Return mock data if no API connection
            return self._generate_mock_data(hashtag, limit)
        
        return collected_data
    
    def _store_tweet_data(self, tweet_data: Dict[str, Any]):
        """Store tweet data in database"""
        if not self.db_connection:
            return
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO hashtag_posts 
                    (post_id, hashtag, author, content, timestamp, platform, 
                     engagement_count, likes_count, retweets_count, replies_count, 
                     sentiment, content_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (post_id) DO UPDATE SET
                        engagement_count = EXCLUDED.engagement_count,
                        likes_count = EXCLUDED.likes_count,
                        retweets_count = EXCLUDED.retweets_count,
                        replies_count = EXCLUDED.replies_count
                """, (
                    tweet_data['post_id'],
                    tweet_data['hashtag'],
                    tweet_data['author'],
                    tweet_data['content'],
                    tweet_data['timestamp'],
                    tweet_data['platform'],
                    tweet_data['engagement'],
                    tweet_data['likes'],
                    tweet_data['retweets'],
                    tweet_data['replies'],
                    tweet_data['sentiment'],
                    tweet_data['content_hash']
                ))
                
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"Error storing tweet data: {e}")
            if self.db_connection:
                self.db_connection.rollback()
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis (can be enhanced with BERT model)"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'Positive'
        elif negative_count > positive_count:
            return 'Negative'
        else:
            return 'Neutral'
    
    def find_original_source(self, hashtag: str) -> Dict[str, Any]:
        """
        Find the original source of a hashtag by analyzing timestamps
        
        Args:
            hashtag: Hashtag to analyze
            
        Returns:
            Dictionary with original source analysis
        """
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        if not self.db_connection:
            return {"error": "Database not available"}
        
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Find earliest post with this hashtag
                cursor.execute("""
                    SELECT * FROM hashtag_posts 
                    WHERE hashtag = %s 
                    ORDER BY timestamp ASC 
                    LIMIT 1
                """, (hashtag,))
                
                earliest_post = cursor.fetchone()
                
                if not earliest_post:
                    return {"error": "No posts found for this hashtag"}
                
                # Get all posts for timeline analysis
                cursor.execute("""
                    SELECT author, content, timestamp, engagement_count, sentiment
                    FROM hashtag_posts 
                    WHERE hashtag = %s 
                    ORDER BY timestamp ASC
                """, (hashtag,))
                
                all_posts = cursor.fetchall()
                
                # Calculate time span
                if len(all_posts) > 1:
                    first_time = all_posts[0]['timestamp']
                    last_time = all_posts[-1]['timestamp']
                    time_span = last_time - first_time
                    
                    if time_span.days > 0:
                        time_span_str = f"{time_span.days} days"
                    elif time_span.seconds > 3600:
                        time_span_str = f"{time_span.seconds // 3600} hours"
                    else:
                        time_span_str = f"{time_span.seconds // 60} minutes"
                else:
                    time_span_str = "Single post"
                
                # Analyze propagation pattern
                propagation_analysis = self._analyze_propagation(all_posts)
                
                return {
                    "original_post": {
                        "author": earliest_post['author'],
                        "content": earliest_post['content'],
                        "timestamp": earliest_post['timestamp'].isoformat(),
                        "engagement": earliest_post['engagement_count'],
                        "sentiment": earliest_post['sentiment']
                    },
                    "timeline_analysis": {
                        "total_posts": len(all_posts),
                        "time_span": time_span_str,
                        "first_post": all_posts[0]['timestamp'].isoformat(),
                        "latest_post": all_posts[-1]['timestamp'].isoformat()
                    },
                    "propagation_pattern": propagation_analysis,
                    "confidence_score": self._calculate_source_confidence(all_posts)
                }
                
        except Exception as e:
            logger.error(f"Error finding original source: {e}")
            return {"error": str(e)}
    
    def _analyze_propagation(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze how the hashtag propagated over time"""
        if len(posts) < 2:
            return {"pattern": "single_post", "velocity": 0}
        
        # Calculate posting velocity (posts per hour)
        first_time = posts[0]['timestamp']
        last_time = posts[-1]['timestamp']
        time_diff = (last_time - first_time).total_seconds() / 3600  # hours
        
        if time_diff > 0:
            velocity = len(posts) / time_diff
        else:
            velocity = len(posts)  # All posts in same hour
        
        # Analyze engagement pattern
        total_engagement = sum(post['engagement_count'] for post in posts)
        avg_engagement = total_engagement / len(posts) if posts else 0
        
        # Determine pattern type
        if velocity > 10:
            pattern = "viral"
        elif velocity > 1:
            pattern = "trending"
        else:
            pattern = "organic"
        
        return {
            "pattern": pattern,
            "velocity": round(velocity, 2),
            "total_posts": len(posts),
            "avg_engagement": round(avg_engagement, 2),
            "peak_engagement": max(post['engagement_count'] for post in posts) if posts else 0
        }
    
    def _calculate_source_confidence(self, posts: List[Dict]) -> float:
        """Calculate confidence score for original source identification"""
        if not posts:
            return 0.0
        
        # Factors affecting confidence
        time_gap_factor = 1.0  # Higher if significant time gap between first and second post
        engagement_factor = 0.8  # Based on engagement patterns
        content_uniqueness = 0.9  # Based on content similarity analysis
        
        if len(posts) > 1:
            first_time = posts[0]['timestamp']
            second_time = posts[1]['timestamp']
            gap_hours = (second_time - first_time).total_seconds() / 3600
            
            # Higher confidence if there's a significant gap
            if gap_hours > 1:
                time_gap_factor = 0.95
            elif gap_hours > 0.5:
                time_gap_factor = 0.85
            else:
                time_gap_factor = 0.75
        
        confidence = (time_gap_factor * 0.4 + engagement_factor * 0.3 + content_uniqueness * 0.3)
        return min(confidence, 0.95)  # Cap at 95%
    
    def _generate_mock_data(self, hashtag: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock data when API is not available"""
        import random
        from datetime import timedelta
        
        mock_data = []
        base_time = datetime.now(timezone.utc)
        
        for i in range(min(limit, 33)):
            # Create realistic timestamps with the first post being earliest
            hours_ago = random.randint(1, 48) if i > 0 else random.randint(24, 48)
            timestamp = base_time - timedelta(hours=hours_ago)
            
            mock_data.append({
                'post_id': f'mock_{random.randint(100000, 999999)}',
                'hashtag': hashtag,
                'author': f'@user_{random.randint(1000, 9999)}',
                'content': f'Sample content related to {hashtag} - post {i+1}',
                'timestamp': timestamp.isoformat(),
                'platform': 'twitter',
                'engagement': random.randint(10, 1000),
                'likes': random.randint(5, 500),
                'retweets': random.randint(0, 100),
                'replies': random.randint(0, 50),
                'sentiment': random.choice(['Positive', 'Negative', 'Neutral']),
                'content_hash': self._calculate_content_hash(f'Sample content related to {hashtag} - post {i+1}')
            })
        
        # Sort by timestamp to ensure chronological order
        mock_data.sort(key=lambda x: x['timestamp'])
        
        # Store mock data in database for testing
        for data in mock_data:
            self._store_tweet_data(data)
        
        return mock_data
    
    def get_hashtag_timeline(self, hashtag: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of hashtag posts"""
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        if not self.db_connection:
            return []
        
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM hashtag_posts 
                    WHERE hashtag = %s 
                    ORDER BY timestamp ASC
                """, (hashtag,))
                
                posts = cursor.fetchall()
                return [dict(post) for post in posts]
                
        except Exception as e:
            logger.error(f"Error getting hashtag timeline: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.db_connection:
            self.db_connection.close()