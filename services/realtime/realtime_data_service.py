#!/usr/bin/env python3
"""
Real-time Data Service
Provides unified real-time data access across all dashboard components
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import networkx as nx

from .social_media_connectors import SocialMediaAggregator
from .realtime_search_service import RealTimeSearchService, SearchQuery

logger = logging.getLogger(__name__)

@dataclass
class RealTimePost:
    """Enhanced post data structure for real-time analysis"""
    id: str
    platform: str
    content: str
    author: str
    author_id: str
    timestamp: datetime
    url: str
    hashtags: List[str]
    mentions: List[str]
    engagement: Dict[str, int]  # likes, shares, comments, views
    location: Optional[str]
    language: str
    sentiment_score: float
    sentiment_label: str
    viral_score: float
    influence_score: float
    risk_level: str
    parent_post_id: Optional[str]  # For tracking retweets/shares
    thread_id: Optional[str]  # For tracking conversations
    media_urls: List[str]
    verified_author: bool

@dataclass
class InfluenceNode:
    """Node in the influence network"""
    user_id: str
    username: str
    platform: str
    follower_count: int
    influence_score: float
    post_count: int
    engagement_rate: float
    verified: bool
    location: Optional[str]
    is_origin: bool = False

@dataclass
class InfluenceEdge:
    """Edge in the influence network"""
    source_user: str
    target_user: str
    interaction_type: str  # retweet, reply, mention, share
    timestamp: datetime
    post_id: str
    weight: float

class RealTimeDataService:
    """Unified real-time data service for all dashboard components"""
    
    def __init__(self):
        self.aggregator = SocialMediaAggregator()
        self.search_service = RealTimeSearchService()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def get_viral_timeline_data(self, 
                                    time_range: str = "Last 24 hours",
                                    platforms: List[str] = None,
                                    keywords: List[str] = None) -> pd.DataFrame:
        """Get real-time viral timeline data"""
        try:
            # Convert time range to hours
            hours_map = {
                "Last 24 hours": 24,
                "Last 3 days": 72,
                "Last week": 168,
                "Last month": 720
            }
            hours = hours_map.get(time_range, 24)
            
            # Create search query
            query = SearchQuery(
                keywords=keywords or ["trending", "viral", "breaking"],
                platforms=platforms or ["twitter", "youtube", "reddit"],
                time_window=hours,
                max_results=500
            )
            
            # Get real-time data
            results = await self.search_service.search_real_time(query)
            
            if not results.posts:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for post in results.posts:
                data.append({
                    "id": post.id,
                    "platform": post.platform,
                    "content": post.content,
                    "timestamp": post.timestamp,
                    "viral_score": post.viral_score,
                    "engagement": sum(post.engagement.values()),
                    "language": post.language,
                    "location": post.location,
                    "sentiment_score": post.sentiment_score,
                    "sentiment_label": post.sentiment_label,
                    "author": post.author,
                    "url": post.url,
                    "hashtags": ",".join(post.hashtags),
                    "risk_level": post.risk_level
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error getting viral timeline data: {e}")
            return pd.DataFrame()
    
    async def get_comprehensive_analysis_data(self, 
                                            keywords: List[str] = None,
                                            platforms: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive analysis data"""
        try:
            query = SearchQuery(
                keywords=keywords or ["trending"],
                platforms=platforms or ["twitter", "youtube", "reddit"],
                time_window=24,
                max_results=1000
            )
            
            results = await self.search_service.search_real_time(query)
            
            if not results.posts:
                return {"posts": [], "summary": {}, "trends": []}
            
            # Analyze trends
            trends = self._analyze_trends(results.posts)
            
            # Generate summary
            summary = {
                "total_posts": len(results.posts),
                "avg_sentiment": np.mean([p.sentiment_score for p in results.posts]),
                "avg_viral_score": np.mean([p.viral_score for p in results.posts]),
                "platform_distribution": self._get_platform_distribution(results.posts),
                "language_distribution": self._get_language_distribution(results.posts),
                "risk_distribution": self._get_risk_distribution(results.posts)
            }
            
            return {
                "posts": results.posts,
                "summary": summary,
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analysis data: {e}")
            return {"posts": [], "summary": {}, "trends": []}
    
    async def get_sentiment_behavior_data(self, 
                                        keywords: List[str] = None,
                                        platforms: List[str] = None) -> Dict[str, Any]:
        """Get sentiment and behavior analysis data"""
        try:
            query = SearchQuery(
                keywords=keywords or ["trending"],
                platforms=platforms or ["twitter", "youtube", "reddit"],
                time_window=48,
                max_results=1000
            )
            
            results = await self.search_service.search_real_time(query)
            
            if not results.posts:
                return {"sentiment_timeline": [], "behavior_patterns": {}}
            
            # Sentiment timeline
            sentiment_timeline = self._create_sentiment_timeline(results.posts)
            
            # Behavior patterns
            behavior_patterns = self._analyze_behavior_patterns(results.posts)
            
            return {
                "sentiment_timeline": sentiment_timeline,
                "behavior_patterns": behavior_patterns,
                "posts": results.posts
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment behavior data: {e}")
            return {"sentiment_timeline": [], "behavior_patterns": {}}
    
    async def get_influence_network_data(self, 
                                       hashtag: str = None,
                                       post_url: str = None,
                                       keywords: List[str] = None) -> Dict[str, Any]:
        """Get influence network data with origin tracking"""
        try:
            # Build search query based on input
            if post_url:
                # Extract post ID and platform from URL
                post_info = self._extract_post_info_from_url(post_url)
                if post_info:
                    query = SearchQuery(
                        post_id=post_info["id"],
                        platforms=[post_info["platform"]],
                        time_window=168,  # 1 week
                        max_results=1000
                    )
            elif hashtag:
                query = SearchQuery(
                    keywords=[hashtag],
                    platforms=["twitter", "youtube", "reddit"],
                    time_window=168,
                    max_results=1000
                )
            else:
                query = SearchQuery(
                    keywords=keywords or ["trending"],
                    platforms=["twitter", "youtube", "reddit"],
                    time_window=72,
                    max_results=500
                )
            
            results = await self.search_service.search_real_time(query)
            
            if not results.posts:
                return {"nodes": [], "edges": [], "origin_nodes": [], "network_stats": {}}
            
            # Build influence network
            network_data = await self._build_influence_network(results.posts)
            
            return network_data
            
        except Exception as e:
            logger.error(f"Error getting influence network data: {e}")
            return {"nodes": [], "edges": [], "origin_nodes": [], "network_stats": {}}
    
    async def get_geographic_spread_data(self, 
                                       keywords: List[str] = None,
                                       platforms: List[str] = None) -> Dict[str, Any]:
        """Get geographic spread data"""
        try:
            query = SearchQuery(
                keywords=keywords or ["trending"],
                platforms=platforms or ["twitter", "youtube", "reddit"],
                time_window=48,
                max_results=1000
            )
            
            results = await self.search_service.search_real_time(query)
            
            if not results.posts:
                return {"geographic_data": [], "heatmap_data": []}
            
            # Process geographic data
            geographic_data = self._process_geographic_data(results.posts)
            
            return geographic_data
            
        except Exception as e:
            logger.error(f"Error getting geographic spread data: {e}")
            return {"geographic_data": [], "heatmap_data": []}
    
    async def get_evidence_collection_data(self, 
                                         post_urls: List[str] = None,
                                         hashtags: List[str] = None,
                                         keywords: List[str] = None) -> Dict[str, Any]:
        """Get evidence collection data"""
        try:
            evidence_data = []
            
            # Process specific post URLs
            if post_urls:
                for url in post_urls:
                    post_info = await self._collect_post_evidence(url)
                    if post_info:
                        evidence_data.append(post_info)
            
            # Process hashtags
            if hashtags:
                for hashtag in hashtags:
                    query = SearchQuery(
                        keywords=[hashtag],
                        platforms=["twitter", "youtube", "reddit"],
                        time_window=168,
                        max_results=100
                    )
                    results = await self.search_service.search_real_time(query)
                    evidence_data.extend(results.posts)
            
            # Process general keywords
            if keywords and not post_urls and not hashtags:
                query = SearchQuery(
                    keywords=keywords,
                    platforms=["twitter", "youtube", "reddit"],
                    time_window=72,
                    max_results=200
                )
                results = await self.search_service.search_real_time(query)
                evidence_data.extend(results.posts)
            
            return {
                "evidence_posts": evidence_data,
                "collection_summary": self._create_evidence_summary(evidence_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting evidence collection data: {e}")
            return {"evidence_posts": [], "collection_summary": {}}
    
    def _analyze_trends(self, posts: List[RealTimePost]) -> List[Dict[str, Any]]:
        """Analyze trending topics from posts"""
        hashtag_counts = {}
        keyword_counts = {}
        
        for post in posts:
            # Count hashtags
            for hashtag in post.hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
            
            # Extract keywords from content
            words = post.content.lower().split()
            for word in words:
                if len(word) > 3 and word.isalpha():
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1
        
        # Get top trends
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        trends = []
        for hashtag, count in top_hashtags:
            trends.append({
                "type": "hashtag",
                "term": hashtag,
                "count": count,
                "trend_score": count / len(posts)
            })
        
        for keyword, count in top_keywords:
            trends.append({
                "type": "keyword",
                "term": keyword,
                "count": count,
                "trend_score": count / len(posts)
            })
        
        return sorted(trends, key=lambda x: x["trend_score"], reverse=True)[:20]
    
    def _get_platform_distribution(self, posts: List[RealTimePost]) -> Dict[str, int]:
        """Get platform distribution"""
        distribution = {}
        for post in posts:
            distribution[post.platform] = distribution.get(post.platform, 0) + 1
        return distribution
    
    def _get_language_distribution(self, posts: List[RealTimePost]) -> Dict[str, int]:
        """Get language distribution"""
        distribution = {}
        for post in posts:
            distribution[post.language] = distribution.get(post.language, 0) + 1
        return distribution
    
    def _get_risk_distribution(self, posts: List[RealTimePost]) -> Dict[str, int]:
        """Get risk level distribution"""
        distribution = {}
        for post in posts:
            distribution[post.risk_level] = distribution.get(post.risk_level, 0) + 1
        return distribution
    
    def _create_sentiment_timeline(self, posts: List[RealTimePost]) -> List[Dict[str, Any]]:
        """Create sentiment timeline data"""
        timeline_data = []
        
        # Group posts by hour
        hourly_data = {}
        for post in posts:
            hour_key = post.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_data:
                hourly_data[hour_key] = []
            hourly_data[hour_key].append(post)
        
        # Calculate hourly sentiment
        for hour, hour_posts in hourly_data.items():
            avg_sentiment = np.mean([p.sentiment_score for p in hour_posts])
            timeline_data.append({
                "timestamp": hour,
                "sentiment_score": avg_sentiment,
                "post_count": len(hour_posts),
                "avg_engagement": np.mean([sum(p.engagement.values()) for p in hour_posts])
            })
        
        return sorted(timeline_data, key=lambda x: x["timestamp"])
    
    def _analyze_behavior_patterns(self, posts: List[RealTimePost]) -> Dict[str, Any]:
        """Analyze behavior patterns"""
        patterns = {
            "posting_frequency": {},
            "engagement_patterns": {},
            "content_patterns": {},
            "user_behavior": {}
        }
        
        # Analyze posting frequency by hour
        hourly_posts = {}
        for post in posts:
            hour = post.timestamp.hour
            hourly_posts[hour] = hourly_posts.get(hour, 0) + 1
        patterns["posting_frequency"] = hourly_posts
        
        # Analyze engagement patterns
        high_engagement = [p for p in posts if sum(p.engagement.values()) > np.percentile([sum(p.engagement.values()) for p in posts], 75)]
        patterns["engagement_patterns"] = {
            "high_engagement_count": len(high_engagement),
            "avg_high_engagement": np.mean([sum(p.engagement.values()) for p in high_engagement]) if high_engagement else 0
        }
        
        return patterns
    
    async def _build_influence_network(self, posts: List[RealTimePost]) -> Dict[str, Any]:
        """Build influence network with origin tracking"""
        nodes = {}
        edges = []
        origin_candidates = []
        
        # Create nodes for each unique user
        for post in posts:
            if post.author_id not in nodes:
                nodes[post.author_id] = InfluenceNode(
                    user_id=post.author_id,
                    username=post.author,
                    platform=post.platform,
                    follower_count=0,  # Would need to fetch from API
                    influence_score=post.influence_score,
                    post_count=1,
                    engagement_rate=sum(post.engagement.values()),
                    verified=post.verified_author,
                    location=post.location
                )
            else:
                nodes[post.author_id].post_count += 1
                nodes[post.author_id].engagement_rate += sum(post.engagement.values())
        
        # Calculate average engagement rates
        for node in nodes.values():
            node.engagement_rate = node.engagement_rate / node.post_count
        
        # Find origin nodes (earliest posts with high influence)
        sorted_posts = sorted(posts, key=lambda x: x.timestamp)
        early_posts = sorted_posts[:min(10, len(sorted_posts))]
        
        for post in early_posts:
            if post.influence_score > 0.7:  # High influence threshold
                if post.author_id in nodes:
                    nodes[post.author_id].is_origin = True
                    origin_candidates.append(post.author_id)
        
        # Create edges based on interactions
        for post in posts:
            if post.parent_post_id:
                # Find parent post author
                parent_post = next((p for p in posts if p.id == post.parent_post_id), None)
                if parent_post:
                    edges.append(InfluenceEdge(
                        source_user=parent_post.author_id,
                        target_user=post.author_id,
                        interaction_type="retweet" if post.platform == "twitter" else "share",
                        timestamp=post.timestamp,
                        post_id=post.id,
                        weight=post.viral_score
                    ))
            
            # Create edges for mentions
            for mention in post.mentions:
                # Would need to resolve mention to user_id
                edges.append(InfluenceEdge(
                    source_user=post.author_id,
                    target_user=mention,  # Simplified - would need user ID resolution
                    interaction_type="mention",
                    timestamp=post.timestamp,
                    post_id=post.id,
                    weight=0.5
                ))
        
        # Calculate network statistics
        G = nx.DiGraph()
        for node_id, node in nodes.items():
            G.add_node(node_id, **node.__dict__)
        
        for edge in edges:
            G.add_edge(edge.source_user, edge.target_user, weight=edge.weight)
        
        network_stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "origin_nodes": len(origin_candidates),
            "avg_clustering": nx.average_clustering(G.to_undirected()) if len(nodes) > 1 else 0,
            "density": nx.density(G) if len(nodes) > 1 else 0
        }
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "origin_nodes": origin_candidates,
            "network_stats": network_stats,
            "graph": G
        }
    
    def _process_geographic_data(self, posts: List[RealTimePost]) -> Dict[str, Any]:
        """Process geographic data from posts"""
        geographic_data = []
        location_counts = {}
        
        for post in posts:
            if post.location:
                location_counts[post.location] = location_counts.get(post.location, 0) + 1
                geographic_data.append({
                    "location": post.location,
                    "post_id": post.id,
                    "timestamp": post.timestamp,
                    "sentiment_score": post.sentiment_score,
                    "viral_score": post.viral_score,
                    "engagement": sum(post.engagement.values())
                })
        
        # Create heatmap data
        heatmap_data = [
            {"location": loc, "count": count, "intensity": count / len(posts)}
            for loc, count in location_counts.items()
        ]
        
        return {
            "geographic_data": geographic_data,
            "heatmap_data": heatmap_data,
            "location_summary": location_counts
        }
    
    def _extract_post_info_from_url(self, url: str) -> Optional[Dict[str, str]]:
        """Extract post information from URL"""
        # Simplified URL parsing - would need more robust implementation
        if "twitter.com" in url or "x.com" in url:
            # Extract tweet ID from URL
            parts = url.split("/")
            if "status" in parts:
                idx = parts.index("status")
                if idx + 1 < len(parts):
                    return {"platform": "twitter", "id": parts[idx + 1]}
        elif "youtube.com" in url:
            # Extract video ID
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
                return {"platform": "youtube", "id": video_id}
        elif "reddit.com" in url:
            # Extract post ID from Reddit URL
            parts = url.split("/")
            if "comments" in parts:
                idx = parts.index("comments")
                if idx + 1 < len(parts):
                    return {"platform": "reddit", "id": parts[idx + 1]}
        
        return None
    
    async def _collect_post_evidence(self, url: str) -> Optional[RealTimePost]:
        """Collect evidence for a specific post URL"""
        try:
            post_info = self._extract_post_info_from_url(url)
            if not post_info:
                return None
            
            # Use search service to get specific post
            query = SearchQuery(
                post_id=post_info["id"],
                platforms=[post_info["platform"]],
                max_results=1
            )
            
            results = await self.search_service.search_real_time(query)
            return results.posts[0] if results.posts else None
            
        except Exception as e:
            logger.error(f"Error collecting post evidence: {e}")
            return None
    
    def _create_evidence_summary(self, evidence_data: List[RealTimePost]) -> Dict[str, Any]:
        """Create evidence collection summary"""
        if not evidence_data:
            return {}
        
        return {
            "total_posts": len(evidence_data),
            "platforms": list(set(p.platform for p in evidence_data)),
            "date_range": {
                "start": min(p.timestamp for p in evidence_data),
                "end": max(p.timestamp for p in evidence_data)
            },
            "avg_viral_score": np.mean([p.viral_score for p in evidence_data]),
            "high_risk_posts": len([p for p in evidence_data if p.risk_level == "high"]),
            "unique_authors": len(set(p.author_id for p in evidence_data))
        }