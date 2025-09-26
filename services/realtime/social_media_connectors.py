#!/usr/bin/env python3
"""
Real-time Social Media Connectors for SentinelBERT
Provides secure, rate-limited access to X.com, YouTube, and Reddit APIs
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import time
from urllib.parse import quote_plus
import re

# API Libraries
import tweepy
import praw
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

# Environment and utilities
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Telegram connector
try:
    from .telegram_connector import TelegramConnector
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Telegram connector not available: {e}")
    TELEGRAM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SocialMediaPost:
    """Standardized social media post structure"""
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
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class RateLimiter:
    """Rate limiting utility for API calls"""
    
    def __init__(self, max_calls: int, time_window: int = 900):  # 15 minutes default
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call) + 1
            logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        self.calls.append(now)

class TwitterConnector:
    """Twitter/X.com API connector with rate limiting - Optimized for Free Tier"""
    
    def __init__(self):
        # Load all Twitter API credentials
        self.api_key = os.getenv('TWITTER_API_KEY', 'tkG3UCrcXhq1LCzC3n02mqg2N')
        self.api_secret = os.getenv('TWITTER_API_SECRET', 'oXRCjqTeJkV4KWrXFS5JO7ZIjcGGTHSNiUGStL0KIjSHmke90x')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN', '835527957481459713-m4BKaUIuaAt2uQ6c2DITWDyoBcFxMAJ')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'B4C9XYaJOMuy7l3nq3Lo2h8FmoKV4TzkmnuqlDtlbveP1')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAAHsN4QEAAAAA8%2BZQa%2BzllARQxtAvmhCQsA0WQCs%3DpF9thH1ztd85xkbAsWZvubIgJ98edZ3z7BdA8q1vfkRHnBMd6B')
        
        self.api_version = os.getenv('TWITTER_API_VERSION', '2')
        self.rate_limit = int(os.getenv('TWITTER_RATE_LIMIT', '100'))  # Free tier limit
        
        # Initialize Tweepy client with full authentication
        try:
            # Try v2 client first (preferred for new features)
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Also initialize v1.1 API for additional functionality
            auth = tweepy.OAuth1UserHandler(
                self.api_key, self.api_secret,
                self.access_token, self.access_token_secret
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter connector initialized with full authentication")
            logger.info(f"Rate limit set to {self.rate_limit} requests (Free tier)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise
        
        self.rate_limiter = RateLimiter(self.rate_limit, time_window=900)  # 15 minutes
        self.monthly_usage = 0  # Track monthly usage for free tier
        self.max_monthly_posts = 100  # Free tier limit
    
    async def search_tweets(self, 
                          keywords: str, 
                          max_results: int = 10,  # Reduced for free tier
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          location: Optional[str] = None) -> List[SocialMediaPost]:
        """Search for tweets with specified criteria - Optimized for Free Tier"""
        
        # Check monthly usage limit
        if self.monthly_usage >= self.max_monthly_posts:
            logger.warning("Monthly API usage limit reached (100 posts)")
            return []
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            # Build search query
            query = self._build_search_query(keywords, location)
            
            # Set time parameters (shorter window for free tier)
            if not start_time:
                start_time = datetime.now() - timedelta(hours=6)  # Reduced from 24h
            if not end_time:
                end_time = datetime.now()
            
            # Limit results for free tier
            max_results = min(max_results, 10, self.max_monthly_posts - self.monthly_usage)
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'context_annotations', 'entities', 'referenced_tweets'],
                user_fields=['username', 'name', 'location', 'verified', 'public_metrics'],
                expansions=['author_id', 'geo.place_id', 'referenced_tweets.id']
            ).flatten(limit=max_results)
            
            posts = []
            for tweet in tweets:
                try:
                    post = self._convert_tweet_to_post(tweet)
                    if post:
                        posts.append(post)
                        self.monthly_usage += 1
                except Exception as e:
                    logger.error(f"Error converting tweet {tweet.id}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(posts)} tweets for query: {keywords} (Monthly usage: {self.monthly_usage}/{self.max_monthly_posts})")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    async def get_tweet_by_id(self, tweet_id: str) -> Optional[SocialMediaPost]:
        """Get a specific tweet by ID - Optimized for tracking"""
        
        # Check monthly usage limit
        if self.monthly_usage >= self.max_monthly_posts:
            logger.warning("Monthly API usage limit reached")
            return None
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            # Get tweet by ID
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'context_annotations', 'entities', 'referenced_tweets'],
                user_fields=['username', 'name', 'location', 'verified', 'public_metrics'],
                expansions=['author_id', 'geo.place_id', 'referenced_tweets.id']
            )
            
            if tweet.data:
                self.monthly_usage += 1
                post = self._convert_tweet_to_post(tweet.data)
                logger.info(f"Retrieved tweet {tweet_id} (Monthly usage: {self.monthly_usage}/{self.max_monthly_posts})")
                return post
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting tweet {tweet_id}: {e}")
            return None
    
    async def get_user_timeline(self, username: str, max_results: int = 5) -> List[SocialMediaPost]:
        """Get user's recent tweets - Optimized for free tier"""
        
        # Check monthly usage limit
        if self.monthly_usage >= self.max_monthly_posts:
            logger.warning("Monthly API usage limit reached")
            return []
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            # Get user by username
            user = self.client.get_user(username=username.lstrip('@'))
            if not user.data:
                logger.warning(f"User {username} not found")
                return []
            
            user_id = user.data.id
            
            # Limit results for free tier
            max_results = min(max_results, 5, self.max_monthly_posts - self.monthly_usage)
            
            # Get user tweets
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'context_annotations', 'entities', 'referenced_tweets'],
                user_fields=['username', 'name', 'location', 'verified', 'public_metrics'],
                expansions=['author_id', 'referenced_tweets.id']
            )
            
            posts = []
            if tweets.data:
                for tweet in tweets.data:
                    try:
                        post = self._convert_tweet_to_post(tweet)
                        if post:
                            posts.append(post)
                            self.monthly_usage += 1
                    except Exception as e:
                        logger.error(f"Error converting tweet {tweet.id}: {e}")
                        continue
            
            logger.info(f"Retrieved {len(posts)} tweets from @{username} (Monthly usage: {self.monthly_usage}/{self.max_monthly_posts})")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting user timeline for {username}: {e}")
            return []
    
    def _build_search_query(self, keywords: str, location: Optional[str] = None) -> str:
        """Build Twitter search query with filters"""
        query = keywords
        
        # Add location filter if specified
        if location:
            # Try to add location-based filters
            if location.lower() in ['india', 'भारत']:
                query += ' (place_country:IN OR lang:hi OR lang:bn OR lang:ta OR lang:te)'
            else:
                query += f' place:"{location}"'
        
        # Add filters for quality and recency
        query += ' -is:retweet lang:en OR lang:hi'  # Exclude retweets, include English and Hindi
        
        return query
    
    def _convert_tweet_to_post(self, tweet) -> Optional[SocialMediaPost]:
        """Convert Twitter API response to standardized post"""
        try:
            # Extract hashtags and mentions
            hashtags = []
            mentions = []
            media_urls = []
            
            if hasattr(tweet, 'entities') and tweet.entities:
                if 'hashtags' in tweet.entities:
                    hashtags = [tag['tag'] for tag in tweet.entities['hashtags']]
                if 'mentions' in tweet.entities:
                    mentions = [mention['username'] for mention in tweet.entities['mentions']]
                if 'urls' in tweet.entities:
                    media_urls = [url['expanded_url'] for url in tweet.entities['urls'] if url.get('expanded_url')]
            
            # Get engagement metrics
            metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
            engagement_metrics = {
                'retweet_count': metrics.get('retweet_count', 0),
                'like_count': metrics.get('like_count', 0),
                'reply_count': metrics.get('reply_count', 0),
                'quote_count': metrics.get('quote_count', 0)
            }
            
            # Extract location data
            location_data = None
            if hasattr(tweet, 'geo') and tweet.geo:
                location_data = {
                    'coordinates': tweet.geo.get('coordinates'),
                    'place_id': tweet.geo.get('place_id')
                }
            
            return SocialMediaPost(
                post_id=str(tweet.id),
                platform='twitter',
                author_handle=f"@{tweet.author_id}",  # Will be resolved with user data
                author_id=str(tweet.author_id),
                content=tweet.text,
                timestamp=tweet.created_at,
                url=f"https://twitter.com/i/status/{tweet.id}",
                engagement_metrics=engagement_metrics,
                metadata={
                    'context_annotations': getattr(tweet, 'context_annotations', []),
                    'possibly_sensitive': getattr(tweet, 'possibly_sensitive', False),
                    'source': 'twitter_api_v2'
                },
                location_data=location_data,
                media_urls=media_urls,
                hashtags=hashtags,
                mentions=mentions
            )
            
        except Exception as e:
            logger.error(f"Error converting tweet: {e}")
            return None

