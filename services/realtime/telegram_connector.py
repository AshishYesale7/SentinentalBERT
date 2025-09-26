#!/usr/bin/env python3
"""
Telegram MTProto Connector for SentinelBERT
Uses Telethon for full MTProto client capability with public channel access
"""

import os
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import time
import re

# Telegram MTProto client
from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
    MessageFwdHeader, PeerChannel, PeerUser, PeerChat
)
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

# Environment and utilities
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TelegramPost:
    """Standardized Telegram post structure"""
    post_id: str
    channel_id: str
    channel_username: str
    author_id: str
    content: str
    timestamp: datetime
    url: str
    engagement_metrics: Dict[str, int]
    metadata: Dict[str, Any]
    forward_info: Optional[Dict[str, Any]] = None
    media_urls: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    content_hash: str = None
    
    def __post_init__(self):
        """Generate content hash for deduplication"""
        if not self.content_hash:
            content_for_hash = f"{self.content}{self.timestamp.isoformat()}"
            self.content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class TelegramConnector:
    """Telegram MTProto connector with full client capability"""
    
    def __init__(self):
        # Load Telegram API credentials
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '27248258'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '7bddc3e66acfc2679592796cecb9eb8a')
        
        # Session file path
        self.session_name = 'sentinelbert_telegram'
        
        # Initialize client
        self.client = None
        self.is_connected = False
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        logger.info("Telegram MTProto connector initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize Telegram client and authenticate"""
        try:
            # Create client
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash,
                device_model='SentinelBERT',
                system_version='1.0',
                app_version='1.0',
                lang_code='en',
                system_lang_code='en'
            )
            
            # Connect to Telegram
            await self.client.connect()
            
            # Check if we're authorized
            if not await self.client.is_user_authorized():
                logger.warning("Telegram client not authorized - manual authentication required")
                return {
                    "status": "auth_required",
                    "message": "Manual authentication required for Telegram client"
                }
            
            self.is_connected = True
            
            # Get current user info
            me = await self.client.get_me()
            
            logger.info(f"Telegram client connected as: {me.first_name} (@{me.username})")
            
            return {
                "status": "connected",
                "user": {
                    "id": me.id,
                    "username": me.username,
                    "first_name": me.first_name,
                    "phone": me.phone
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def authenticate_with_phone(self, phone_number: str) -> Dict[str, Any]:
        """Authenticate with phone number (for first-time setup)"""
        try:
            if not self.client:
                await self.initialize()
            
            # Send code request
            await self.client.send_code_request(phone_number)
            
            return {
                "status": "code_sent",
                "message": "Verification code sent to phone"
            }
            
        except Exception as e:
            logger.error(f"Failed to send verification code: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def verify_code(self, phone_number: str, code: str, password: str = None) -> Dict[str, Any]:
        """Verify authentication code"""
        try:
            if not self.client:
                await self.initialize()
            
            # Sign in with code
            try:
                await self.client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                if password:
                    await self.client.sign_in(password=password)
                else:
                    return {
                        "status": "password_required",
                        "message": "Two-factor authentication password required"
                    }
            
            self.is_connected = True
            me = await self.client.get_me()
            
            return {
                "status": "authenticated",
                "user": {
                    "id": me.id,
                    "username": me.username,
                    "first_name": me.first_name
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to verify code: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def search_channels(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for public channels"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            await self.rate_limit_wait()
            
            # Search for channels
            results = await self.client.get_dialogs(limit=limit)
            
            channels = []
            for dialog in results:
                if hasattr(dialog.entity, 'username') and dialog.entity.username:
                    if query.lower() in dialog.entity.title.lower():
                        channels.append({
                            "id": dialog.entity.id,
                            "username": dialog.entity.username,
                            "title": dialog.entity.title,
                            "participants_count": getattr(dialog.entity, 'participants_count', 0)
                        })
            
            return channels
            
        except Exception as e:
            logger.error(f"Failed to search channels: {e}")
            return []
    
    async def get_channel_history(self, channel_username: str, limit: int = 100, 
                                 hours_back: int = 24) -> List[TelegramPost]:
        """Get channel message history"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            await self.rate_limit_wait()
            
            # Get channel entity
            try:
                channel = await self.client.get_entity(channel_username)
            except Exception as e:
                logger.error(f"Failed to get channel {channel_username}: {e}")
                return []
            
            # Calculate time range
            offset_date = datetime.now() - timedelta(hours=hours_back)
            
            posts = []
            
            try:
                # Get messages
                async for message in self.client.iter_messages(
                    channel, 
                    limit=limit,
                    offset_date=offset_date
                ):
                    if message.text or message.media:
                        post = await self._convert_message_to_post(message, channel)
                        if post:
                            posts.append(post)
                
            except FloodWaitError as e:
                logger.warning(f"Rate limited, waiting {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                return []
            
            logger.info(f"Retrieved {len(posts)} posts from {channel_username}")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get channel history: {e}")
            return []
    
    async def search_hashtag(self, hashtag: str, max_results: int = 100) -> List[TelegramPost]:
        """Search for posts with specific hashtag across accessible channels"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            posts = []
            
            # Get all accessible dialogs
            dialogs = await self.client.get_dialogs()
            
            for dialog in dialogs:
                if hasattr(dialog.entity, 'broadcast') and dialog.entity.broadcast:
                    # This is a channel
                    try:
                        await self.rate_limit_wait()
                        
                        async for message in self.client.iter_messages(
                            dialog.entity,
                            limit=50,  # Limit per channel
                            search=hashtag
                        ):
                            if hashtag.lower() in (message.text or "").lower():
                                post = await self._convert_message_to_post(message, dialog.entity)
                                if post:
                                    posts.append(post)
                                    
                                    if len(posts) >= max_results:
                                        break
                        
                        if len(posts) >= max_results:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to search in channel {dialog.entity.title}: {e}")
                        continue
            
            logger.info(f"Found {len(posts)} posts with hashtag {hashtag}")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to search hashtag: {e}")
            return []
    
    async def _convert_message_to_post(self, message, channel) -> Optional[TelegramPost]:
        """Convert Telegram message to standardized post format"""
        try:
            # Extract content
            content = message.text or ""
            if message.media and hasattr(message.media, 'caption'):
                content = message.media.caption or content
            
            # Skip empty messages
            if not content.strip():
                return None
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', content)
            mentions = re.findall(r'@\w+', content)
            
            # Extract media URLs
            media_urls = []
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_urls.append("photo")
                elif isinstance(message.media, MessageMediaDocument):
                    media_urls.append("document")
                elif isinstance(message.media, MessageMediaWebPage):
                    if message.media.webpage.url:
                        media_urls.append(message.media.webpage.url)
            
            # Extract forward information
            forward_info = None
            if message.fwd_from:
                forward_info = {
                    "from_id": getattr(message.fwd_from, 'from_id', None),
                    "from_name": getattr(message.fwd_from, 'from_name', None),
                    "channel_post": getattr(message.fwd_from, 'channel_post', None),
                    "post_author": getattr(message.fwd_from, 'post_author', None),
                    "saved_from_peer": getattr(message.fwd_from, 'saved_from_peer', None),
                    "saved_from_msg_id": getattr(message.fwd_from, 'saved_from_msg_id', None),
                    "date": getattr(message.fwd_from, 'date', None)
                }
            
            # Create post URL
            channel_username = getattr(channel, 'username', None)
            if channel_username:
                url = f"https://t.me/{channel_username}/{message.id}"
            else:
                url = f"https://t.me/c/{channel.id}/{message.id}"
            
            # Engagement metrics
            engagement_metrics = {
                "views": getattr(message, 'views', 0),
                "forwards": getattr(message, 'forwards', 0),
                "replies": getattr(message, 'replies', {}).get('replies', 0) if hasattr(message, 'replies') and message.replies else 0
            }
            
            # Metadata
            metadata = {
                "message_id": message.id,
                "edit_date": message.edit_date.isoformat() if message.edit_date else None,
                "grouped_id": message.grouped_id,
                "restriction_reason": getattr(message, 'restriction_reason', None),
                "ttl_period": getattr(message, 'ttl_period', None)
            }
            
            return TelegramPost(
                post_id=str(message.id),
                channel_id=str(channel.id),
                channel_username=channel_username or str(channel.id),
                author_id=str(message.from_id) if message.from_id else "unknown",
                content=content,
                timestamp=message.date,
                url=url,
                engagement_metrics=engagement_metrics,
                metadata=metadata,
                forward_info=forward_info,
                media_urls=media_urls,
                hashtags=hashtags,
                mentions=mentions
            )
            
        except Exception as e:
            logger.error(f"Failed to convert message to post: {e}")
            return None
    
    async def monitor_channels(self, channel_usernames: List[str], 
                              callback=None) -> None:
        """Monitor channels for new messages in real-time"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            # Add event handler for new messages
            @self.client.on(events.NewMessage)
            async def handler(event):
                try:
                    # Check if message is from monitored channels
                    if hasattr(event.chat, 'username') and event.chat.username in channel_usernames:
                        post = await self._convert_message_to_post(event.message, event.chat)
                        if post and callback:
                            await callback(post)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
            
            logger.info(f"Started monitoring {len(channel_usernames)} channels")
            
            # Keep the client running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to monitor channels: {e}")
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        try:
            if self.client and self.is_connected:
                await self.client.disconnect()
                self.is_connected = False
                logger.info("Telegram client disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

# Utility functions for integration
async def fetch_channel_history(channel_username: str, limit: int = 100, 
                               hours_back: int = 24) -> List[Dict[str, Any]]:
    """Standalone function to fetch channel history"""
    connector = TelegramConnector()
    try:
        await connector.initialize()
        posts = await connector.get_channel_history(channel_username, limit, hours_back)
        return [post.to_dict() for post in posts]
    finally:
        await connector.disconnect()

async def search_telegram_hashtag(hashtag: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Standalone function to search hashtag"""
    connector = TelegramConnector()
    try:
        await connector.initialize()
        posts = await connector.search_hashtag(hashtag, limit)
        return [post.to_dict() for post in posts]
    finally:
        await connector.disconnect()

# Example usage
if __name__ == "__main__":
    async def main():
        connector = TelegramConnector()
        
        # Initialize
        result = await connector.initialize()
        print(f"Initialization result: {result}")
        
        if result["status"] == "connected":
            # Search for posts with hashtag
            posts = await connector.search_hashtag("#SentinentalBERT", limit=10)
            print(f"Found {len(posts)} posts")
            
            for post in posts[:3]:  # Show first 3
                print(f"Channel: {post.channel_username}")
                print(f"Content: {post.content[:100]}...")
                print(f"URL: {post.url}")
                print("---")
        
        await connector.disconnect()
    
    asyncio.run(main())