#!/usr/bin/env python3
"""
Enhanced Real-time Search Component for SentinentalBERT
Real-time search with trend analysis, controversy detection, and key spreader identification
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import sys
import os
import re
from collections import Counter, defaultdict
import json

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from database.enhanced_cache_manager import EnhancedCacheManager
    from platforms.enhanced_twitter_service import EnhancedTwitterService
except ImportError as e:
    logging.warning(f"Could not import services: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeSearchEnhanced:
    """Enhanced real-time search with comprehensive trend and controversy analysis"""
    
    def __init__(self):
        self.cache_manager = EnhancedCacheManager()
        self.twitter_service = EnhancedTwitterService()
        
        # Controversy keywords for detection
        self.controversy_keywords = [
            'scandal', 'controversy', 'outrage', 'protest', 'boycott', 'ban', 'illegal',
            'fraud', 'corruption', 'fake', 'misleading', 'dangerous', 'harmful', 'toxic',
            'violence', 'threat', 'attack', 'crisis', 'emergency', 'disaster'
        ]
        
        # Trending indicators
        self.trending_indicators = [
            'breaking', 'urgent', 'alert', 'developing', 'exclusive', 'confirmed',
            'official', 'announced', 'revealed', 'exposed', 'leaked'
        ]
        
    def render_search_dashboard(self, keyword: str):
        """Render the complete real-time search dashboard"""
        st.subheader("🔍 Real-time Search & Trend Analysis")
        
        if not keyword:
            st.info("Enter a keyword to perform real-time search and trend analysis")
            return
        
        # Search control panel
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Real-time Analysis for:** `{keyword}`")
        
        with col2:
            search_depth = st.selectbox(
                "Search Depth",
                ["Surface", "Deep", "Comprehensive"],
                help="Surface: Basic trends, Deep: Detailed analysis, Comprehensive: Full investigation"
            )
        
        with col3:
            if st.button("🔄 Refresh Search", key="refresh_search"):
                self._refresh_search_data(keyword, search_depth)
                st.rerun()
        
        # Search tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trending Analysis", "⚠️ Controversy Detection", "👥 Key Spreaders", "🔗 Related Trends"])
        
        with tab1:
            self._render_trending_analysis(keyword, search_depth)
        
        with tab2:
            self._render_controversy_detection(keyword)
        
        with tab3:
            self._render_key_spreaders(keyword)
        
        with tab4:
            self._render_related_trends(keyword)
    
    def _refresh_search_data(self, keyword: str, depth: str):
        """Refresh search data with specified depth"""
        try:
            with st.spinner(f"Performing {depth.lower()} search analysis..."):
                # Get fresh data from Twitter
                max_results = {"Surface": 10, "Deep": 15, "Comprehensive": 20}[depth]
                tweets = self.twitter_service.search_tweets(keyword, max_results=max_results)
                
                if tweets:
                    # Analyze and store search trends
                    self._analyze_search_trends(keyword, tweets)
                    st.success(f"Refreshed search data with {len(tweets)} posts")
                else:
                    st.warning("No fresh search data available")
                    
        except Exception as e:
            logger.error(f"Error refreshing search data: {e}")
            st.error(f"Error refreshing search: {e}")
    
    def _analyze_search_trends(self, keyword: str, tweets: List) -> Dict[str, Any]:
        """Analyze search trends from tweets"""
        try:
            trend_data = {
                'keyword': keyword,
                'analysis_timestamp': datetime.now(),
                'total_posts': len(tweets),
                'trending_score': 0.0,
                'controversy_score': 0.0,
                'related_keywords': [],
                'key_spreaders': [],
                'sentiment_trend': 'neutral'
            }
            
            if not tweets:
                return trend_data
            
            # Calculate trending score
            total_engagement = sum(
                tweet.public_metrics.get('like_count', 0) + 
                tweet.public_metrics.get('retweet_count', 0) + 
                tweet.public_metrics.get('reply_count', 0)
                for tweet in tweets
            )
            
            trend_data['trending_score'] = min(total_engagement / 1000.0, 1.0)  # Normalize
            
            # Detect controversy
            controversy_mentions = 0
            for tweet in tweets:
                text_lower = tweet.text.lower()
                controversy_mentions += sum(1 for word in self.controversy_keywords if word in text_lower)
            
            trend_data['controversy_score'] = min(controversy_mentions / len(tweets), 1.0)
            
            # Extract related keywords (hashtags and mentions)
            all_text = ' '.join([tweet.text for tweet in tweets])
            hashtags = re.findall(r'#\w+', all_text)
            mentions = re.findall(r'@\w+', all_text)
            
            hashtag_counts = Counter(hashtags)
            trend_data['related_keywords'] = [tag for tag, count in hashtag_counts.most_common(10)]
            
            # Identify key spreaders
            spreader_metrics = {}
            for tweet in tweets:
                author_id = tweet.author_id
                engagement = (
                    tweet.public_metrics.get('like_count', 0) + 
                    tweet.public_metrics.get('retweet_count', 0) * 2 +  # Retweets weighted more
                    tweet.public_metrics.get('reply_count', 0)
                )
                
                if author_id not in spreader_metrics:
                    spreader_metrics[author_id] = {
                        'author_name': tweet.author_name,
                        'total_engagement': 0,
                        'post_count': 0
                    }
                
                spreader_metrics[author_id]['total_engagement'] += engagement
                spreader_metrics[author_id]['post_count'] += 1
            
            # Sort by influence (engagement per post)
            sorted_spreaders = sorted(
                spreader_metrics.items(),
                key=lambda x: x[1]['total_engagement'] / x[1]['post_count'],
                reverse=True
            )
            
            trend_data['key_spreaders'] = [
                {
                    'author_id': author_id,
                    'author_name': data['author_name'],
                    'influence_score': data['total_engagement'] / data['post_count'],
                    'post_count': data['post_count']
                }
                for author_id, data in sorted_spreaders[:10]
            ]
            
            # Store trend data
            self._store_trend_data(trend_data)
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error analyzing search trends: {e}")
            return {}
    
    def _store_trend_data(self, trend_data: Dict[str, Any]):
        """Store trend data in cache"""
        try:
            # This would store in the search_trends table
            # For now, we'll use a simple approach
            pass
        except Exception as e:
            logger.error(f"Error storing trend data: {e}")
    
    def _render_trending_analysis(self, keyword: str, depth: str):
        """Render trending analysis dashboard"""
        st.subheader("📈 Trending Analysis")
        
        # Get trending data
        trending_data = self._get_trending_data(keyword)
        
        if not trending_data:
            st.info("No trending data available. Refresh search to analyze trends.")
            return
        
        # Trending metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trending_score = trending_data.get('trending_score', 0)
            trend_emoji = "🔥" if trending_score > 0.7 else "📈" if trending_score > 0.3 else "📊"
            st.metric("Trending Score", f"{trend_emoji} {trending_score:.3f}")
        
        with col2:
            total_posts = trending_data.get('total_posts', 0)
            st.metric("Total Posts", f"{total_posts:,}")
        
        with col3:
            controversy_score = trending_data.get('controversy_score', 0)
            controversy_emoji = "🚨" if controversy_score > 0.5 else "⚠️" if controversy_score > 0.2 else "✅"
            st.metric("Controversy Level", f"{controversy_emoji} {controversy_score:.3f}")
        
        with col4:
            key_spreaders_count = len(trending_data.get('key_spreaders', []))
            st.metric("Key Spreaders", key_spreaders_count)
        
        # Trending timeline (mock data for visualization)
        st.subheader("📊 Trending Timeline")
        
        # Generate mock timeline data
        timeline_data = self._generate_trending_timeline(keyword)
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline['timestamp'] = pd.to_datetime(df_timeline['timestamp'])
            
            fig_timeline = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Trending Score Over Time', 'Post Volume & Engagement'),
                vertical_spacing=0.1
            )
            
            # Trending score line
            fig_timeline.add_trace(
                go.Scatter(
                    x=df_timeline['timestamp'],
                    y=df_timeline['trending_score'],
                    name='Trending Score',
                    line=dict(color='red', width=3),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            # Post volume bars
            fig_timeline.add_trace(
                go.Bar(
                    x=df_timeline['timestamp'],
                    y=df_timeline['post_count'],
                    name='Posts',
                    marker_color='blue',
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Engagement line
            fig_timeline.add_trace(
                go.Scatter(
                    x=df_timeline['timestamp'],
                    y=df_timeline['engagement'],
                    name='Engagement',
                    line=dict(color='green', width=2),
                    yaxis='y4'
                ),
                row=2, col=1
            )
            
            fig_timeline.update_layout(height=600, showlegend=True)
            fig_timeline.update_yaxes(title_text="Trending Score", row=1, col=1)
            fig_timeline.update_yaxes(title_text="Post Count", row=2, col=1)
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Related keywords
        related_keywords = trending_data.get('related_keywords', [])
        if related_keywords:
            st.subheader("🏷️ Related Keywords & Hashtags")
            
            # Create word cloud-style visualization
            keyword_data = []
            for i, keyword in enumerate(related_keywords[:10]):
                keyword_data.append({
                    'keyword': keyword,
                    'frequency': len(related_keywords) - i,  # Mock frequency
                    'category': 'hashtag' if keyword.startswith('#') else 'mention'
                })
            
            df_keywords = pd.DataFrame(keyword_data)
            
            fig_keywords = px.bar(
                df_keywords,
                x='frequency',
                y='keyword',
                orientation='h',
                color='category',
                title='Top Related Keywords',
                color_discrete_map={'hashtag': '#1f77b4', 'mention': '#ff7f0e'}
            )
            
            st.plotly_chart(fig_keywords, use_container_width=True)
    
    def _render_controversy_detection(self, keyword: str):
        """Render controversy detection analysis"""
        st.subheader("⚠️ Controversy Detection")
        
        # Get controversy analysis
        controversy_data = self._analyze_controversy(keyword)
        
        if not controversy_data:
            st.info("No controversy data available. Refresh search to analyze potential controversies.")
            return
        
        # Controversy risk assessment
        risk_level = controversy_data.get('risk_level', 'low')
        risk_score = controversy_data.get('risk_score', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_color = {'low': 'green', 'medium': 'orange', 'high': 'red'}[risk_level]
            risk_emoji = {'low': '✅', 'medium': '⚠️', 'high': '🚨'}[risk_level]
            st.markdown(f"**Risk Level:** {risk_emoji} <span style='color:{risk_color}'>{risk_level.upper()}</span>", unsafe_allow_html=True)
        
        with col2:
            st.metric("Risk Score", f"{risk_score:.3f}")
        
        with col3:
            controversy_indicators = len(controversy_data.get('indicators', []))
            st.metric("Controversy Indicators", controversy_indicators)
        
        # Controversy indicators
        indicators = controversy_data.get('indicators', [])
        if indicators:
            st.subheader("🔍 Detected Controversy Indicators")
            
            for indicator in indicators:
                with st.expander(f"⚠️ {indicator['type'].title()} - Severity: {indicator['severity']}"):
                    st.markdown(f"**Description:** {indicator['description']}")
                    st.markdown(f"**Evidence:** {indicator['evidence']}")
                    st.markdown(f"**Confidence:** {indicator['confidence']:.2f}")
                    
                    if indicator.get('related_posts'):
                        st.markdown("**Related Posts:**")
                        for post in indicator['related_posts'][:3]:
                            st.markdown(f"- {post[:100]}...")
        
        # Controversy timeline
        st.subheader("📈 Controversy Development Timeline")
        
        timeline_data = controversy_data.get('timeline', [])
        if timeline_data:
            df_controversy = pd.DataFrame(timeline_data)
            df_controversy['timestamp'] = pd.to_datetime(df_controversy['timestamp'])
            
            fig_controversy = px.line(
                df_controversy,
                x='timestamp',
                y='controversy_score',
                title='Controversy Score Over Time',
                line_shape='spline'
            )
            
            fig_controversy.add_hline(
                y=0.5, line_dash="dash", line_color="orange",
                annotation_text="Medium Risk Threshold"
            )
            fig_controversy.add_hline(
                y=0.7, line_dash="dash", line_color="red",
                annotation_text="High Risk Threshold"
            )
            
            st.plotly_chart(fig_controversy, use_container_width=True)
        
        # Mitigation recommendations
        st.subheader("💡 Mitigation Recommendations")
        
        recommendations = controversy_data.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. **{rec['action']}** - {rec['description']}")
        else:
            st.info("No specific mitigation recommendations at this time.")
    
    def _render_key_spreaders(self, keyword: str):
        """Render key spreaders analysis"""
        st.subheader("👥 Key Spreaders Analysis")
        
        # Get spreader data
        spreader_data = self._get_key_spreaders(keyword)
        
        if not spreader_data:
            st.info("No key spreader data available. Refresh search to identify key spreaders.")
            return
        
        spreaders = spreader_data.get('spreaders', [])
        
        if not spreaders:
            st.warning("No key spreaders identified")
            return
        
        # Top spreaders metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Spreaders", len(spreaders))
        
        with col2:
            avg_influence = np.mean([s['influence_score'] for s in spreaders])
            st.metric("Avg Influence Score", f"{avg_influence:.2f}")
        
        with col3:
            total_reach = sum(s.get('estimated_reach', 0) for s in spreaders)
            st.metric("Estimated Total Reach", f"{total_reach:,}")
        
        # Spreader ranking
        st.subheader("🏆 Top Key Spreaders")
        
        for i, spreader in enumerate(spreaders[:10], 1):
            with st.expander(f"#{i} {spreader['author_name']} - Influence: {spreader['influence_score']:.2f}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Author ID:** {spreader['author_id']}")
                    st.markdown(f"**Post Count:** {spreader['post_count']}")
                    st.markdown(f"**Influence Score:** {spreader['influence_score']:.2f}")
                    st.markdown(f"**Estimated Reach:** {spreader.get('estimated_reach', 'N/A'):,}")
                    
                    # Spreader characteristics
                    characteristics = spreader.get('characteristics', {})
                    if characteristics:
                        st.markdown("**Characteristics:**")
                        for char, value in characteristics.items():
                            st.markdown(f"- {char.title()}: {value}")
                
                with col2:
                    # Spreader type classification
                    spreader_type = spreader.get('type', 'regular')
                    type_emoji = {
                        'influencer': '⭐',
                        'bot_suspected': '🤖',
                        'regular': '👤',
                        'organization': '🏢'
                    }.get(spreader_type, '👤')
                    
                    st.markdown(f"**Type:** {type_emoji} {spreader_type.title()}")
                    
                    # Risk assessment
                    risk_level = spreader.get('risk_level', 'low')
                    risk_emoji = {'low': '✅', 'medium': '⚠️', 'high': '🚨'}[risk_level]
                    st.markdown(f"**Risk Level:** {risk_emoji} {risk_level.title()}")
        
        # Spreader network visualization
        st.subheader("🕸️ Spreader Network")
        
        if len(spreaders) > 1:
            # Create network visualization data
            network_data = self._create_spreader_network(spreaders)
            
            if network_data:
                fig_network = px.scatter(
                    network_data,
                    x='x',
                    y='y',
                    size='influence_score',
                    color='type',
                    hover_name='author_name',
                    hover_data=['post_count', 'influence_score'],
                    title='Key Spreaders Network'
                )
                
                st.plotly_chart(fig_network, use_container_width=True)
    
    def _render_related_trends(self, keyword: str):
        """Render related trends analysis"""
        st.subheader("🔗 Related Trends & Connections")
        
        # Get related trends
        related_data = self._get_related_trends(keyword)
        
        if not related_data:
            st.info("No related trends data available.")
            return
        
        # Related keywords trending
        related_keywords = related_data.get('related_keywords', [])
        if related_keywords:
            st.subheader("📈 Related Keywords Trending")
            
            df_related = pd.DataFrame(related_keywords)
            
            fig_related = px.bar(
                df_related,
                x='trend_score',
                y='keyword',
                orientation='h',
                color='trend_score',
                title='Related Keywords by Trend Score',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig_related, use_container_width=True)
        
        # Topic clusters
        st.subheader("🎯 Topic Clusters")
        
        clusters = related_data.get('topic_clusters', [])
        if clusters:
            for i, cluster in enumerate(clusters, 1):
                with st.expander(f"Cluster #{i}: {cluster['name']} ({len(cluster['keywords'])} keywords)"):
                    st.markdown(f"**Main Topic:** {cluster['name']}")
                    st.markdown(f"**Keywords:** {', '.join(cluster['keywords'])}")
                    st.markdown(f"**Relevance Score:** {cluster['relevance_score']:.3f}")
                    st.markdown(f"**Post Count:** {cluster['post_count']:,}")
        
        # Trend connections
        st.subheader("🔗 Trend Connections")
        
        connections = related_data.get('connections', [])
        if connections:
            connection_data = []
            for conn in connections:
                connection_data.append({
                    'source': conn['source'],
                    'target': conn['target'],
                    'strength': conn['strength'],
                    'type': conn['type']
                })
            
            df_connections = pd.DataFrame(connection_data)
            
            fig_connections = px.scatter(
                df_connections,
                x='source',
                y='target',
                size='strength',
                color='type',
                title='Trend Connection Network'
            )
            
            st.plotly_chart(fig_connections, use_container_width=True)
    
    def _get_trending_data(self, keyword: str) -> Dict[str, Any]:
        """Get trending data for keyword"""
        # This would query the database for trending data
        # For now, return mock data structure
        return {
            'keyword': keyword,
            'trending_score': 0.65,
            'total_posts': 150,
            'controversy_score': 0.25,
            'key_spreaders': [
                {
                    'author_id': 'user_1',
                    'author_name': 'Climate Activist',
                    'influence_score': 8.5,
                    'post_count': 5
                }
            ],
            'related_keywords': ['#climatechange', '#globalwarming', '#environment', '@greenpeace']
        }
    
    def _generate_trending_timeline(self, keyword: str) -> List[Dict]:
        """Generate mock trending timeline data"""
        timeline_data = []
        base_time = datetime.now() - timedelta(hours=12)
        
        for i in range(12):
            timestamp = base_time + timedelta(hours=i)
            timeline_data.append({
                'timestamp': timestamp,
                'trending_score': 0.3 + 0.4 * np.sin(i * 0.5) + np.random.normal(0, 0.1),
                'post_count': 10 + int(20 * np.sin(i * 0.3)) + np.random.randint(-5, 5),
                'engagement': 50 + int(100 * np.sin(i * 0.4)) + np.random.randint(-20, 20)
            })
        
        return timeline_data
    
    def _analyze_controversy(self, keyword: str) -> Dict[str, Any]:
        """Analyze controversy indicators"""
        # Mock controversy analysis
        return {
            'risk_level': 'medium',
            'risk_score': 0.45,
            'indicators': [
                {
                    'type': 'negative_sentiment_spike',
                    'severity': 'medium',
                    'description': 'Sudden increase in negative sentiment detected',
                    'evidence': 'Sentiment score dropped from 0.2 to -0.3 in 2 hours',
                    'confidence': 0.75,
                    'related_posts': [
                        'This is completely wrong and misleading!',
                        'How can they say this? Outrageous!',
                        'This needs to be stopped immediately'
                    ]
                }
            ],
            'timeline': [
                {'timestamp': datetime.now() - timedelta(hours=6), 'controversy_score': 0.1},
                {'timestamp': datetime.now() - timedelta(hours=4), 'controversy_score': 0.3},
                {'timestamp': datetime.now() - timedelta(hours=2), 'controversy_score': 0.45},
                {'timestamp': datetime.now(), 'controversy_score': 0.4}
            ],
            'recommendations': [
                {
                    'action': 'Monitor closely',
                    'description': 'Continue monitoring for escalation patterns'
                },
                {
                    'action': 'Fact-check content',
                    'description': 'Verify accuracy of trending information'
                }
            ]
        }
    
    def _get_key_spreaders(self, keyword: str) -> Dict[str, Any]:
        """Get key spreaders data"""
        # Mock spreader data
        return {
            'spreaders': [
                {
                    'author_id': 'user_1',
                    'author_name': 'Climate Expert',
                    'influence_score': 9.2,
                    'post_count': 8,
                    'estimated_reach': 50000,
                    'type': 'influencer',
                    'risk_level': 'low',
                    'characteristics': {
                        'verified': True,
                        'follower_count': 100000,
                        'engagement_rate': 0.05
                    }
                },
                {
                    'author_id': 'user_2',
                    'author_name': 'News Bot',
                    'influence_score': 7.8,
                    'post_count': 15,
                    'estimated_reach': 25000,
                    'type': 'bot_suspected',
                    'risk_level': 'medium',
                    'characteristics': {
                        'verified': False,
                        'posting_frequency': 'very_high',
                        'content_similarity': 0.8
                    }
                }
            ]
        }
    
    def _create_spreader_network(self, spreaders: List[Dict]) -> List[Dict]:
        """Create spreader network visualization data"""
        network_data = []
        
        for i, spreader in enumerate(spreaders):
            # Position spreaders in a circle
            angle = 2 * np.pi * i / len(spreaders)
            x = np.cos(angle) * spreader['influence_score']
            y = np.sin(angle) * spreader['influence_score']
            
            network_data.append({
                'x': x,
                'y': y,
                'author_name': spreader['author_name'],
                'influence_score': spreader['influence_score'],
                'post_count': spreader['post_count'],
                'type': spreader['type']
            })
        
        return network_data
    
    def _get_related_trends(self, keyword: str) -> Dict[str, Any]:
        """Get related trends data"""
        # Mock related trends data
        return {
            'related_keywords': [
                {'keyword': 'global warming', 'trend_score': 0.8},
                {'keyword': 'carbon emissions', 'trend_score': 0.6},
                {'keyword': 'renewable energy', 'trend_score': 0.7},
                {'keyword': 'sustainability', 'trend_score': 0.5}
            ],
            'topic_clusters': [
                {
                    'name': 'Environmental Policy',
                    'keywords': ['policy', 'government', 'regulation', 'law'],
                    'relevance_score': 0.75,
                    'post_count': 120
                },
                {
                    'name': 'Scientific Research',
                    'keywords': ['study', 'research', 'data', 'evidence'],
                    'relevance_score': 0.65,
                    'post_count': 85
                }
            ],
            'connections': [
                {
                    'source': keyword,
                    'target': 'global warming',
                    'strength': 0.9,
                    'type': 'semantic'
                },
                {
                    'source': keyword,
                    'target': 'carbon emissions',
                    'strength': 0.7,
                    'type': 'causal'
                }
            ]
        }
    
    def get_search_summary(self, keyword: str) -> Dict[str, Any]:
        """Get search summary for other components"""
        trending_data = self._get_trending_data(keyword)
        controversy_data = self._analyze_controversy(keyword)
        spreader_data = self._get_key_spreaders(keyword)
        
        return {
            'trending_score': trending_data.get('trending_score', 0),
            'controversy_level': controversy_data.get('risk_level', 'low'),
            'controversy_score': controversy_data.get('risk_score', 0),
            'key_spreaders_count': len(spreader_data.get('spreaders', [])),
            'top_spreader': spreader_data.get('spreaders', [{}])[0].get('author_name', 'N/A'),
            'related_keywords_count': len(trending_data.get('related_keywords', [])),
            'risk_indicators': len(controversy_data.get('indicators', []))
        }

# Test the component
if __name__ == "__main__":
    # This would be called from the main dashboard
    realtime_search = RealtimeSearchEnhanced()
    
    # Test with sample data
    test_keyword = "climate change"
    print(f"Testing real-time search for keyword: {test_keyword}")
    
    summary = realtime_search.get_search_summary(test_keyword)
    print(f"Search summary: {summary}")