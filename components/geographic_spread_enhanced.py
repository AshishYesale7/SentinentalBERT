#!/usr/bin/env python3
"""
Enhanced Geographic Spread Component for SentinentalBERT
Real-time geographic visualization with viral hotspot detection
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import sys
import os
import json
import random

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

class GeographicSpreadEnhanced:
    """Enhanced geographic spread visualization with real-time hotspot detection"""
    
    def __init__(self):
        self.cache_manager = EnhancedCacheManager()
        self.twitter_service = EnhancedTwitterService()
        
        # Major world cities for mock data
        self.world_cities = [
            {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090, "country_code": "IN"},
            {"city": "Mumbai", "country": "India", "lat": 19.0760, "lng": 72.8777, "country_code": "IN"},
            {"city": "Bangalore", "country": "India", "lat": 12.9716, "lng": 77.5946, "country_code": "IN"},
            {"city": "Chennai", "country": "India", "lat": 13.0827, "lng": 80.2707, "country_code": "IN"},
            {"city": "Kolkata", "country": "India", "lat": 22.5726, "lng": 88.3639, "country_code": "IN"},
            {"city": "Hyderabad", "country": "India", "lat": 17.3850, "lng": 78.4867, "country_code": "IN"},
            {"city": "London", "country": "United Kingdom", "lat": 51.5074, "lng": -0.1278, "country_code": "GB"},
            {"city": "New York", "country": "United States", "lat": 40.7128, "lng": -74.0060, "country_code": "US"},
            {"city": "Los Angeles", "country": "United States", "lat": 34.0522, "lng": -118.2437, "country_code": "US"},
            {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503, "country_code": "JP"},
            {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lng": 103.8198, "country_code": "SG"},
            {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lng": 55.2708, "country_code": "AE"},
            {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lng": 151.2093, "country_code": "AU"},
            {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lng": -79.3832, "country_code": "CA"},
            {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050, "country_code": "DE"},
            {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522, "country_code": "FR"},
            {"city": "São Paulo", "country": "Brazil", "lat": -23.5505, "lng": -46.6333, "country_code": "BR"},
            {"city": "Mexico City", "country": "Mexico", "lat": 19.4326, "lng": -99.1332, "country_code": "MX"},
            {"city": "Cairo", "country": "Egypt", "lat": 30.0444, "lng": 31.2357, "country_code": "EG"},
            {"city": "Lagos", "country": "Nigeria", "lat": 6.5244, "lng": 3.3792, "country_code": "NG"}
        ]
        
    def render_geographic_dashboard(self, keyword: str):
        """Render the complete geographic spread dashboard"""
        st.subheader("🌍 Geographic Spread Analysis")
        
        if not keyword:
            st.info("Enter a keyword to analyze geographic spread patterns")
            return
        
        # Control panel
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Analyzing Geographic Spread for:** `{keyword}`")
        
        with col2:
            map_style = st.selectbox(
                "Map Style",
                ["Satellite", "Street", "Terrain", "Dark"],
                help="Choose the map visualization style"
            )
        
        with col3:
            if st.button("🔄 Refresh Map", key="refresh_geo"):
                self._refresh_geographic_data(keyword)
                st.rerun()
        
        # Get geographic data
        geo_data = self._get_geographic_data(keyword)
        
        if not geo_data:
            st.warning("No geographic data available. Generating spread analysis...")
            self._generate_geographic_spread(keyword)
            geo_data = self._get_geographic_data(keyword)
        
        if geo_data:
            # Main world map
            self._render_world_map(geo_data, map_style)
            
            # Regional analysis
            self._render_regional_analysis(geo_data)
            
            # Hotspot detection
            self._render_hotspot_analysis(geo_data)
            
            # Spread timeline
            self._render_spread_timeline(keyword, geo_data)
        else:
            st.error("Unable to load geographic data. Please try again.")
    
    def _get_geographic_data(self, keyword: str) -> List[Dict]:
        """Get geographic spread data"""
        try:
            return self.cache_manager.get_geographic_spread(keyword)
        except Exception as e:
            logger.error(f"Error getting geographic data: {e}")
            return []
    
    def _generate_geographic_spread(self, keyword: str):
        """Generate geographic spread data"""
        try:
            with st.spinner("Analyzing geographic spread patterns..."):
                # Generate realistic spread data
                spread_data = []
                
                # Select random cities with weighted probability (India gets higher weight)
                selected_cities = random.choices(
                    self.world_cities, 
                    weights=[3 if city['country_code'] == 'IN' else 1 for city in self.world_cities],
                    k=random.randint(8, 15)
                )
                
                for city in selected_cities:
                    # Generate realistic metrics
                    base_posts = random.randint(5, 100)
                    engagement_multiplier = random.uniform(0.5, 3.0)
                    sentiment_bias = random.uniform(-0.5, 0.5)
                    
                    spread_data.append({
                        'country_code': city['country_code'],
                        'region': city['country'],
                        'city': city['city'],
                        'latitude': city['lat'],
                        'longitude': city['lng'],
                        'post_count': base_posts,
                        'engagement': int(base_posts * engagement_multiplier),
                        'sentiment': sentiment_bias
                    })
                
                # Store in cache
                if spread_data:
                    self.cache_manager.update_geographic_spread(keyword, spread_data)
                    st.success(f"Generated geographic spread data for {len(spread_data)} locations")
                
        except Exception as e:
            logger.error(f"Error generating geographic spread: {e}")
            st.error(f"Error generating spread data: {e}")
    
    def _refresh_geographic_data(self, keyword: str):
        """Refresh geographic data"""
        with st.spinner("Refreshing geographic spread data..."):
            self._generate_geographic_spread(keyword)
    
    def _render_world_map(self, geo_data: List[Dict], map_style: str):
        """Render interactive world map"""
        if not geo_data:
            st.warning("No geographic data to display on map")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(geo_data)
        
        # Calculate bubble sizes (normalize post counts)
        max_posts = df['posts'].max() if not df.empty else 1
        df['bubble_size'] = (df['posts'] / max_posts * 50) + 10  # Scale between 10-60
        
        # Create color scale based on sentiment
        df['sentiment_color'] = df['sentiment'].apply(
            lambda x: 'Positive' if x > 0.1 else 'Negative' if x < -0.1 else 'Neutral'
        )
        
        # Create the map
        fig = px.scatter_mapbox(
            df,
            lat='lat',
            lon='lng',
            size='bubble_size',
            color='sentiment_color',
            hover_name='city',
            hover_data={
                'country': True,
                'posts': True,
                'engagement': True,
                'sentiment': ':.3f',
                'lat': False,
                'lng': False,
                'bubble_size': False
            },
            color_discrete_map={
                'Positive': '#2E8B57',
                'Negative': '#DC143C',
                'Neutral': '#708090'
            },
            size_max=60,
            zoom=1,
            height=600,
            title="Global Content Spread - Real-time Viral Hotspots"
        )
        
        # Set map style
        mapbox_style = {
            "Satellite": "satellite",
            "Street": "open-street-map",
            "Terrain": "stamen-terrain",
            "Dark": "carto-darkmatter"
        }.get(map_style, "open-street-map")
        
        fig.update_layout(
            mapbox_style=mapbox_style,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Map statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_locations = len(df)
            st.metric("Active Locations", total_locations)
        
        with col2:
            total_posts = df['posts'].sum()
            st.metric("Total Posts", f"{total_posts:,}")
        
        with col3:
            total_engagement = df['engagement'].sum()
            st.metric("Total Engagement", f"{total_engagement:,}")
        
        with col4:
            avg_sentiment = df['sentiment'].mean()
            sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😞" if avg_sentiment < -0.1 else "😐"
            st.metric("Global Sentiment", f"{sentiment_emoji} {avg_sentiment:.3f}")
    
    def _render_regional_analysis(self, geo_data: List[Dict]):
        """Render regional analysis breakdown"""
        st.subheader("🌏 Regional Analysis")
        
        if not geo_data:
            st.warning("No regional data available")
            return
        
        df = pd.DataFrame(geo_data)
        
        # Group by country/region
        regional_stats = df.groupby('country').agg({
            'posts': 'sum',
            'engagement': 'sum',
            'sentiment': 'mean',
            'city': 'count'
        }).reset_index()
        regional_stats.columns = ['Country', 'Total Posts', 'Total Engagement', 'Avg Sentiment', 'Cities']
        regional_stats = regional_stats.sort_values('Total Posts', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top countries by posts
            fig_countries = px.bar(
                regional_stats.head(10),
                x='Total Posts',
                y='Country',
                orientation='h',
                title='Top Countries by Post Volume',
                color='Avg Sentiment',
                color_continuous_scale='RdYlGn'
            )
            fig_countries.update_layout(height=400)
            st.plotly_chart(fig_countries, use_container_width=True)
        
        with col2:
            # Engagement vs Posts scatter
            fig_scatter = px.scatter(
                regional_stats,
                x='Total Posts',
                y='Total Engagement',
                size='Cities',
                color='Avg Sentiment',
                hover_name='Country',
                title='Engagement vs Post Volume by Country',
                color_continuous_scale='RdYlGn'
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Regional data table
        st.subheader("📊 Regional Statistics")
        
        # Format the dataframe for display
        display_df = regional_stats.copy()
        display_df['Avg Sentiment'] = display_df['Avg Sentiment'].round(3)
        display_df['Engagement Rate'] = (display_df['Total Engagement'] / display_df['Total Posts']).round(2)
        
        st.dataframe(display_df, use_container_width=True)
    
    def _render_hotspot_analysis(self, geo_data: List[Dict]):
        """Render viral hotspot analysis"""
        st.subheader("🔥 Viral Hotspot Detection")
        
        if not geo_data:
            st.warning("No hotspot data available")
            return
        
        df = pd.DataFrame(geo_data)
        
        # Calculate hotspot scores
        df['engagement_rate'] = df['engagement'] / df['posts']
        df['hotspot_score'] = (
            (df['posts'] / df['posts'].max()) * 0.4 +
            (df['engagement'] / df['engagement'].max()) * 0.4 +
            (df['engagement_rate'] / df['engagement_rate'].max()) * 0.2
        )
        
        # Identify hotspots (top 20% by score)
        hotspot_threshold = df['hotspot_score'].quantile(0.8)
        hotspots = df[df['hotspot_score'] >= hotspot_threshold].sort_values('hotspot_score', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Hotspot map
            if not hotspots.empty:
                fig_hotspots = px.scatter_mapbox(
                    hotspots,
                    lat='lat',
                    lon='lng',
                    size='hotspot_score',
                    color='hotspot_score',
                    hover_name='city',
                    hover_data=['country', 'posts', 'engagement'],
                    color_continuous_scale='Reds',
                    size_max=50,
                    zoom=2,
                    height=400,
                    title="Detected Viral Hotspots"
                )
                
                fig_hotspots.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r": 0, "t": 50, "l": 0, "b": 0}
                )
                
                st.plotly_chart(fig_hotspots, use_container_width=True)
            else:
                st.info("No significant hotspots detected")
        
        with col2:
            st.markdown("**🏆 Top Viral Hotspots**")
            
            if not hotspots.empty:
                for i, (_, hotspot) in enumerate(hotspots.head(5).iterrows(), 1):
                    st.markdown(f"""
                    **#{i} {hotspot['city']}, {hotspot['country']}**
                    - Posts: {hotspot['posts']:,}
                    - Engagement: {hotspot['engagement']:,}
                    - Hotspot Score: {hotspot['hotspot_score']:.3f}
                    """)
            else:
                st.info("No hotspots to display")
        
        # Hotspot characteristics
        if not hotspots.empty:
            st.subheader("📈 Hotspot Characteristics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_posts = hotspots['posts'].mean()
                st.metric("Avg Posts in Hotspots", f"{avg_posts:.0f}")
            
            with col2:
                avg_engagement = hotspots['engagement'].mean()
                st.metric("Avg Engagement in Hotspots", f"{avg_engagement:.0f}")
            
            with col3:
                avg_engagement_rate = hotspots['engagement_rate'].mean()
                st.metric("Avg Engagement Rate", f"{avg_engagement_rate:.2f}")
            
            with col4:
                hotspot_sentiment = hotspots['sentiment'].mean()
                sentiment_emoji = "😊" if hotspot_sentiment > 0.1 else "😞" if hotspot_sentiment < -0.1 else "😐"
                st.metric("Hotspot Sentiment", f"{sentiment_emoji} {hotspot_sentiment:.3f}")
    
    def _render_spread_timeline(self, keyword: str, geo_data: List[Dict]):
        """Render geographic spread timeline"""
        st.subheader("⏰ Geographic Spread Timeline")
        
        if not geo_data:
            st.warning("No timeline data available")
            return
        
        # Generate mock timeline data (in real implementation, this would come from database)
        timeline_data = self._generate_spread_timeline(keyword, geo_data)
        
        if not timeline_data:
            st.info("No timeline data to display")
            return
        
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline['timestamp'] = pd.to_datetime(df_timeline['timestamp'])
        
        # Cumulative spread over time
        df_timeline_sorted = df_timeline.sort_values('timestamp')
        df_timeline_sorted['cumulative_locations'] = range(1, len(df_timeline_sorted) + 1)
        df_timeline_sorted['cumulative_posts'] = df_timeline_sorted['posts'].cumsum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Geographic spread over time
            fig_spread = px.line(
                df_timeline_sorted,
                x='timestamp',
                y='cumulative_locations',
                title='Geographic Spread Over Time',
                labels={'cumulative_locations': 'Number of Locations', 'timestamp': 'Time'}
            )
            fig_spread.update_layout(height=300)
            st.plotly_chart(fig_spread, use_container_width=True)
        
        with col2:
            # Post volume over time
            fig_volume = px.line(
                df_timeline_sorted,
                x='timestamp',
                y='cumulative_posts',
                title='Cumulative Post Volume',
                labels={'cumulative_posts': 'Total Posts', 'timestamp': 'Time'}
            )
            fig_volume.update_layout(height=300)
            st.plotly_chart(fig_volume, use_container_width=True)
        
        # Spread velocity analysis
        st.subheader("🚀 Spread Velocity Analysis")
        
        if len(df_timeline_sorted) > 1:
            # Calculate time differences
            time_diffs = df_timeline_sorted['timestamp'].diff().dt.total_seconds() / 3600  # Hours
            avg_spread_time = time_diffs.mean()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Time Between Locations", f"{avg_spread_time:.1f} hours")
            
            with col2:
                total_spread_time = (df_timeline_sorted['timestamp'].max() - df_timeline_sorted['timestamp'].min()).total_seconds() / 3600
                st.metric("Total Spread Duration", f"{total_spread_time:.1f} hours")
            
            with col3:
                spread_velocity = len(df_timeline_sorted) / total_spread_time if total_spread_time > 0 else 0
                st.metric("Spread Velocity", f"{spread_velocity:.2f} locations/hour")
    
    def _generate_spread_timeline(self, keyword: str, geo_data: List[Dict]) -> List[Dict]:
        """Generate mock spread timeline data"""
        try:
            timeline_data = []
            base_time = datetime.now() - timedelta(hours=24)
            
            # Sort locations by post count (simulate spread pattern)
            sorted_locations = sorted(geo_data, key=lambda x: x['posts'], reverse=True)
            
            for i, location in enumerate(sorted_locations):
                # Simulate realistic spread timing
                time_offset = i * random.uniform(0.5, 3.0)  # Hours between locations
                timestamp = base_time + timedelta(hours=time_offset)
                
                timeline_data.append({
                    'timestamp': timestamp,
                    'city': location['city'],
                    'country': location['country'],
                    'posts': location['posts'],
                    'engagement': location['engagement'],
                    'lat': location['lat'],
                    'lng': location['lng']
                })
            
            return timeline_data
            
        except Exception as e:
            logger.error(f"Error generating spread timeline: {e}")
            return []
    
    def get_geographic_summary(self, keyword: str) -> Dict[str, Any]:
        """Get geographic summary for other components"""
        geo_data = self._get_geographic_data(keyword)
        
        if not geo_data:
            return {}
        
        df = pd.DataFrame(geo_data)
        
        # Calculate hotspot threshold
        if not df.empty:
            df['engagement_rate'] = df['engagement'] / df['posts']
            df['hotspot_score'] = (
                (df['posts'] / df['posts'].max()) * 0.4 +
                (df['engagement'] / df['engagement'].max()) * 0.4 +
                (df['engagement_rate'] / df['engagement_rate'].max()) * 0.2
            )
            
            hotspot_threshold = df['hotspot_score'].quantile(0.8)
            hotspots = df[df['hotspot_score'] >= hotspot_threshold]
            
            return {
                'total_locations': len(df),
                'total_countries': df['country'].nunique(),
                'total_posts': df['posts'].sum(),
                'total_engagement': df['engagement'].sum(),
                'global_sentiment': df['sentiment'].mean(),
                'hotspot_count': len(hotspots),
                'top_hotspot': hotspots.loc[hotspots['hotspot_score'].idxmax(), 'city'] if not hotspots.empty else None,
                'most_active_country': df.groupby('country')['posts'].sum().idxmax()
            }
        else:
            return {}

# Test the component
if __name__ == "__main__":
    # This would be called from the main dashboard
    geographic_spread = GeographicSpreadEnhanced()
    
    # Test with sample data
    test_keyword = "climate change"
    print(f"Testing geographic spread for keyword: {test_keyword}")
    
    summary = geographic_spread.get_geographic_summary(test_keyword)
    print(f"Geographic summary: {summary}")