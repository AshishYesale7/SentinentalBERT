"""
Cloud Function for Twitter/X.com data ingestion
Fetches tweets and publishes to Pub/Sub for processing
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import functions_framework
import tweepy
from google.cloud import pubsub_v1
from google.cloud import secretmanager
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PROJECT_ID = os.environ.get('GCP_PROJECT')
PUBSUB_TOPIC = os.environ.get('PUBSUB_TOPIC', 'social-media-raw-dev')
STORAGE_BUCKET = os.environ.get('STORAGE_BUCKET')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

# Initialize clients
publisher = pubsub_v1.PublisherClient()
secret_client = secretmanager.SecretManagerServiceClient()
storage_client = storage.Client()

def get_secret(secret_id: str) -> str:
    """Retrieve secret from Secret Manager"""
    try:
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_id}: {e}")
        raise

def get_twitter_client() -> tweepy.Client:
    """Initialize Twitter API client"""
    bearer_token = get_secret(f'twitter-bearer-token-{ENVIRONMENT}')
    return tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

def format_tweet_data(tweet: tweepy.Tweet, includes: Dict = None) -> Dict:
    """Format tweet data for processing"""
    # Extract user information
    user_info = {}
    if includes and 'users' in includes:
        for user in includes['users']:
            if user.id == tweet.author_id:
                user_info = {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.name,
                    'followers_count': user.public_metrics.get('followers_count', 0),
                    'verified': user.verified,
                    'description': user.description,
                    'location': user.location,
                    'profile_image_url': user.profile_image_url
                }
                break

    # Extract media information
    media_urls = []
    if includes and 'media' in includes:
        for media in includes['media']:
            if hasattr(tweet, 'attachments') and tweet.attachments:
                if media.media_key in tweet.attachments.get('media_keys', []):
                    media_urls.append({
                        'url': media.url,
                        'type': media.type,
                        'preview_image_url': getattr(media, 'preview_image_url', None)
                    })

    # Extract location information
    location_info = {}
    if hasattr(tweet, 'geo') and tweet.geo:
        location_info = {
            'place_id': tweet.geo.get('place_id'),
            'coordinates': tweet.geo.get('coordinates')
        }

    # Format the tweet data
    formatted_data = {
        'post_id': str(tweet.id),
        'platform': 'twitter',
        'author_id': str(tweet.author_id),
        'author_info': user_info,
        'content': tweet.text,
        'content_type': 'text',
        'language': tweet.lang,
        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
        'ingested_at': datetime.utcnow().isoformat(),
        'url': f"https://twitter.com/i/status/{tweet.id}",
        'engagement_metrics': {
            'likes': tweet.public_metrics.get('like_count', 0),
            'retweets': tweet.public_metrics.get('retweet_count', 0),
            'replies': tweet.public_metrics.get('reply_count', 0),
            'quotes': tweet.public_metrics.get('quote_count', 0)
        },
        'location': location_info,
        'hashtags': [tag['tag'] for tag in tweet.entities.get('hashtags', [])],
        'mentions': [mention['username'] for mention in tweet.entities.get('mentions', [])],
        'media_urls': media_urls,
        'is_retweet': hasattr(tweet, 'referenced_tweets') and 
                     any(ref.type == 'retweeted' for ref in tweet.referenced_tweets or []),
        'is_reply': tweet.in_reply_to_user_id is not None,
        'parent_post_id': None,
        'raw_data': tweet.data if hasattr(tweet, 'data') else {}
    }

    # Handle referenced tweets (retweets, replies, quotes)
    if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
        for ref in tweet.referenced_tweets:
            if ref.type in ['retweeted', 'replied_to', 'quoted']:
                formatted_data['parent_post_id'] = str(ref.id)
                break

    return formatted_data

def publish_to_pubsub(data: Dict) -> None:
    """Publish data to Pub/Sub topic"""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
        message_data = json.dumps(data, default=str).encode('utf-8')
        
        # Add attributes for routing and filtering
        attributes = {
            'platform': data.get('platform', 'unknown'),
            'content_type': data.get('content_type', 'text'),
            'language': data.get('language', 'unknown'),
            'ingestion_timestamp': str(int(datetime.utcnow().timestamp()))
        }
        
        future = publisher.publish(topic_path, message_data, **attributes)
        message_id = future.result()
        logger.info(f"Published message {message_id} to {PUBSUB_TOPIC}")
        
    except Exception as e:
        logger.error(f"Error publishing to Pub/Sub: {e}")
        raise

def store_raw_data(data: Dict) -> None:
    """Store raw data in Cloud Storage for backup"""
    if not STORAGE_BUCKET:
        return
        
    try:
        bucket = storage_client.bucket(STORAGE_BUCKET)
        
        # Create a path based on date and platform
        now = datetime.utcnow()
        blob_path = f"raw-data/twitter/{now.year}/{now.month:02d}/{now.day:02d}/{data['post_id']}.json"
        
        blob = bucket.blob(blob_path)
        blob.upload_from_string(
            json.dumps(data, default=str, indent=2),
            content_type='application/json'
        )
        
        logger.info(f"Stored raw data at gs://{STORAGE_BUCKET}/{blob_path}")
        
    except Exception as e:
        logger.error(f"Error storing raw data: {e}")
        # Don't raise here as this is not critical

def search_tweets(query: str, max_results: int = 100) -> List[Dict]:
    """Search for tweets and return formatted data"""
    try:
        client = get_twitter_client()
        
        # Define tweet fields to retrieve
        tweet_fields = [
            'id', 'text', 'author_id', 'created_at', 'lang', 'public_metrics',
            'entities', 'geo', 'in_reply_to_user_id', 'referenced_tweets',
            'reply_settings', 'source', 'withheld'
        ]
        
        user_fields = [
            'id', 'username', 'name', 'description', 'location', 'verified',
            'public_metrics', 'profile_image_url', 'protected'
        ]
        
        media_fields = ['media_key', 'type', 'url', 'preview_image_url']
        
        # Search for tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            media_fields=media_fields,
            expansions=['author_id', 'attachments.media_keys', 'geo.place_id']
        )
        
        if not tweets.data:
            logger.info("No tweets found for query")
            return []
        
        # Format and process tweets
        formatted_tweets = []
        includes = tweets.includes or {}
        
        for tweet in tweets.data:
            try:
                formatted_data = format_tweet_data(tweet, includes)
                formatted_tweets.append(formatted_data)
                
                # Publish to Pub/Sub
                publish_to_pubsub(formatted_data)
                
                # Store raw data
                store_raw_data(formatted_data)
                
            except Exception as e:
                logger.error(f"Error processing tweet {tweet.id}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(formatted_tweets)} tweets")
        return formatted_tweets
        
    except Exception as e:
        logger.error(f"Error searching tweets: {e}")
        raise

@functions_framework.http
def twitter_ingestion(request):
    """HTTP Cloud Function for Twitter data ingestion"""
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return {'error': 'No JSON payload provided'}, 400
        
        # Extract parameters
        query = request_json.get('query')
        max_results = request_json.get('max_results', 100)
        
        if not query:
            return {'error': 'Query parameter is required'}, 400
        
        # Validate max_results
        if max_results > 500:  # Twitter API limit
            max_results = 500
        
        logger.info(f"Starting Twitter ingestion for query: {query}")
        
        # Search and process tweets
        tweets = search_tweets(query, max_results)
        
        response = {
            'status': 'success',
            'query': query,
            'tweets_processed': len(tweets),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Twitter ingestion completed: {len(tweets)} tweets processed")
        return response, 200
        
    except Exception as e:
        logger.error(f"Error in Twitter ingestion: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 500

@functions_framework.cloud_event
def twitter_scheduled_ingestion(cloud_event):
    """Cloud Event function for scheduled Twitter ingestion"""
    try:
        # Default queries for scheduled ingestion
        default_queries = [
            "climate change -is:retweet lang:en",
            "artificial intelligence -is:retweet lang:en",
            "social media trends -is:retweet lang:en",
            "breaking news -is:retweet lang:en"
        ]
        
        total_tweets = 0
        
        for query in default_queries:
            try:
                logger.info(f"Processing scheduled query: {query}")
                tweets = search_tweets(query, max_results=50)
                total_tweets += len(tweets)
                
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                continue
        
        logger.info(f"Scheduled Twitter ingestion completed: {total_tweets} total tweets processed")
        
    except Exception as e:
        logger.error(f"Error in scheduled Twitter ingestion: {e}")
        raise