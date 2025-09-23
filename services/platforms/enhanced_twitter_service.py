#!/usr/bin/env python3
"""
Enhanced Twitter API Service for SentinentalBERT
Optimized for free tier limitations with smart caching
"""

import tweepy
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import time
import os
from dataclasses import dataclass, asdict
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TwitterPost:
    """Twitter post data structure"""
    id: str
    text: str
    author_id: str
    author_username: str
    author_name: str
    created_at: datetime
    public_metrics: Dict[str, int]
    context_annotations: List[Dict] = None
    entities: Dict = None
    geo: Dict = None
    lang: str = "en"
    possibly_sensitive: bool = False
    referenced_tweets: List[Dict] = None
    reply_settings: str = "everyone"
    source: str = "Twitter Web App"
    withheld: Dict = None

class EnhancedTwitterService:
    """Enhanced Twitter API service with caching and rate limiting"""
    
    def __init__(self, db_path: str = "data/twitter_cache.db"):
        # Twitter API credentials
        self.api_key = "tkG3UCrcXhq1LCzC3n02mqg2N"
        self.api_secret = "oXRCjqTeJkV4KWrXFS5JO7ZIjcGGTHSNiUGStL0KIjSHmke90x"
        self.access_token = "835527957481459713-m4BKaUIuaAt2uQ6c2DITWDyoBcFxMAJ"
        self.access_token_secret = "B4C9XYaJOMuy7l3nq3Lo2h8FmoKV4TzkmnuqlDtlbveP1"
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAAHsN4QEAAAAA8%2BZQa%2BzllARQxtAvmhCQsA0WQCs%3DpF9thH1ztd85xkbAsWZvubIgJ98edZ3z7BdA8q1vfkRHnBMd6B"
        
        # Initialize Twitter API clients
        self.client_v2 = None
        self.api_v1 = None
        self.db_path = db_path
        
        # Rate limiting tracking
        self.monthly_requests = 0
        self.monthly_limit = 100  # Free tier limit
        self.last_reset = datetime.now()
        
        # Initialize database and API
        self._init_database()
        self._init_twitter_api()
        
    def _init_database(self):
        """Initialize SQLite database for caching"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for caching
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS twitter_posts (
                id TEXT PRIMARY KEY,
                keyword TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                date TEXT PRIMARY KEY,
                requests_used INTEGER DEFAULT 0,
                writes_used INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results_count INTEGER,
                cache_hit BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twitter_posts_keyword ON twitter_posts(keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_twitter_posts_expires ON twitter_posts(expires_at)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    def _init_twitter_api(self):
        """Initialize Twitter API clients"""
        try:
            # Initialize Twitter API v2 client
            self.client_v2 = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Initialize Twitter API v1.1 for additional features
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test connection
            me = self.client_v2.get_me()
            logger.info(f"Twitter API initialized successfully. User: {me.data.username}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT requests_used FROM api_usage WHERE date = ?', (today,))
        result = cursor.fetchone()
        
        current_usage = result[0] if result else 0
        conn.close()
        
        return current_usage < self.monthly_limit
    
    def _update_usage(self, requests: int = 1, writes: int = 0):
        """Update API usage tracking"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO api_usage (date, requests_used, writes_used)
            VALUES (?, 
                    COALESCE((SELECT requests_used FROM api_usage WHERE date = ?), 0) + ?,
                    COALESCE((SELECT writes_used FROM api_usage WHERE date = ?), 0) + ?)
        ''', (today, today, requests, today, writes))
        
        conn.commit()
        conn.close()
    
    def _get_cached_data(self, keyword: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """Get cached data for a keyword"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        cursor.execute('''
            SELECT data FROM twitter_posts 
            WHERE keyword = ? AND created_at > ? 
            ORDER BY created_at DESC
        ''', (keyword, cutoff_time))
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            cached_data = []
            for row in results:
                cached_data.extend(json.loads(row[0]))
            logger.info(f"Retrieved {len(cached_data)} cached posts for keyword: {keyword}")
            return cached_data
        
        return None
    
    def _cache_data(self, keyword: str, data: List[Dict], expires_hours: int = 24):
        """Cache data for a keyword"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        data_json = json.dumps(data)
        
        # Create unique ID for this cache entry
        cache_id = hashlib.md5(f"{keyword}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO twitter_posts (id, keyword, data, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (cache_id, keyword, data_json, expires_at))
        
        conn.commit()
        conn.close()
        logger.info(f"Cached {len(data)} posts for keyword: {keyword}")
    
    def search_tweets(self, keyword: str, max_results: int = 10, use_cache: bool = True) -> List[TwitterPost]:
        """Search tweets with caching and rate limiting"""
        
        # Check cache first if enabled
        if use_cache:
            cached_data = self._get_cached_data(keyword)
            if cached_data:
                self._log_search(keyword, len(cached_data), cache_hit=True)
                return [self._dict_to_twitter_post(post) for post in cached_data]
        
        # Check rate limits
        if not self._check_rate_limits():
            logger.warning("Rate limit exceeded, using cached data only")
            cached_data = self._get_cached_data(keyword, max_age_hours=168)  # 1 week
            if cached_data:
                return [self._dict_to_twitter_post(post) for post in cached_data]
            else:
                return []
        
        try:
            # Search using Twitter API v2
            tweets = self.client_v2.search_recent_tweets(
                query=keyword,
                max_results=min(max_results, 10),  # Free tier limitation
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 
                             'entities', 'geo', 'lang', 'possibly_sensitive', 'referenced_tweets', 
                             'reply_settings', 'source', 'withheld'],
                user_fields=['username', 'name', 'verified', 'public_metrics'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                logger.info(f"No tweets found for keyword: {keyword}")
                return []
            
            # Process results
            users = {user.id: user for user in tweets.includes.get('users', [])}
            twitter_posts = []
            posts_data = []
            
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                
                post = TwitterPost(
                    id=tweet.id,
                    text=tweet.text,
                    author_id=tweet.author_id,
                    author_username=author.username if author else "unknown",
                    author_name=author.name if author else "Unknown User",
                    created_at=tweet.created_at,
                    public_metrics=tweet.public_metrics or {},
                    context_annotations=tweet.context_annotations,
                    entities=tweet.entities,
                    geo=tweet.geo,
                    lang=tweet.lang,
                    possibly_sensitive=tweet.possibly_sensitive,
                    referenced_tweets=tweet.referenced_tweets,
                    reply_settings=tweet.reply_settings,
                    source=tweet.source,
                    withheld=tweet.withheld
                )
                
                twitter_posts.append(post)
                posts_data.append(asdict(post))
            
            # Cache the results
            if posts_data:
                self._cache_data(keyword, posts_data)
            
            # Update usage tracking
            self._update_usage(requests=1)
            self._log_search(keyword, len(twitter_posts), cache_hit=False)
            
            logger.info(f"Retrieved {len(twitter_posts)} tweets for keyword: {keyword}")
            return twitter_posts
            
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            # Fallback to cached data
            cached_data = self._get_cached_data(keyword, max_age_hours=168)
            if cached_data:
                return [self._dict_to_twitter_post(post) for post in cached_data]
            return []
    
    def _dict_to_twitter_post(self, data: Dict) -> TwitterPost:
        """Convert dictionary to TwitterPost object"""
        # Handle datetime conversion
        if isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        return TwitterPost(**data)
    
    def _log_search(self, keyword: str, results_count: int, cache_hit: bool = False):
        """Log search activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (keyword, results_count, cache_hit)
            VALUES (?, ?, ?)
        ''', (keyword, results_count, cache_hit))
        
        conn.commit()
        conn.close()
    
    def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """Get trending topics (cached for 1 hour)"""
        cache_key = f"trends_{woeid}"
        cached_data = self._get_cached_data(cache_key, max_age_hours=1)
        
        if cached_data:
            return cached_data
        
        if not self._check_rate_limits():
            return []
        
        try:
            trends = self.api_v1.get_place_trends(woeid)
            trend_data = []
            
            for trend in trends[0]['trends'][:10]:  # Top 10 trends
                trend_data.append({
                    'name': trend['name'],
                    'url': trend['url'],
                    'tweet_volume': trend['tweet_volume'],
                    'query': trend['query']
                })
            
            self._cache_data(cache_key, trend_data, expires_hours=1)
            self._update_usage(requests=1)
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get today's usage
        cursor.execute('SELECT requests_used, writes_used FROM api_usage WHERE date = ?', (today,))
        result = cursor.fetchone()
        
        current_usage = {
            'requests_used': result[0] if result else 0,
            'writes_used': result[1] if result else 0,
            'requests_remaining': self.monthly_limit - (result[0] if result else 0),
            'writes_remaining': 500 - (result[1] if result else 0)
        }
        
        # Get cache statistics
        cursor.execute('SELECT COUNT(*) FROM twitter_posts WHERE created_at > ?', 
                      (datetime.now() - timedelta(days=7),))
        cached_posts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM search_history WHERE search_time > ?', 
                      (datetime.now() - timedelta(days=7),))
        total_searches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM search_history WHERE cache_hit = 1 AND search_time > ?', 
                      (datetime.now() - timedelta(days=7),))
        cache_hits = cursor.fetchone()[0]
        
        conn.close()
        
        cache_hit_rate = (cache_hits / total_searches * 100) if total_searches > 0 else 0
        
        return {
            **current_usage,
            'cached_posts_week': cached_posts,
            'total_searches_week': total_searches,
            'cache_hit_rate': round(cache_hit_rate, 2)
        }
    
    def get_mock_data(self, keyword: str) -> List[TwitterPost]:
        """Generate mock data for testing when API limits are reached"""
        mock_posts = []
        
        # Generate realistic mock data
        for i in range(5):
            post = TwitterPost(
                id=f"mock_{keyword}_{i}",
                text=f"Mock tweet about {keyword} - This is sample content for testing purposes #{keyword}",
                author_id=f"mock_user_{i}",
                author_username=f"user_{i}",
                author_name=f"Mock User {i}",
                created_at=datetime.now() - timedelta(hours=i),
                public_metrics={
                    'retweet_count': 10 + i * 5,
                    'like_count': 50 + i * 10,
                    'reply_count': 5 + i * 2,
                    'quote_count': 2 + i
                },
                lang="en"
            )
            mock_posts.append(post)
        
        return mock_posts

# Test the service
if __name__ == "__main__":
    service = EnhancedTwitterService()
    
    # Test search
    results = service.search_tweets("climate change", max_results=5)
    print(f"Found {len(results)} tweets")
    
    for post in results[:2]:
        print(f"- {post.author_username}: {post.text[:100]}...")
    
    # Show usage stats
    stats = service.get_usage_stats()
    print(f"API Usage: {stats}")