class YouTubeConnector:
    """YouTube Data API connector"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.rate_limiter = RateLimiter(100)  # 100 requests per 100 seconds
        
        logger.info("YouTube connector initialized")
    
    async def search_videos(self,
                          keywords: str,
                          max_results: int = 50,
                          published_after: Optional[datetime] = None,
                          region_code: str = 'IN') -> List[SocialMediaPost]:
        """Search for YouTube videos"""
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            # Set default time window
            if not published_after:
                published_after = datetime.now() - timedelta(hours=24)
            
            # Search for videos
            search_response = self.youtube.search().list(
                q=keywords,
                part='id,snippet',
                maxResults=min(max_results, 50),  # API limit
                order='date',
                publishedAfter=published_after.isoformat() + 'Z',
                regionCode=region_code,
                type='video',
                relevanceLanguage='en'
            ).execute()
            
            posts = []
            video_ids = []
            
            # Collect video IDs for detailed stats
            for item in search_response.get('items', []):
                video_ids.append(item['id']['videoId'])
            
            # Get detailed video statistics
            if video_ids:
                stats_response = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                stats_dict = {item['id']: item for item in stats_response.get('items', [])}
                
                # Convert to standardized posts
                for item in search_response.get('items', []):
                    try:
                        video_id = item['id']['videoId']
                        post = self._convert_video_to_post(item, stats_dict.get(video_id))
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.error(f"Error converting video {video_id}: {e}")
                        continue
            
            logger.info(f"Retrieved {len(posts)} YouTube videos for query: {keywords}")
            return posts
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {e}")
            return []
    
    def _convert_video_to_post(self, video_item, stats_item=None) -> Optional[SocialMediaPost]:
        """Convert YouTube API response to standardized post"""
        try:
            snippet = video_item['snippet']
            video_id = video_item['id']['videoId']
            
            # Extract hashtags from description
            hashtags = re.findall(r'#\w+', snippet.get('description', ''))
            
            # Get engagement metrics
            engagement_metrics = {}
            if stats_item and 'statistics' in stats_item:
                stats = stats_item['statistics']
                engagement_metrics = {
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'favorite_count': int(stats.get('favoriteCount', 0))
                }
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
            
            return SocialMediaPost(
                post_id=video_id,
                platform='youtube',
                author_handle=snippet['channelTitle'],
                author_id=snippet['channelId'],
                content=f"{snippet['title']}\n\n{snippet.get('description', '')[:500]}...",
                timestamp=timestamp,
                url=f"https://www.youtube.com/watch?v={video_id}",
                engagement_metrics=engagement_metrics,
                metadata={
                    'category_id': snippet.get('categoryId'),
                    'default_language': snippet.get('defaultLanguage'),
                    'duration': stats_item.get('contentDetails', {}).get('duration') if stats_item else None,
                    'source': 'youtube_api_v3'
                },
                media_urls=[f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"],
                hashtags=hashtags,
                mentions=[]
            )
            
        except Exception as e:
            logger.error(f"Error converting YouTube video: {e}")
            return None

class RedditConnector:
    """Reddit API connector"""
    
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'SentinelBERT/1.0')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Reddit API credentials not found in environment")
        
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
        self.rate_limiter = RateLimiter(60)  # 60 requests per minute
        
        logger.info("Reddit connector initialized")
    
    async def search_posts(self,
                         keywords: str,
                         max_results: int = 100,
                         time_filter: str = 'day',
                         subreddits: Optional[List[str]] = None) -> List[SocialMediaPost]:
        """Search Reddit posts"""
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            posts = []
            
            # Default subreddits for Indian content
            if not subreddits:
                subreddits = ['india', 'IndiaSpeaks', 'unitedstatesofindia', 'worldnews', 'news']
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search within subreddit
                    search_results = subreddit.search(
                        keywords,
                        sort='new',
                        time_filter=time_filter,
                        limit=max_results // len(subreddits)
                    )
                    
                    for submission in search_results:
                        try:
                            post = self._convert_submission_to_post(submission)
                            if post:
                                posts.append(post)
                        except Exception as e:
                            logger.error(f"Error converting Reddit post {submission.id}: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error searching subreddit {subreddit_name}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            posts.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"Retrieved {len(posts)} Reddit posts for query: {keywords}")
            return posts[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []
    
    def _convert_submission_to_post(self, submission) -> Optional[SocialMediaPost]:
        """Convert Reddit submission to standardized post"""
        try:
            # Extract content
            content = submission.title
            if submission.selftext:
                content += f"\n\n{submission.selftext[:1000]}..."
            
            # Get engagement metrics
            engagement_metrics = {
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'num_crossposts': getattr(submission, 'num_crossposts', 0)
            }
            
            # Extract media URLs
            media_urls = []
            if submission.url and not submission.is_self:
                media_urls.append(submission.url)
            
            return SocialMediaPost(
                post_id=submission.id,
                platform='reddit',
                author_handle=f"u/{submission.author.name}" if submission.author else "u/[deleted]",
                author_id=str(submission.author.id) if submission.author else "deleted",
                content=content,
                timestamp=datetime.fromtimestamp(submission.created_utc),
                url=f"https://reddit.com{submission.permalink}",
                engagement_metrics=engagement_metrics,
                metadata={
                    'subreddit': submission.subreddit.display_name,
                    'flair': submission.link_flair_text,
                    'is_self': submission.is_self,
                    'over_18': submission.over_18,
                    'spoiler': submission.spoiler,
                    'source': 'reddit_api'
                },
                media_urls=media_urls,
                hashtags=[],  # Reddit doesn't use hashtags
                mentions=[]
            )
            
        except Exception as e:
            logger.error(f"Error converting Reddit submission: {e}")
            return None

class SocialMediaAggregator:
    """Aggregates data from multiple social media platforms"""
    
    def __init__(self):
        self.connectors = {}
        
        # Initialize available connectors
        try:
            self.connectors['twitter'] = TwitterConnector()
        except Exception as e:
            logger.warning(f"Twitter connector not available: {e}")
        
        try:
            self.connectors['youtube'] = YouTubeConnector()
        except Exception as e:
            logger.warning(f"YouTube connector not available: {e}")
        
        try:
            self.connectors['reddit'] = RedditConnector()
        except Exception as e:
            logger.warning(f"Reddit connector not available: {e}")
        
        # Initialize Telegram connector if available
        if TELEGRAM_AVAILABLE:
            try:
                self.connectors['telegram'] = TelegramConnector()
            except Exception as e:
                logger.warning(f"Telegram connector not available: {e}")
        
        logger.info(f"Social Media Aggregator initialized with {len(self.connectors)} connectors")
    
    async def search_all_platforms(self,
                                 keywords: str,
                                 max_results_per_platform: int = 50,
                                 time_window_hours: int = 24,
                                 location: Optional[str] = None,
                                 platforms: Optional[List[str]] = None) -> List[SocialMediaPost]:
        """Search across all available platforms"""
        
        if not platforms:
            platforms = list(self.connectors.keys())
        
        start_time = datetime.now() - timedelta(hours=time_window_hours)
        all_posts = []
        
        # Search each platform concurrently
        tasks = []
        
        for platform in platforms:
            if platform not in self.connectors:
                logger.warning(f"Platform {platform} not available")
                continue
            
            connector = self.connectors[platform]
            
            if platform == 'twitter':
                task = connector.search_tweets(
                    keywords=keywords,
                    max_results=max_results_per_platform,
                    start_time=start_time,
                    location=location
                )
            elif platform == 'youtube':
                task = connector.search_videos(
                    keywords=keywords,
                    max_results=max_results_per_platform,
                    published_after=start_time,
                    region_code='IN' if location and 'india' in location.lower() else 'US'
                )
            elif platform == 'reddit':
                task = connector.search_posts(
                    keywords=keywords,
                    max_results=max_results_per_platform,
                    time_filter='day' if time_window_hours <= 24 else 'week'
                )
            elif platform == 'telegram':
                task = connector.search_hashtag(
                    hashtag=keywords,
                    limit=max_results_per_platform
                )
            else:
                continue
            
            tasks.append(task)
        
        # Execute all searches concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Platform search failed: {result}")
                elif isinstance(result, list):
                    all_posts.extend(result)
        
        # Sort all posts by timestamp (newest first)
        all_posts.sort(key=lambda x: x.timestamp, reverse=True)
        
        logger.info(f"Retrieved {len(all_posts)} total posts from {len(platforms)} platforms")
        return all_posts
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        return list(self.connectors.keys())