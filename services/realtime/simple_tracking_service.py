#!/usr/bin/env python3
"""
Simplified Enhanced Tracking Service for SentinelBERT
Optimized for Hackathon Demo - No Heavy ML Dependencies
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import time
import re
from urllib.parse import urlparse, parse_qs
import networkx as nx

# Import only essential services
from .social_media_connectors import TwitterConnector, SocialMediaPost

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrackingResult:
    """Result of viral content tracking"""
    original_post: Optional[SocialMediaPost]
    viral_chain: List[SocialMediaPost]
    network_graph: Dict[str, Any]
    timeline_analysis: Dict[str, Any]
    influence_metrics: Dict[str, Any]
    tracking_confidence: float
    api_calls_used: int
    processing_time: float

class SimpleTrackingService:
    """Simplified tracking service for hackathon demo"""
    
    def __init__(self):
        self.twitter_connector = TwitterConnector()
        self.api_call_count = 0
        self.max_api_calls = 20  # Conservative for demo
        
        logger.info("Simple Enhanced Tracking Service initialized")
    
    async def track_viral_origin(self, 
                                input_data: str, 
                                input_type: str = "auto") -> TrackingResult:
        """
        Main tracking function - finds original source of viral content
        """
        start_time = time.time()
        self.api_call_count = 0
        
        try:
            # Auto-detect input type if not specified
            if input_type == "auto":
                input_type = self._detect_input_type(input_data)
            
            logger.info(f"Starting viral origin tracking for {input_type}: {input_data}")
            
            # Route to appropriate tracking method
            if input_type == "post_url":
                result = await self._track_from_post_url(input_data)
            elif input_type == "username":
                result = await self._track_from_username(input_data)
            elif input_type == "hashtag":
                result = await self._track_from_hashtag(input_data)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.api_calls_used = self.api_call_count
            
            logger.info(f"Tracking completed in {processing_time:.2f}s using {self.api_call_count} API calls")
            return result
            
        except Exception as e:
            logger.error(f"Error in viral origin tracking: {e}")
            return TrackingResult(
                original_post=None,
                viral_chain=[],
                network_graph={},
                timeline_analysis={},
                influence_metrics={},
                tracking_confidence=0.0,
                api_calls_used=self.api_call_count,
                processing_time=time.time() - start_time
            )
    
    def _detect_input_type(self, input_data: str) -> str:
        """Auto-detect the type of input provided"""
        input_data = input_data.strip()
        
        if input_data.startswith('@'):
            return "username"
        elif input_data.startswith('#'):
            return "hashtag"
        elif 'twitter.com' in input_data or 'x.com' in input_data:
            return "post_url"
        elif input_data.startswith('http'):
            return "post_url"
        else:
            return "username"
    
    async def _track_from_post_url(self, post_url: str) -> TrackingResult:
        """Track viral origin from a specific post URL"""
        logger.info(f"Tracking from post URL: {post_url}")
        
        try:
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id_from_url(post_url)
            if not tweet_id:
                raise ValueError("Could not extract tweet ID from URL")
            
            # Get the specific tweet
            target_post = await self._get_tweet_by_id(tweet_id)
            if not target_post:
                raise ValueError("Could not retrieve tweet")
            
            # Simple reverse chronological trace
            viral_chain = [target_post]
            
            # Check if it's a retweet and get original
            if self._is_retweet(target_post):
                original_id = self._extract_original_tweet_id(target_post)
                if original_id:
                    original_post = await self._get_tweet_by_id(original_id)
                    if original_post:
                        viral_chain.insert(0, original_post)
            
            # Build simple network graph
            network_graph = self._build_simple_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Determine original post
            original_post = viral_chain[0] if viral_chain else target_post
            
            # Calculate confidence
            confidence = 0.9 if len(viral_chain) > 1 else 0.7
            
            return TrackingResult(
                original_post=original_post,
                viral_chain=viral_chain,
                network_graph=network_graph,
                timeline_analysis=timeline_analysis,
                influence_metrics=influence_metrics,
                tracking_confidence=confidence,
                api_calls_used=self.api_call_count,
                processing_time=0.0
            )
            
        except Exception as e:
            logger.error(f"Error tracking from post URL: {e}")
            raise
    
    async def _track_from_username(self, username: str) -> TrackingResult:
        """Track viral origin from a username"""
        logger.info(f"Tracking from username: {username}")
        
        try:
            # Clean username
            username = username.lstrip('@')
            
            # Get user's recent tweets
            user_posts = await self._get_user_timeline(username, max_results=5)
            if not user_posts:
                raise ValueError("Could not retrieve user timeline")
            
            # Use all posts as viral chain
            viral_chain = user_posts
            
            # Build network graph
            network_graph = self._build_simple_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Find most likely original post (earliest with highest engagement)
            original_post = self._find_original_post(viral_chain)
            
            # Calculate confidence
            confidence = 0.8 if len(viral_chain) > 1 else 0.6
            
            return TrackingResult(
                original_post=original_post,
                viral_chain=viral_chain,
                network_graph=network_graph,
                timeline_analysis=timeline_analysis,
                influence_metrics=influence_metrics,
                tracking_confidence=confidence,
                api_calls_used=self.api_call_count,
                processing_time=0.0
            )
            
        except Exception as e:
            logger.error(f"Error tracking from username: {e}")
            raise
    
    async def _track_from_hashtag(self, hashtag: str) -> TrackingResult:
        """Track viral origin from a hashtag"""
        logger.info(f"Tracking from hashtag: {hashtag}")
        
        try:
            # Clean hashtag
            hashtag = hashtag.lstrip('#')
            
            # Search for recent posts with hashtag
            hashtag_posts = await self._search_hashtag_posts(f"#{hashtag}", max_results=5)
            if not hashtag_posts:
                raise ValueError("No posts found for hashtag")
            
            # Sort by timestamp (earliest first)
            hashtag_posts.sort(key=lambda x: x.timestamp)
            viral_chain = hashtag_posts
            
            # Build network graph
            network_graph = self._build_simple_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Find original post (earliest)
            original_post = viral_chain[0] if viral_chain else None
            
            # Calculate confidence
            confidence = 0.7 if len(viral_chain) > 1 else 0.5
            
            return TrackingResult(
                original_post=original_post,
                viral_chain=viral_chain,
                network_graph=network_graph,
                timeline_analysis=timeline_analysis,
                influence_metrics=influence_metrics,
                tracking_confidence=confidence,
                api_calls_used=self.api_call_count,
                processing_time=0.0
            )
            
        except Exception as e:
            logger.error(f"Error tracking from hashtag: {e}")
            raise
    
    def _build_simple_network_graph(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Build simple network graph"""
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes (users)
            for post in posts:
                G.add_node(post.author_id, 
                          username=post.author_handle,
                          platform=post.platform,
                          influence_score=self._calculate_user_influence(post))
            
            # Add edges for mentions and retweets
            for post in posts:
                if post.mentions:
                    for mention in post.mentions:
                        # Simple edge for mentions
                        G.add_edge(post.author_id, f"@{mention}", 
                                 interaction_type="mention",
                                 weight=1.0)
            
            # Calculate simple metrics
            network_metrics = {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "density": nx.density(G) if G.number_of_nodes() > 0 else 0,
                "is_connected": nx.is_weakly_connected(G) if G.number_of_nodes() > 1 else True
            }
            
            # Find origin candidates
            origin_candidates = []
            for node_id in G.nodes():
                node_data = G.nodes[node_id]
                origin_candidates.append({
                    "user_id": node_id,
                    "username": node_data.get("username", ""),
                    "origin_score": node_data.get("influence_score", 0),
                    "influence_score": node_data.get("influence_score", 0)
                })
            
            # Sort by influence score
            origin_candidates.sort(key=lambda x: x["origin_score"], reverse=True)
            
            return {
                "graph_data": nx.node_link_data(G),
                "network_metrics": network_metrics,
                "origin_candidates": origin_candidates[:3]
            }
            
        except Exception as e:
            logger.error(f"Error building network graph: {e}")
            return {"error": str(e)}
    
    def _analyze_timeline(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        if not posts:
            return {}
        
        try:
            # Sort posts by timestamp
            sorted_posts = sorted(posts, key=lambda x: x.timestamp)
            
            # Calculate time span
            if len(sorted_posts) > 1:
                total_time = (sorted_posts[-1].timestamp - sorted_posts[0].timestamp).total_seconds()
                spread_velocity = len(posts) / max(total_time / 3600, 1)  # Posts per hour
            else:
                total_time = 0
                spread_velocity = 0
            
            # Analyze hourly activity
            hourly_activity = {}
            for post in posts:
                hour = post.timestamp.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
            
            return {
                "total_posts": len(posts),
                "time_span_hours": total_time / 3600,
                "spread_velocity": spread_velocity,
                "peak_activity_hour": peak_hour,
                "hourly_distribution": hourly_activity,
                "first_post_time": sorted_posts[0].timestamp.isoformat(),
                "last_post_time": sorted_posts[-1].timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeline: {e}")
            return {}
    
    def _calculate_influence_metrics(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Calculate influence metrics"""
        if not posts:
            return {}
        
        try:
            total_engagement = 0
            user_influence = {}
            
            for post in posts:
                engagement = sum(post.engagement_metrics.values())
                total_engagement += engagement
                
                user_id = post.author_id
                if user_id not in user_influence:
                    user_influence[user_id] = {
                        "username": post.author_handle,
                        "total_engagement": 0,
                        "post_count": 0
                    }
                
                user_influence[user_id]["total_engagement"] += engagement
                user_influence[user_id]["post_count"] += 1
            
            # Calculate influence scores
            for user_id, data in user_influence.items():
                data["avg_engagement"] = data["total_engagement"] / data["post_count"]
                data["influence_score"] = data["avg_engagement"]
            
            # Sort by influence
            top_influencers = sorted(user_influence.items(), 
                                   key=lambda x: x[1]["influence_score"], 
                                   reverse=True)
            
            return {
                "total_engagement": total_engagement,
                "average_engagement": total_engagement / len(posts),
                "unique_users": len(user_influence),
                "top_influencers": dict(top_influencers[:3]),
                "viral_coefficient": len([p for p in posts if self._is_retweet(p)]) / max(len(posts), 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating influence metrics: {e}")
            return {}
    
    # Helper methods
    def _extract_tweet_id_from_url(self, url: str) -> Optional[str]:
        """Extract tweet ID from Twitter URL"""
        try:
            patterns = [
                r'twitter\.com/\w+/status/(\d+)',
                r'x\.com/\w+/status/(\d+)',
                r'/status/(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting tweet ID: {e}")
            return None
    
    async def _get_tweet_by_id(self, tweet_id: str) -> Optional[SocialMediaPost]:
        """Get a specific tweet by ID"""
        if self.api_call_count >= self.max_api_calls:
            logger.warning("API call limit reached")
            return None
        
        try:
            self.api_call_count += 1
            post = await self.twitter_connector.get_tweet_by_id(tweet_id)
            return post
        except Exception as e:
            logger.error(f"Error getting tweet by ID {tweet_id}: {e}")
            return None
    
    async def _get_user_timeline(self, username: str, max_results: int = 5) -> List[SocialMediaPost]:
        """Get user's recent timeline"""
        if self.api_call_count >= self.max_api_calls:
            logger.warning("API call limit reached")
            return []
        
        try:
            self.api_call_count += 1
            posts = await self.twitter_connector.get_user_timeline(username, max_results)
            return posts
        except Exception as e:
            logger.error(f"Error getting user timeline for {username}: {e}")
            return []
    
    async def _search_hashtag_posts(self, hashtag: str, max_results: int = 5) -> List[SocialMediaPost]:
        """Search for posts with specific hashtag"""
        if self.api_call_count >= self.max_api_calls:
            logger.warning("API call limit reached")
            return []
        
        try:
            self.api_call_count += 1
            return await self.twitter_connector.search_tweets(
                keywords=hashtag,
                max_results=max_results
            )
        except Exception as e:
            logger.error(f"Error searching hashtag posts: {e}")
            return []
    
    def _is_retweet(self, post: SocialMediaPost) -> bool:
        """Check if post is a retweet"""
        return (post.content.startswith('RT @') or 
                'retweeted_status' in post.metadata or
                'referenced_tweets' in post.metadata)
    
    def _extract_original_tweet_id(self, post: SocialMediaPost) -> Optional[str]:
        """Extract original tweet ID from retweet"""
        try:
            # Check metadata for referenced tweets
            if 'referenced_tweets' in post.metadata:
                for ref in post.metadata['referenced_tweets']:
                    if ref.get('type') in ['retweeted', 'quoted']:
                        return ref.get('id')
            
            return None
        except Exception as e:
            logger.error(f"Error extracting original tweet ID: {e}")
            return None
    
    def _find_original_post(self, posts: List[SocialMediaPost]) -> Optional[SocialMediaPost]:
        """Find the most likely original post"""
        if not posts:
            return None
        
        try:
            # Sort by timestamp (earliest first) and engagement
            scored_posts = []
            for post in posts:
                engagement = sum(post.engagement_metrics.values())
                # Earlier posts get higher time scores
                time_score = 1.0
                # Non-retweets get higher originality scores
                originality_score = 2.0 if not self._is_retweet(post) else 1.0
                
                total_score = engagement * 0.4 + time_score * 0.3 + originality_score * 0.3
                scored_posts.append((post, total_score))
            
            # Sort by score and return highest
            scored_posts.sort(key=lambda x: x[1], reverse=True)
            return scored_posts[0][0]
            
        except Exception as e:
            logger.error(f"Error finding original post: {e}")
            return posts[0] if posts else None
    
    def _calculate_user_influence(self, post: SocialMediaPost) -> float:
        """Calculate user influence score"""
        try:
            engagement = sum(post.engagement_metrics.values())
            # Simple influence score based on engagement
            return min(engagement / 100.0, 1.0)  # Normalize to 0-1
        except Exception as e:
            logger.error(f"Error calculating user influence: {e}")
            return 0.0