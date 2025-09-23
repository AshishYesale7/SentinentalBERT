#!/usr/bin/env python3
"""
Enhanced Tracking Service for SentinelBERT
Implements Reverse Chronological Tracing and Advanced Network Traversal
Optimized for Indian Police Hackathon Demo
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
import pandas as pd
import numpy as np

# Import existing services
from .social_media_connectors import TwitterConnector, SocialMediaPost
from ..nlp.models.sentiment_model import SentimentAnalyzer

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

@dataclass
class OriginNode:
    """Represents a potential origin node in viral spread"""
    user_id: str
    username: str
    platform: str
    post_id: str
    timestamp: datetime
    content: str
    confidence_score: float
    evidence_strength: float
    retweet_chain_length: int
    influence_indicators: Dict[str, Any]

class EnhancedTrackingService:
    """Enhanced tracking service with reverse chronological tracing"""
    
    def __init__(self):
        self.twitter_connector = TwitterConnector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.api_call_count = 0
        self.max_api_calls = 50  # Conservative limit for demo
        
        logger.info("Enhanced Tracking Service initialized")
    
    async def track_viral_origin(self, 
                                input_data: str, 
                                input_type: str = "auto") -> TrackingResult:
        """
        Main tracking function - finds original source of viral content
        
        Args:
            input_data: Username (@user), post URL, or hashtag
            input_type: "username", "post_url", "hashtag", or "auto"
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
            # Default to username if no clear indicator
            return "username"
    
    async def _track_from_post_url(self, post_url: str) -> TrackingResult:
        """
        Track viral origin from a specific post URL
        Uses Direct Retweet Chain Traversal - Most efficient for demo
        """
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
            
            # Apply Reverse Chronological Tracing
            viral_chain = await self._reverse_chronological_trace(target_post)
            
            # Build network graph
            network_graph = await self._build_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Determine original post (earliest in chain)
            original_post = viral_chain[0] if viral_chain else target_post
            
            # Calculate confidence score
            confidence = self._calculate_tracking_confidence(viral_chain, "post_url")
            
            return TrackingResult(
                original_post=original_post,
                viral_chain=viral_chain,
                network_graph=network_graph,
                timeline_analysis=timeline_analysis,
                influence_metrics=influence_metrics,
                tracking_confidence=confidence,
                api_calls_used=self.api_call_count,
                processing_time=0.0  # Will be set by caller
            )
            
        except Exception as e:
            logger.error(f"Error tracking from post URL: {e}")
            raise
    
    async def _track_from_username(self, username: str) -> TrackingResult:
        """
        Track viral origin from a username
        Uses Timeline Analysis with Content Similarity
        """
        logger.info(f"Tracking from username: {username}")
        
        try:
            # Clean username
            username = username.lstrip('@')
            
            # Get user's recent tweets
            user_posts = await self._get_user_timeline(username, max_results=20)
            if not user_posts:
                raise ValueError("Could not retrieve user timeline")
            
            # Find potential viral content (high engagement)
            viral_candidates = self._identify_viral_candidates(user_posts)
            
            if not viral_candidates:
                # If no clear viral content, analyze all posts
                viral_candidates = user_posts[:5]  # Top 5 recent posts
            
            # For each candidate, perform reverse chronological tracing
            all_chains = []
            for candidate in viral_candidates:
                chain = await self._reverse_chronological_trace(candidate)
                if chain:
                    all_chains.extend(chain)
            
            # Combine and deduplicate
            viral_chain = self._deduplicate_posts(all_chains)
            
            # Build network graph
            network_graph = await self._build_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Find original post
            original_post = self._find_original_post(viral_chain)
            
            # Calculate confidence
            confidence = self._calculate_tracking_confidence(viral_chain, "username")
            
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
        """
        Track viral origin from a hashtag
        Uses Content Similarity with Timestamp Analysis
        """
        logger.info(f"Tracking from hashtag: {hashtag}")
        
        try:
            # Clean hashtag
            hashtag = hashtag.lstrip('#')
            
            # Search for recent posts with hashtag
            hashtag_posts = await self._search_hashtag_posts(f"#{hashtag}", max_results=50)
            if not hashtag_posts:
                raise ValueError("No posts found for hashtag")
            
            # Sort by timestamp (earliest first)
            hashtag_posts.sort(key=lambda x: x.timestamp)
            
            # Group similar content
            content_clusters = self._cluster_similar_content(hashtag_posts)
            
            # For each cluster, find the earliest post (potential origin)
            viral_chain = []
            for cluster in content_clusters:
                cluster_sorted = sorted(cluster, key=lambda x: x.timestamp)
                viral_chain.extend(cluster_sorted)
            
            # Build network graph
            network_graph = await self._build_network_graph(viral_chain)
            
            # Analyze timeline
            timeline_analysis = self._analyze_timeline(viral_chain)
            
            # Calculate influence metrics
            influence_metrics = self._calculate_influence_metrics(viral_chain)
            
            # Find original post (earliest with highest influence)
            original_post = self._find_original_post(viral_chain)
            
            # Calculate confidence
            confidence = self._calculate_tracking_confidence(viral_chain, "hashtag")
            
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
    
    async def _reverse_chronological_trace(self, target_post: SocialMediaPost) -> List[SocialMediaPost]:
        """
        Core Reverse Chronological Tracing Algorithm
        Traces back through retweet chains and similar content
        """
        logger.info(f"Starting reverse chronological trace for post {target_post.post_id}")
        
        traced_posts = [target_post]
        current_post = target_post
        
        try:
            # Check if this is a retweet/quote tweet
            if self._is_retweet(current_post):
                # Direct retweet chain traversal
                original_id = self._extract_original_tweet_id(current_post)
                if original_id:
                    original_post = await self._get_tweet_by_id(original_id)
                    if original_post:
                        traced_posts.insert(0, original_post)  # Add to beginning
                        logger.info(f"Found original tweet: {original_id}")
            
            # Search for similar content posted earlier
            similar_posts = await self._find_similar_earlier_posts(current_post)
            
            # Add similar posts to chain, sorted by timestamp
            for post in similar_posts:
                if post.timestamp < current_post.timestamp:
                    traced_posts.insert(0, post)
            
            # Remove duplicates and sort by timestamp
            traced_posts = self._deduplicate_posts(traced_posts)
            traced_posts.sort(key=lambda x: x.timestamp)
            
            logger.info(f"Reverse chronological trace found {len(traced_posts)} posts in chain")
            return traced_posts
            
        except Exception as e:
            logger.error(f"Error in reverse chronological trace: {e}")
            return [target_post]  # Return at least the target post
    
    async def _build_network_graph(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """
        Build network graph from posts using NetworkX
        Enhanced Network Traversal Algorithm
        """
        logger.info(f"Building network graph from {len(posts)} posts")
        
        try:
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes (users)
            for post in posts:
                G.add_node(post.author_id, 
                          username=post.author_handle,
                          platform=post.platform,
                          post_count=1,
                          earliest_post=post.timestamp,
                          influence_score=self._calculate_user_influence(post))
            
            # Add edges (interactions)
            for i, post in enumerate(posts):
                # Connect to mentions
                if post.mentions:
                    for mention in post.mentions:
                        if mention in [p.author_handle for p in posts]:
                            target_id = next((p.author_id for p in posts if p.author_handle == mention), None)
                            if target_id:
                                G.add_edge(post.author_id, target_id, 
                                         interaction_type="mention",
                                         timestamp=post.timestamp,
                                         weight=1.0)
                
                # Connect retweet chains
                if self._is_retweet(post):
                    original_id = self._extract_original_tweet_id(post)
                    if original_id:
                        original_author = next((p.author_id for p in posts if p.post_id == original_id), None)
                        if original_author:
                            G.add_edge(original_author, post.author_id,
                                     interaction_type="retweet",
                                     timestamp=post.timestamp,
                                     weight=2.0)
            
            # Calculate network metrics
            network_metrics = {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "density": nx.density(G),
                "is_connected": nx.is_weakly_connected(G),
                "diameter": self._safe_diameter(G),
                "clustering_coefficient": nx.average_clustering(G.to_undirected())
            }
            
            # Find central nodes
            try:
                centrality = nx.degree_centrality(G)
                betweenness = nx.betweenness_centrality(G)
                closeness = nx.closeness_centrality(G)
            except:
                centrality = betweenness = closeness = {}
            
            # Identify origin nodes (high centrality, early timestamp)
            origin_candidates = []
            for node_id in G.nodes():
                node_data = G.nodes[node_id]
                origin_score = (
                    centrality.get(node_id, 0) * 0.4 +
                    betweenness.get(node_id, 0) * 0.3 +
                    closeness.get(node_id, 0) * 0.3
                )
                
                origin_candidates.append({
                    "user_id": node_id,
                    "username": node_data.get("username", ""),
                    "origin_score": origin_score,
                    "earliest_post": node_data.get("earliest_post"),
                    "influence_score": node_data.get("influence_score", 0)
                })
            
            # Sort by origin score
            origin_candidates.sort(key=lambda x: x["origin_score"], reverse=True)
            
            return {
                "graph_data": nx.node_link_data(G),
                "network_metrics": network_metrics,
                "origin_candidates": origin_candidates[:5],  # Top 5
                "centrality_scores": centrality,
                "betweenness_scores": betweenness,
                "closeness_scores": closeness
            }
            
        except Exception as e:
            logger.error(f"Error building network graph: {e}")
            return {"error": str(e)}
    
    def _analyze_timeline(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Analyze temporal patterns in viral spread"""
        if not posts:
            return {}
        
        try:
            # Sort posts by timestamp
            sorted_posts = sorted(posts, key=lambda x: x.timestamp)
            
            # Calculate time intervals
            intervals = []
            for i in range(1, len(sorted_posts)):
                interval = (sorted_posts[i].timestamp - sorted_posts[i-1].timestamp).total_seconds()
                intervals.append(interval)
            
            # Analyze spread velocity
            total_time = (sorted_posts[-1].timestamp - sorted_posts[0].timestamp).total_seconds()
            spread_velocity = len(posts) / max(total_time / 3600, 1)  # Posts per hour
            
            # Identify peak activity periods
            hourly_activity = {}
            for post in posts:
                hour = post.timestamp.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
            
            return {
                "total_posts": len(posts),
                "time_span_hours": total_time / 3600,
                "spread_velocity": spread_velocity,
                "average_interval_minutes": np.mean(intervals) / 60 if intervals else 0,
                "peak_activity_hour": peak_hour,
                "hourly_distribution": hourly_activity,
                "first_post_time": sorted_posts[0].timestamp.isoformat(),
                "last_post_time": sorted_posts[-1].timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeline: {e}")
            return {}
    
    def _calculate_influence_metrics(self, posts: List[SocialMediaPost]) -> Dict[str, Any]:
        """Calculate influence metrics for the viral chain"""
        if not posts:
            return {}
        
        try:
            # User influence scores
            user_influence = {}
            total_engagement = 0
            
            for post in posts:
                user_id = post.author_id
                engagement = sum(post.engagement_metrics.values())
                total_engagement += engagement
                
                if user_id not in user_influence:
                    user_influence[user_id] = {
                        "username": post.author_handle,
                        "total_engagement": 0,
                        "post_count": 0,
                        "avg_engagement": 0,
                        "influence_score": 0
                    }
                
                user_influence[user_id]["total_engagement"] += engagement
                user_influence[user_id]["post_count"] += 1
            
            # Calculate average engagement and influence scores
            for user_id, data in user_influence.items():
                data["avg_engagement"] = data["total_engagement"] / data["post_count"]
                data["influence_score"] = data["avg_engagement"] * np.log(data["post_count"] + 1)
            
            # Sort by influence score
            top_influencers = sorted(user_influence.items(), 
                                   key=lambda x: x[1]["influence_score"], 
                                   reverse=True)
            
            return {
                "total_engagement": total_engagement,
                "average_engagement": total_engagement / len(posts),
                "unique_users": len(user_influence),
                "top_influencers": dict(top_influencers[:5]),
                "engagement_distribution": [sum(p.engagement_metrics.values()) for p in posts],
                "viral_coefficient": self._calculate_viral_coefficient(posts)
            }
            
        except Exception as e:
            logger.error(f"Error calculating influence metrics: {e}")
            return {}
    
    # Helper methods
    def _extract_tweet_id_from_url(self, url: str) -> Optional[str]:
        """Extract tweet ID from Twitter URL"""
        try:
            # Handle both twitter.com and x.com URLs
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
            # Use Twitter connector's optimized method
            post = await self.twitter_connector.get_tweet_by_id(tweet_id)
            return post
            
        except Exception as e:
            logger.error(f"Error getting tweet by ID {tweet_id}: {e}")
            return None
    
    async def _get_user_timeline(self, username: str, max_results: int = 5) -> List[SocialMediaPost]:
        """Get user's recent timeline - Optimized for free tier"""
        if self.api_call_count >= self.max_api_calls:
            logger.warning("API call limit reached")
            return []
        
        try:
            self.api_call_count += 1
            # Use Twitter connector's optimized method
            posts = await self.twitter_connector.get_user_timeline(username, max_results)
            return posts
            
        except Exception as e:
            logger.error(f"Error getting user timeline for {username}: {e}")
            return []
    
    async def _search_hashtag_posts(self, hashtag: str, max_results: int = 10) -> List[SocialMediaPost]:
        """Search for posts with specific hashtag - Optimized for free tier"""
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
            
            # Check for retweeted_status
            if 'retweeted_status' in post.metadata:
                return post.metadata['retweeted_status'].get('id_str')
            
            return None
        except Exception as e:
            logger.error(f"Error extracting original tweet ID: {e}")
            return None
    
    async def _find_similar_earlier_posts(self, post: SocialMediaPost, max_results: int = 10) -> List[SocialMediaPost]:
        """Find similar posts posted earlier"""
        if self.api_call_count >= self.max_api_calls:
            return []
        
        try:
            # Extract key terms from content
            key_terms = self._extract_key_terms(post.content)
            if not key_terms:
                return []
            
            # Search for similar content
            search_query = ' OR '.join(key_terms[:3])  # Use top 3 terms
            similar_posts = await self.twitter_connector.search_tweets(
                keywords=search_query,
                max_results=max_results,
                end_time=post.timestamp  # Only posts before this one
            )
            
            # Filter for actual similarity
            filtered_posts = []
            for similar_post in similar_posts:
                if self._calculate_content_similarity(post.content, similar_post.content) > 0.7:
                    filtered_posts.append(similar_post)
            
            return filtered_posts
            
        except Exception as e:
            logger.error(f"Error finding similar earlier posts: {e}")
            return []
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key terms from content"""
        try:
            # Remove URLs, mentions, hashtags
            cleaned = re.sub(r'http\S+|@\w+|#\w+', '', content)
            
            # Split into words and filter
            words = cleaned.lower().split()
            
            # Remove common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
            
            key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
            
            return key_terms[:10]  # Return top 10 terms
            
        except Exception as e:
            logger.error(f"Error extracting key terms: {e}")
            return []
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two pieces of content"""
        try:
            # Simple word overlap similarity
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    def _identify_viral_candidates(self, posts: List[SocialMediaPost]) -> List[SocialMediaPost]:
        """Identify posts with viral potential"""
        try:
            # Sort by engagement
            sorted_posts = sorted(posts, 
                                key=lambda x: sum(x.engagement_metrics.values()), 
                                reverse=True)
            
            # Return top 30% or at least 1 post
            num_candidates = max(1, len(posts) // 3)
            return sorted_posts[:num_candidates]
            
        except Exception as e:
            logger.error(f"Error identifying viral candidates: {e}")
            return posts[:5] if posts else []
    
    def _cluster_similar_content(self, posts: List[SocialMediaPost]) -> List[List[SocialMediaPost]]:
        """Group posts with similar content"""
        try:
            clusters = []
            used_posts = set()
            
            for post in posts:
                if post.post_id in used_posts:
                    continue
                
                cluster = [post]
                used_posts.add(post.post_id)
                
                # Find similar posts
                for other_post in posts:
                    if (other_post.post_id not in used_posts and 
                        self._calculate_content_similarity(post.content, other_post.content) > 0.6):
                        cluster.append(other_post)
                        used_posts.add(other_post.post_id)
                
                clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering similar content: {e}")
            return [[post] for post in posts]  # Each post in its own cluster
    
    def _deduplicate_posts(self, posts: List[SocialMediaPost]) -> List[SocialMediaPost]:
        """Remove duplicate posts"""
        seen_ids = set()
        unique_posts = []
        
        for post in posts:
            if post.post_id not in seen_ids:
                unique_posts.append(post)
                seen_ids.add(post.post_id)
        
        return unique_posts
    
    def _find_original_post(self, posts: List[SocialMediaPost]) -> Optional[SocialMediaPost]:
        """Find the most likely original post"""
        if not posts:
            return None
        
        try:
            # Sort by timestamp and influence
            scored_posts = []
            for post in posts:
                influence_score = self._calculate_user_influence(post)
                time_score = 1.0  # Earlier posts get higher scores
                
                # Boost score for non-retweets
                originality_score = 2.0 if not self._is_retweet(post) else 1.0
                
                total_score = influence_score * 0.4 + time_score * 0.3 + originality_score * 0.3
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
            
            # Normalize engagement (simple approach)
            influence_score = min(engagement / 1000.0, 1.0)  # Cap at 1.0
            
            return influence_score
            
        except Exception as e:
            logger.error(f"Error calculating user influence: {e}")
            return 0.0
    
    def _calculate_tracking_confidence(self, posts: List[SocialMediaPost], method: str) -> float:
        """Calculate confidence in tracking results"""
        try:
            if not posts:
                return 0.0
            
            base_confidence = 0.5
            
            # Boost confidence based on method
            method_boost = {
                "post_url": 0.3,  # Highest confidence for direct URL
                "username": 0.2,
                "hashtag": 0.1
            }
            
            confidence = base_confidence + method_boost.get(method, 0.0)
            
            # Boost for chain length
            chain_boost = min(len(posts) * 0.05, 0.2)
            confidence += chain_boost
            
            # Boost for retweet chains (more reliable)
            retweet_count = sum(1 for post in posts if self._is_retweet(post))
            retweet_boost = min(retweet_count * 0.1, 0.2)
            confidence += retweet_boost
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating tracking confidence: {e}")
            return 0.5
    
    def _calculate_viral_coefficient(self, posts: List[SocialMediaPost]) -> float:
        """Calculate viral coefficient (spread rate)"""
        try:
            if len(posts) < 2:
                return 0.0
            
            # Simple viral coefficient: retweets / original posts
            retweets = sum(1 for post in posts if self._is_retweet(post))
            originals = len(posts) - retweets
            
            if originals == 0:
                return 0.0
            
            return retweets / originals
            
        except Exception as e:
            logger.error(f"Error calculating viral coefficient: {e}")
            return 0.0
    
    def _safe_diameter(self, graph: nx.Graph) -> int:
        """Safely calculate graph diameter"""
        try:
            if nx.is_connected(graph.to_undirected()):
                return nx.diameter(graph.to_undirected())
            else:
                return 0
        except:
            return 0