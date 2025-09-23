#!/usr/bin/env python3
"""
Enhanced Influence Network Component for SentinentalBERT
Chronological influence tracking with IST-based timeline analysis
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Optional, Tuple
import logging
import sys
import os
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

class InfluenceNetworkEnhanced:
    """Enhanced influence network with chronological tracking"""
    
    def __init__(self):
        self.cache_manager = EnhancedCacheManager()
        self.twitter_service = EnhancedTwitterService()
        self.ist_timezone = pytz.timezone('Asia/Kolkata')
        
    def render_influence_dashboard(self, keyword: str):
        """Render the complete influence network dashboard"""
        st.subheader("🕸️ Influence Network Analysis")
        
        if not keyword:
            st.info("Enter a keyword to analyze influence networks")
            return
        
        # Control panel
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Analyzing Influence Network for:** `{keyword}`")
        
        with col2:
            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Surface", "Deep", "Complete"],
                help="Surface: Direct interactions, Deep: 2-hop connections, Complete: Full network"
            )
        
        with col3:
            if st.button("🔄 Refresh Network", key="refresh_network"):
                self._refresh_network_data(keyword)
                st.rerun()
        
        # Get network data
        network_data = self._get_network_data(keyword, analysis_depth)
        
        if not network_data or not network_data.get('nodes'):
            st.warning("No network data available. Building influence network...")
            self._build_influence_network(keyword)
            network_data = self._get_network_data(keyword, analysis_depth)
        
        if network_data and network_data.get('nodes'):
            # Main network visualization
            self._render_network_graph(network_data)
            
            # Chronological analysis
            self._render_chronological_analysis(keyword, network_data)
            
            # Influence metrics
            self._render_influence_metrics(network_data)
            
            # Original content tracking
            self._render_original_content_tracking(keyword)
        else:
            st.error("Unable to build influence network. Please try again.")
    
    def _get_network_data(self, keyword: str, depth: str = "Surface") -> Dict[str, Any]:
        """Get influence network data"""
        try:
            network_data = self.cache_manager.get_influence_network(keyword)
            
            # Filter based on depth
            if depth == "Surface":
                # Limit to top 20 nodes
                network_data['nodes'] = network_data['nodes'][:20]
                network_data['edges'] = [
                    edge for edge in network_data['edges'] 
                    if edge['source'] in [node['id'] for node in network_data['nodes']] and
                       edge['target'] in [node['id'] for node in network_data['nodes']]
                ]
            elif depth == "Deep":
                # Limit to top 50 nodes
                network_data['nodes'] = network_data['nodes'][:50]
                network_data['edges'] = network_data['edges'][:100]
            
            return network_data
            
        except Exception as e:
            logger.error(f"Error getting network data: {e}")
            return {}
    
    def _build_influence_network(self, keyword: str):
        """Build influence network from available data"""
        try:
            # Get tweets for the keyword
            tweets = self.twitter_service.search_tweets(keyword, max_results=10)
            
            if not tweets:
                st.warning("No tweets available to build network")
                return
            
            # Extract interactions
            interactions = []
            
            for tweet in tweets:
                # Convert datetime to IST
                ist_time = tweet.created_at.astimezone(self.ist_timezone)
                
                # Direct post interaction
                interactions.append({
                    'source_user_id': tweet.author_id,
                    'target_user_id': None,
                    'type': 'original_post',
                    'timestamp': ist_time,
                    'weight': 1.0,
                    'content_id': tweet.id
                })
                
                # Extract mentions and replies
                if hasattr(tweet, 'entities') and tweet.entities:
                    mentions = tweet.entities.get('mentions', [])
                    for mention in mentions:
                        interactions.append({
                            'source_user_id': tweet.author_id,
                            'target_user_id': mention.get('id', mention.get('username')),
                            'type': 'mention',
                            'timestamp': ist_time,
                            'weight': 0.5,
                            'content_id': tweet.id
                        })
                
                # Check for retweets
                if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
                    for ref_tweet in tweet.referenced_tweets:
                        if ref_tweet.get('type') == 'retweeted':
                            interactions.append({
                                'source_user_id': tweet.author_id,
                                'target_user_id': 'original_author',  # Would need original tweet data
                                'type': 'retweet',
                                'timestamp': ist_time,
                                'weight': 2.0,
                                'content_id': tweet.id
                            })
            
            # Store interactions
            if interactions:
                self.cache_manager.track_influence_network(keyword, interactions)
                st.success(f"Built influence network with {len(interactions)} interactions")
            
        except Exception as e:
            logger.error(f"Error building influence network: {e}")
            st.error(f"Error building network: {e}")
    
    def _refresh_network_data(self, keyword: str):
        """Refresh network data"""
        with st.spinner("Refreshing influence network..."):
            self._build_influence_network(keyword)
    
    def _render_network_graph(self, network_data: Dict[str, Any]):
        """Render interactive network graph"""
        nodes = network_data.get('nodes', [])
        edges = network_data.get('edges', [])
        
        if not nodes:
            st.warning("No network nodes to display")
            return
        
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            G.add_node(
                node['id'], 
                influence=node['influence'],
                interactions=node['interactions']
            )
        
        # Add edges
        for edge in edges:
            if edge['source'] in G.nodes and edge['target'] in G.nodes:
                G.add_edge(
                    edge['source'], 
                    edge['target'], 
                    weight=edge['weight'],
                    type=edge['type']
                )
        
        # Calculate layout
        try:
            pos = nx.spring_layout(G, k=1, iterations=50)
        except:
            pos = {node: (np.random.random(), np.random.random()) for node in G.nodes()}
        
        # Prepare data for Plotly
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            edge_data = G.edges[edge]
            edge_info.append(f"Connection: {edge[0]} → {edge[1]}<br>Weight: {edge_data.get('weight', 1)}")
        
        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            influence = node_data.get('influence', 0)
            interactions = node_data.get('interactions', 0)
            
            node_text.append(f"User: {node}<br>Influence: {influence}<br>Interactions: {interactions}")
            node_size.append(max(10, min(50, influence * 10)))  # Scale node size
            node_color.append(influence)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node[:10] + '...' if len(node) > 10 else node for node in G.nodes()],
            textposition="middle center",
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=True,
                color=node_color,
                size=node_size,
                colorbar=dict(
                    thickness=15,
                    len=0.5,
                    x=1.02,
                    title="Influence Score"
                ),
                line=dict(width=2)
            )
        )
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f'Influence Network - {network_data.get("keyword", "Unknown")}',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text=f"Network Stats: {len(nodes)} nodes, {len(edges)} connections",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_chronological_analysis(self, keyword: str, network_data: Dict[str, Any]):
        """Render chronological influence analysis"""
        st.subheader("⏰ Chronological Influence Analysis (IST)")
        
        # Get chronological data from database
        chronological_data = self._get_chronological_data(keyword)
        
        if not chronological_data:
            st.info("No chronological data available")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(chronological_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Timeline of interactions
            fig_timeline = px.scatter(
                df,
                x='timestamp',
                y='influence_weight',
                color='interaction_type',
                size='influence_weight',
                title='Influence Timeline (IST)',
                hover_data=['source_user_id', 'interaction_type']
            )
            fig_timeline.update_layout(height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        with col2:
            # Hourly activity pattern
            hourly_activity = df.groupby('hour').agg({
                'influence_weight': 'sum',
                'source_user_id': 'count'
            }).reset_index()
            hourly_activity.columns = ['hour', 'total_influence', 'interaction_count']
            
            fig_hourly = px.bar(
                hourly_activity,
                x='hour',
                y='interaction_count',
                title='Hourly Activity Pattern (IST)',
                labels={'hour': 'Hour (IST)', 'interaction_count': 'Interactions'}
            )
            fig_hourly.update_layout(height=400)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Interaction type breakdown
        interaction_summary = df.groupby('interaction_type').agg({
            'influence_weight': ['sum', 'mean', 'count']
        }).round(2)
        
        st.subheader("📊 Interaction Type Analysis")
        st.dataframe(interaction_summary, use_container_width=True)
    
    def _render_influence_metrics(self, network_data: Dict[str, Any]):
        """Render influence metrics and rankings"""
        st.subheader("📈 Influence Metrics")
        
        nodes = network_data.get('nodes', [])
        edges = network_data.get('edges', [])
        network_stats = network_data.get('network_stats', {})
        
        # Top influencers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🏆 Top Influencers**")
            top_influencers = sorted(nodes, key=lambda x: x['influence'], reverse=True)[:5]
            for i, influencer in enumerate(top_influencers, 1):
                st.markdown(f"{i}. **{influencer['id'][:15]}...** - {influencer['influence']:.2f}")
        
        with col2:
            st.markdown("**💬 Most Active Users**")
            most_active = sorted(nodes, key=lambda x: x['interactions'], reverse=True)[:5]
            for i, user in enumerate(most_active, 1):
                st.markdown(f"{i}. **{user['id'][:15]}...** - {user['interactions']} interactions")
        
        with col3:
            st.markdown("**🔗 Network Statistics**")
            st.markdown(f"• **Total Nodes:** {network_stats.get('total_nodes', 0)}")
            st.markdown(f"• **Total Edges:** {network_stats.get('total_edges', 0)}")
            st.markdown(f"• **Top Influencer:** {network_stats.get('top_influencer', 'N/A')[:15]}...")
            
            # Calculate network density
            if len(nodes) > 1:
                max_edges = len(nodes) * (len(nodes) - 1) / 2
                density = len(edges) / max_edges if max_edges > 0 else 0
                st.markdown(f"• **Network Density:** {density:.3f}")
        
        # Influence distribution
        if nodes:
            influence_scores = [node['influence'] for node in nodes]
            
            fig_dist = px.histogram(
                x=influence_scores,
                nbins=20,
                title='Influence Score Distribution',
                labels={'x': 'Influence Score', 'y': 'Number of Users'}
            )
            fig_dist.update_layout(height=300)
            st.plotly_chart(fig_dist, use_container_width=True)
    
    def _render_original_content_tracking(self, keyword: str):
        """Render original content tracking analysis"""
        st.subheader("🎯 Original Content Tracking")
        
        # Get original content data
        original_content = self._track_original_content(keyword)
        
        if not original_content:
            st.info("No original content tracking data available")
            return
        
        # Display original content timeline
        df = pd.DataFrame(original_content)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp to find chronological order
        df_sorted = df.sort_values('timestamp')
        
        st.markdown("**📅 Chronological Content Timeline (IST)**")
        
        for i, (_, row) in enumerate(df_sorted.iterrows()):
            timestamp_ist = row['timestamp'].tz_localize('UTC').tz_convert(self.ist_timezone)
            
            with st.expander(f"#{i+1} - {timestamp_ist.strftime('%Y-%m-%d %H:%M:%S IST')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Author:** {row['author_id']}")
                    st.markdown(f"**Content:** {row['content'][:200]}...")
                    st.markdown(f"**Type:** {row['content_type']}")
                
                with col2:
                    st.markdown(f"**Influence:** {row['influence_score']:.2f}")
                    st.markdown(f"**Engagement:** {row['engagement_count']}")
                    
                    if row['is_original']:
                        st.success("🎯 Original Content")
                    else:
                        st.info("🔄 Derivative Content")
        
        # Original vs Derivative analysis
        original_count = len(df[df['is_original'] == True])
        derivative_count = len(df[df['is_original'] == False])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Original Content", original_count)
        
        with col2:
            st.metric("Derivative Content", derivative_count)
        
        with col3:
            originality_ratio = original_count / len(df) if len(df) > 0 else 0
            st.metric("Originality Ratio", f"{originality_ratio:.2%}")
    
    def _get_chronological_data(self, keyword: str) -> List[Dict]:
        """Get chronological interaction data"""
        try:
            # This would query the influence_network table
            # For now, return mock data structure
            return [
                {
                    'source_user_id': 'user_1',
                    'target_user_id': 'user_2',
                    'interaction_type': 'retweet',
                    'timestamp': datetime.now() - timedelta(hours=2),
                    'influence_weight': 2.0,
                    'content_id': 'content_1'
                },
                {
                    'source_user_id': 'user_2',
                    'target_user_id': None,
                    'interaction_type': 'original_post',
                    'timestamp': datetime.now() - timedelta(hours=3),
                    'influence_weight': 1.0,
                    'content_id': 'content_2'
                }
            ]
        except Exception as e:
            logger.error(f"Error getting chronological data: {e}")
            return []
    
    def _track_original_content(self, keyword: str) -> List[Dict]:
        """Track original content sources"""
        try:
            # This would analyze content to identify original vs derivative
            # For now, return mock data structure
            return [
                {
                    'content_id': 'content_1',
                    'author_id': 'original_author',
                    'content': f'Original post about {keyword}',
                    'timestamp': datetime.now() - timedelta(hours=5),
                    'content_type': 'original_post',
                    'influence_score': 8.5,
                    'engagement_count': 150,
                    'is_original': True
                },
                {
                    'content_id': 'content_2',
                    'author_id': 'retweeter_1',
                    'content': f'RT: Original post about {keyword}',
                    'timestamp': datetime.now() - timedelta(hours=3),
                    'content_type': 'retweet',
                    'influence_score': 3.2,
                    'engagement_count': 45,
                    'is_original': False
                }
            ]
        except Exception as e:
            logger.error(f"Error tracking original content: {e}")
            return []
    
    def get_network_summary(self, keyword: str) -> Dict[str, Any]:
        """Get network summary for other components"""
        network_data = self._get_network_data(keyword)
        
        if not network_data:
            return {}
        
        nodes = network_data.get('nodes', [])
        edges = network_data.get('edges', [])
        
        return {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'top_influencer': nodes[0]['id'] if nodes else None,
            'max_influence': max([node['influence'] for node in nodes]) if nodes else 0,
            'network_density': len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0,
            'most_active_user': max(nodes, key=lambda x: x['interactions'])['id'] if nodes else None
        }

# Test the component
if __name__ == "__main__":
    # This would be called from the main dashboard
    influence_network = InfluenceNetworkEnhanced()
    
    # Test with sample data
    test_keyword = "climate change"
    print(f"Testing influence network for keyword: {test_keyword}")
    
    summary = influence_network.get_network_summary(test_keyword)
    print(f"Network summary: {summary}")