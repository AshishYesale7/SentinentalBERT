#!/usr/bin/env python3
"""
Enhanced Viral Timeline Component for SentinentalBERT
Interactive timeline analytics with 24h/1week/1month views
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import sys
import os

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

class ViralTimelineEnhanced:
    """Enhanced viral timeline with comprehensive analytics"""
    
    def __init__(self):
        self.cache_manager = EnhancedCacheManager()
        self.twitter_service = EnhancedTwitterService()
        
    def render_timeline_dashboard(self, keyword: str):
        """Render the complete timeline dashboard"""
        st.subheader("📈 Viral Timeline Analysis")
        
        if not keyword:
            st.info("Enter a keyword to analyze viral timeline patterns")
            return
        
        # Time period selector
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Analyzing:** `{keyword}`")
        
        with col2:
            time_period = st.selectbox(
                "Time Period",
                ["24h", "1w", "1m"],
                format_func=lambda x: {
                    "24h": "Last 24 Hours",
                    "1w": "Last Week", 
                    "1m": "Last Month"
                }[x]
            )
        
        with col3:
            if st.button("🔄 Refresh Data", key="refresh_timeline"):
                self._refresh_timeline_data(keyword)
                st.rerun()
        
        # Get timeline data
        timeline_data = self._get_timeline_data(keyword, time_period)
        
        if not timeline_data or not timeline_data.get('timeline'):
            st.warning("No timeline data available. Collecting fresh data...")
            self._collect_fresh_data(keyword)
            timeline_data = self._get_timeline_data(keyword, time_period)
        
        if timeline_data and timeline_data.get('timeline'):
            # Main timeline visualization
            self._render_main_timeline(timeline_data, time_period)
            
            # Analytics cards
            self._render_analytics_cards(timeline_data)
            
            # Detailed breakdown
            self._render_detailed_breakdown(timeline_data, time_period)
            
            # Peak activity analysis
            self._render_peak_analysis(timeline_data)
        else:
            st.error("Unable to load timeline data. Please try again.")
    
    def _get_timeline_data(self, keyword: str, time_period: str) -> Dict[str, Any]:
        """Get timeline data from cache manager"""
        try:
            return self.cache_manager.get_timeline_analytics(keyword, time_period)
        except Exception as e:
            logger.error(f"Error getting timeline data: {e}")
            return {}
    
    def _collect_fresh_data(self, keyword: str):
        """Collect fresh data from Twitter API"""
        try:
            # Get fresh tweets
            tweets = self.twitter_service.search_tweets(keyword, max_results=10)
            
            if tweets:
                # Convert to cache format
                posts_data = []
                for tweet in tweets:
                    posts_data.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'author_id': tweet.author_id,
                        'author_name': tweet.author_name,
                        'created_at': tweet.created_at,
                        'public_metrics': tweet.public_metrics,
                        'platform': 'twitter'
                    })
                
                # Cache the data
                self.cache_manager.cache_viral_content(keyword, posts_data)
                st.success(f"Collected {len(tweets)} fresh posts for analysis")
            else:
                st.warning("No fresh data available from API")
                
        except Exception as e:
            logger.error(f"Error collecting fresh data: {e}")
            st.error(f"Error collecting data: {e}")
    
    def _refresh_timeline_data(self, keyword: str):
        """Refresh timeline data"""
        with st.spinner("Refreshing timeline data..."):
            self._collect_fresh_data(keyword)
    
    def _render_main_timeline(self, timeline_data: Dict[str, Any], time_period: str):
        """Render main timeline visualization"""
        timeline = timeline_data.get('timeline', [])
        
        if not timeline:
            st.warning("No timeline data to display")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(timeline)
        df['time'] = pd.to_datetime(df['time'])
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Post Volume & Engagement', 'Viral Score Trend'),
            vertical_spacing=0.1,
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )
        
        # Post volume bars
        fig.add_trace(
            go.Bar(
                x=df['time'],
                y=df['posts'],
                name='Posts',
                marker_color='rgba(55, 128, 191, 0.7)',
                yaxis='y'
            ),
            row=1, col=1
        )
        
        # Engagement line
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['engagement'],
                name='Engagement',
                line=dict(color='rgba(255, 127, 14, 1)', width=3),
                yaxis='y2'
            ),
            row=1, col=1
        )
        
        # Viral score trend
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['viral_score'],
                name='Viral Score',
                fill='tonexty',
                line=dict(color='rgba(44, 160, 44, 1)', width=2),
                fillcolor='rgba(44, 160, 44, 0.3)'
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"Viral Timeline Analysis - {timeline_data['keyword']} ({time_period})",
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Number of Posts", row=1, col=1)
        fig.update_yaxes(title_text="Engagement Count", secondary_y=True, row=1, col=1)
        fig.update_yaxes(title_text="Viral Score", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_analytics_cards(self, timeline_data: Dict[str, Any]):
        """Render analytics summary cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        timeline = timeline_data.get('timeline', [])
        total_posts = timeline_data.get('total_posts', 0)
        peak_time = timeline_data.get('peak_time', 'N/A')
        
        # Calculate metrics
        total_engagement = sum(item['engagement'] for item in timeline)
        avg_viral_score = np.mean([item['viral_score'] for item in timeline]) if timeline else 0
        peak_posts = max([item['posts'] for item in timeline]) if timeline else 0
        
        with col1:
            st.metric(
                label="Total Posts",
                value=f"{total_posts:,}",
                delta=f"+{len(timeline)} periods"
            )
        
        with col2:
            st.metric(
                label="Total Engagement",
                value=f"{total_engagement:,}",
                delta=f"Avg: {total_engagement//len(timeline) if timeline else 0}"
            )
        
        with col3:
            st.metric(
                label="Avg Viral Score",
                value=f"{avg_viral_score:.2f}",
                delta=f"Peak: {max([item['viral_score'] for item in timeline]) if timeline else 0:.2f}"
            )
        
        with col4:
            st.metric(
                label="Peak Activity",
                value=f"{peak_posts} posts",
                delta=f"At: {peak_time}"
            )
    
    def _render_detailed_breakdown(self, timeline_data: Dict[str, Any], time_period: str):
        """Render detailed timeline breakdown"""
        st.subheader("📊 Detailed Timeline Breakdown")
        
        timeline = timeline_data.get('timeline', [])
        
        if not timeline:
            st.info("No detailed data available")
            return
        
        # Create detailed DataFrame
        df = pd.DataFrame(timeline)
        df['time'] = pd.to_datetime(df['time'])
        df['engagement_rate'] = df['engagement'] / df['posts'].replace(0, 1)
        df['viral_category'] = pd.cut(
            df['viral_score'], 
            bins=[0, 0.2, 0.5, 0.8, 1.0], 
            labels=['Low', 'Medium', 'High', 'Viral']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Engagement rate distribution
            fig_eng = px.histogram(
                df, 
                x='engagement_rate',
                title='Engagement Rate Distribution',
                nbins=10,
                color_discrete_sequence=['#1f77b4']
            )
            fig_eng.update_layout(height=300)
            st.plotly_chart(fig_eng, use_container_width=True)
        
        with col2:
            # Viral score categories
            viral_counts = df['viral_category'].value_counts()
            fig_viral = px.pie(
                values=viral_counts.values,
                names=viral_counts.index,
                title='Viral Score Categories',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_viral.update_layout(height=300)
            st.plotly_chart(fig_viral, use_container_width=True)
        
        # Data table
        st.subheader("📋 Timeline Data Table")
        display_df = df.copy()
        display_df['time'] = display_df['time'].dt.strftime('%Y-%m-%d %H:%M')
        display_df = display_df.round(2)
        
        st.dataframe(
            display_df[['time', 'posts', 'engagement', 'viral_score', 'engagement_rate', 'viral_category']],
            use_container_width=True
        )
    
    def _render_peak_analysis(self, timeline_data: Dict[str, Any]):
        """Render peak activity analysis"""
        st.subheader("🎯 Peak Activity Analysis")
        
        timeline = timeline_data.get('timeline', [])
        
        if not timeline:
            st.info("No peak analysis data available")
            return
        
        # Find peaks
        df = pd.DataFrame(timeline)
        df['time'] = pd.to_datetime(df['time'])
        
        # Sort by different metrics
        top_posts = df.nlargest(3, 'posts')
        top_engagement = df.nlargest(3, 'engagement')
        top_viral = df.nlargest(3, 'viral_score')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔥 Top Post Volume**")
            for _, row in top_posts.iterrows():
                st.markdown(f"• **{row['posts']} posts** at {row['time'].strftime('%m/%d %H:%M')}")
        
        with col2:
            st.markdown("**💬 Top Engagement**")
            for _, row in top_engagement.iterrows():
                st.markdown(f"• **{row['engagement']:,} interactions** at {row['time'].strftime('%m/%d %H:%M')}")
        
        with col3:
            st.markdown("**⚡ Top Viral Score**")
            for _, row in top_viral.iterrows():
                st.markdown(f"• **{row['viral_score']:.2f} score** at {row['time'].strftime('%m/%d %H:%M')}")
        
        # Activity pattern analysis
        st.subheader("📈 Activity Patterns")
        
        # Hour-of-day analysis (if 24h period)
        if timeline_data.get('period') == '24h':
            df['hour'] = df['time'].dt.hour
            hourly_activity = df.groupby('hour').agg({
                'posts': 'sum',
                'engagement': 'sum',
                'viral_score': 'mean'
            }).reset_index()
            
            fig_hourly = px.bar(
                hourly_activity,
                x='hour',
                y='posts',
                title='Hourly Activity Pattern',
                labels={'hour': 'Hour of Day', 'posts': 'Total Posts'}
            )
            fig_hourly.update_layout(height=300)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Trend analysis
        if len(df) > 1:
            # Calculate trend
            df_sorted = df.sort_values('time')
            posts_trend = np.polyfit(range(len(df_sorted)), df_sorted['posts'], 1)[0]
            engagement_trend = np.polyfit(range(len(df_sorted)), df_sorted['engagement'], 1)[0]
            viral_trend = np.polyfit(range(len(df_sorted)), df_sorted['viral_score'], 1)[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trend_icon = "📈" if posts_trend > 0 else "📉" if posts_trend < 0 else "➡️"
                st.metric(
                    "Posts Trend",
                    f"{trend_icon}",
                    f"{posts_trend:+.2f} per period"
                )
            
            with col2:
                trend_icon = "📈" if engagement_trend > 0 else "📉" if engagement_trend < 0 else "➡️"
                st.metric(
                    "Engagement Trend",
                    f"{trend_icon}",
                    f"{engagement_trend:+.0f} per period"
                )
            
            with col3:
                trend_icon = "📈" if viral_trend > 0 else "📉" if viral_trend < 0 else "➡️"
                st.metric(
                    "Viral Score Trend",
                    f"{trend_icon}",
                    f"{viral_trend:+.3f} per period"
                )
    
    def get_timeline_summary(self, keyword: str, time_period: str) -> Dict[str, Any]:
        """Get timeline summary for other components"""
        timeline_data = self._get_timeline_data(keyword, time_period)
        
        if not timeline_data or not timeline_data.get('timeline'):
            return {}
        
        timeline = timeline_data['timeline']
        
        return {
            'total_posts': timeline_data.get('total_posts', 0),
            'total_periods': len(timeline),
            'peak_time': timeline_data.get('peak_time'),
            'avg_viral_score': np.mean([item['viral_score'] for item in timeline]),
            'total_engagement': sum(item['engagement'] for item in timeline),
            'trend_direction': self._calculate_trend_direction(timeline)
        }
    
    def _calculate_trend_direction(self, timeline: List[Dict]) -> str:
        """Calculate overall trend direction"""
        if len(timeline) < 2:
            return "stable"
        
        df = pd.DataFrame(timeline)
        posts_trend = np.polyfit(range(len(df)), df['posts'], 1)[0]
        
        if posts_trend > 0.1:
            return "increasing"
        elif posts_trend < -0.1:
            return "decreasing"
        else:
            return "stable"

# Test the component
if __name__ == "__main__":
    # This would be called from the main dashboard
    timeline = ViralTimelineEnhanced()
    
    # Test with sample data
    test_keyword = "climate change"
    print(f"Testing timeline for keyword: {test_keyword}")
    
    summary = timeline.get_timeline_summary(test_keyword, "24h")
    print(f"Timeline summary: {summary}")