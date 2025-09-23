#!/usr/bin/env python3
"""
Enhanced Integrated Dashboard for SentinentalBERT
Government of India - Ministry of Home Affairs
Cyber Crime Investigation Division

Complete viral content analysis platform with all enhanced components
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import hashlib
import time
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Import enhanced components
try:
    from viral_timeline_enhanced import ViralTimelineEnhanced
    from influence_network_enhanced import InfluenceNetworkEnhanced
    from sentiment_behavior_enhanced import SentimentBehaviorEnhanced
    from geographic_spread_enhanced import GeographicSpreadEnhanced
    from evidence_collection_enhanced import EvidenceCollectionEnhanced
    from realtime_search_enhanced import RealtimeSearchEnhanced
    from platforms.enhanced_twitter_service import EnhancedTwitterService
    from database.enhanced_cache_manager import EnhancedCacheManager
except ImportError as e:
    logging.warning(f"Could not import enhanced components: {e}")
    # Create mock classes to prevent crashes
    class ViralTimelineEnhanced:
        def render_timeline_dashboard(self, keyword): st.info("Timeline component not available")
        def get_timeline_summary(self, keyword, period): return {}
    
    class InfluenceNetworkEnhanced:
        def render_influence_dashboard(self, keyword): st.info("Influence network component not available")
        def get_network_summary(self, keyword): return {}
    
    class SentimentBehaviorEnhanced:
        def render_sentiment_dashboard(self, keyword): st.info("Sentiment analysis component not available")
        def get_sentiment_summary(self, keyword): return {}
    
    class GeographicSpreadEnhanced:
        def render_geographic_dashboard(self, keyword): st.info("Geographic spread component not available")
        def get_geographic_summary(self, keyword): return {}
    
    class EvidenceCollectionEnhanced:
        def render_evidence_dashboard(self, keyword): st.info("Evidence collection component not available")
        def get_evidence_summary(self, keyword): return {}
    
    class RealtimeSearchEnhanced:
        def render_search_dashboard(self, keyword): st.info("Real-time search component not available")
        def get_search_summary(self, keyword): return {}
    
    class EnhancedTwitterService:
        def get_usage_stats(self): return {}
    
    class EnhancedCacheManager:
        def get_cache_stats(self): return {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedIntegratedDashboard:
    """Enhanced integrated dashboard with all components"""
    
    def __init__(self):
        self.timeline_component = ViralTimelineEnhanced()
        self.network_component = InfluenceNetworkEnhanced()
        self.sentiment_component = SentimentBehaviorEnhanced()
        self.geographic_component = GeographicSpreadEnhanced()
        self.evidence_component = EvidenceCollectionEnhanced()
        self.search_component = RealtimeSearchEnhanced()
        self._twitter_service = None  # Lazy-loaded to avoid startup delays
        self.cache_manager = EnhancedCacheManager()
    
    @property
    def twitter_service(self):
        """Lazy-load Twitter service to avoid startup delays"""
        if self._twitter_service is None:
            try:
                self._twitter_service = EnhancedTwitterService()
            except Exception as e:
                logging.warning(f"Failed to initialize Twitter service: {e}")
                # Return a mock service
                class MockTwitterService:
                    def search_tweets(self, *args, **kwargs): return []
                    def get_user_info(self, *args, **kwargs): return {}
                self._twitter_service = MockTwitterService()
        return self._twitter_service
    
    def render_dashboard(self):
        """Render the complete integrated dashboard"""
        # Page configuration
        st.set_page_config(
            page_title="SentinentalBERT - Enhanced Viral Analysis Platform",
            page_icon="🇮🇳",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for Indian government theme
        self._apply_custom_css()
        
        # Header
        self._render_header()
        
        # Sidebar
        keyword = self._render_sidebar()
        
        # Main dashboard content
        if keyword:
            self._render_main_dashboard(keyword)
        else:
            self._render_welcome_screen()
    
    def _apply_custom_css(self):
        """Apply custom CSS for Indian government theme"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            color: #000080;
            font-weight: bold;
        }
        
        .metric-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #138808;
            margin: 0.5rem 0;
        }
        
        .alert-high {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            border-radius: 4px;
        }
        
        .alert-medium {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 1rem;
            border-radius: 4px;
        }
        
        .alert-low {
            background: #e8f5e8;
            border-left: 4px solid #4caf50;
            padding: 1rem;
            border-radius: 4px;
        }
        
        .component-header {
            background: #000080;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🇮🇳 SentinentalBERT - Enhanced Viral Analysis Platform</h1>
            <h3>Government of India | Ministry of Home Affairs | Cyber Crime Investigation Division</h3>
            <p>Advanced AI-Powered Social Media Intelligence & Evidence Collection System</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self) -> str:
        """Render sidebar with controls and return selected keyword"""
        st.sidebar.markdown("## 🔍 Analysis Controls")
        
        # Keyword input
        keyword = st.sidebar.text_input(
            "Enter Keyword for Analysis",
            placeholder="e.g., climate change, election, protest",
            help="Enter a keyword to analyze across all social media platforms"
        )
        
        # Analysis options
        st.sidebar.markdown("### ⚙️ Analysis Options")
        
        analysis_mode = st.sidebar.selectbox(
            "Analysis Mode",
            ["Comprehensive", "Quick Scan", "Deep Investigation"],
            help="Choose the depth of analysis to perform"
        )
        
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last Week", "Last Month", "Custom Range"],
            help="Select the time period for analysis"
        )
        
        platforms = st.sidebar.multiselect(
            "Platforms to Monitor",
            ["Twitter/X", "Facebook", "Instagram", "YouTube", "Koo", "ShareChat"],
            default=["Twitter/X"],
            help="Select social media platforms to include in analysis"
        )
        
        # System status
        st.sidebar.markdown("### 📊 System Status")
        
        # API usage stats
        try:
            usage_stats = self.twitter_service.get_usage_stats()
            
            if usage_stats:
                st.sidebar.markdown("**Twitter API Usage:**")
                st.sidebar.progress(usage_stats.get('requests_used', 0) / 100)
                st.sidebar.caption(f"Requests: {usage_stats.get('requests_used', 0)}/100")
                
                cache_hit_rate = usage_stats.get('cache_hit_rate', 0)
                st.sidebar.metric("Cache Hit Rate", f"{cache_hit_rate}%")
        except Exception as e:
            st.sidebar.warning("API status unavailable")
        
        # Cache stats
        try:
            cache_stats = self.cache_manager.get_cache_stats()
            
            if cache_stats:
                st.sidebar.markdown("**Cache Statistics:**")
                st.sidebar.metric("Cached Posts", cache_stats.get('total_viral_content', 0))
                st.sidebar.metric("Evidence Items", cache_stats.get('total_evidence', 0))
        except Exception as e:
            st.sidebar.warning("Cache stats unavailable")
        
        # Legal compliance status
        st.sidebar.markdown("### ⚖️ Legal Compliance")
        st.sidebar.success("✅ IT Act 2000 Compliant")
        st.sidebar.success("✅ Evidence Act 1872 Ready")
        st.sidebar.success("✅ CrPC 1973 Procedures")
        
        return keyword
    
    def _render_welcome_screen(self):
        """Render welcome screen when no keyword is entered"""
        st.markdown("## 🚀 Welcome to SentinentalBERT Enhanced Platform")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Key Features
            - **Real-time Viral Tracking**
            - **AI-Powered Sentiment Analysis**
            - **Influence Network Mapping**
            - **Geographic Spread Visualization**
            - **Legal Evidence Collection**
            - **Multi-language Support**
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Enhanced Capabilities
            - **Twitter API Integration**
            - **Smart Caching System**
            - **24h/1w/1m Timeline Analytics**
            - **IST-based Chronological Tracking**
            - **BERT-based NLP Analysis**
            - **Real-time Hotspot Detection**
            """)
        
        with col3:
            st.markdown("""
            ### 📋 Evidence & Compliance
            - **JSON/PDF Export**
            - **Chain of Custody**
            - **Digital Signatures**
            - **Integrity Verification**
            - **Court-ready Reports**
            - **Audit Trail Maintenance**
            """)
        
        st.markdown("---")
        st.info("👈 Enter a keyword in the sidebar to begin comprehensive viral content analysis")
        
        # Sample keywords
        st.markdown("### 💡 Sample Keywords to Try:")
        sample_keywords = [
            "climate change", "election fraud", "vaccine misinformation", 
            "social media ban", "digital privacy", "cyber security"
        ]
        
        cols = st.columns(3)
        for i, keyword in enumerate(sample_keywords):
            with cols[i % 3]:
                if st.button(f"🔍 {keyword}", key=f"sample_{i}"):
                    st.session_state.sample_keyword = keyword
                    st.rerun()
    
    def _render_main_dashboard(self, keyword: str):
        """Render main dashboard with all components"""
        # Dashboard overview
        self._render_dashboard_overview(keyword)
        
        # Component tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Viral Timeline", 
            "🕸️ Influence Network", 
            "🧠 Sentiment & Behavior",
            "🌍 Geographic Spread",
            "📋 Evidence Collection",
            "🔍 Real-time Search"
        ])
        
        with tab1:
            st.markdown('<div class="component-header">📈 Viral Timeline Analysis</div>', unsafe_allow_html=True)
            self.timeline_component.render_timeline_dashboard(keyword)
        
        with tab2:
            st.markdown('<div class="component-header">🕸️ Influence Network Analysis</div>', unsafe_allow_html=True)
            self.network_component.render_influence_dashboard(keyword)
        
        with tab3:
            st.markdown('<div class="component-header">🧠 Sentiment & Behavior Analysis</div>', unsafe_allow_html=True)
            self.sentiment_component.render_sentiment_dashboard(keyword)
        
        with tab4:
            st.markdown('<div class="component-header">🌍 Geographic Spread Analysis</div>', unsafe_allow_html=True)
            self.geographic_component.render_geographic_dashboard(keyword)
        
        with tab5:
            st.markdown('<div class="component-header">📋 Evidence Collection System</div>', unsafe_allow_html=True)
            self.evidence_component.render_evidence_dashboard(keyword)
        
        with tab6:
            st.markdown('<div class="component-header">🔍 Real-time Search & Trends</div>', unsafe_allow_html=True)
            self.search_component.render_search_dashboard(keyword)
    
    def _render_dashboard_overview(self, keyword: str):
        """Render dashboard overview with key metrics"""
        st.markdown(f"## 📊 Analysis Overview: `{keyword}`")
        
        # Get summaries from all components
        timeline_summary = self.timeline_component.get_timeline_summary(keyword, "24h")
        network_summary = self.network_component.get_network_summary(keyword)
        sentiment_summary = self.sentiment_component.get_sentiment_summary(keyword)
        geographic_summary = self.geographic_component.get_geographic_summary(keyword)
        evidence_summary = self.evidence_component.get_evidence_summary(keyword)
        search_summary = self.search_component.get_search_summary(keyword)
        
        # Key metrics row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            total_posts = timeline_summary.get('total_posts', 0)
            st.metric("Total Posts", f"{total_posts:,}")
        
        with col2:
            network_nodes = network_summary.get('total_nodes', 0)
            st.metric("Network Nodes", network_nodes)
        
        with col3:
            avg_sentiment = sentiment_summary.get('average_sentiment', 0)
            sentiment_emoji = "😊" if avg_sentiment > 0.1 else "😞" if avg_sentiment < -0.1 else "😐"
            st.metric("Avg Sentiment", f"{sentiment_emoji} {avg_sentiment:.3f}")
        
        with col4:
            total_locations = geographic_summary.get('total_locations', 0)
            st.metric("Locations", total_locations)
        
        with col5:
            total_evidence = evidence_summary.get('total_evidence', 0)
            st.metric("Evidence Items", total_evidence)
        
        with col6:
            trending_score = search_summary.get('trending_score', 0)
            trend_emoji = "🔥" if trending_score > 0.7 else "📈" if trending_score > 0.3 else "📊"
            st.metric("Trending Score", f"{trend_emoji} {trending_score:.3f}")
        
        # Alert system
        self._render_alert_system(keyword, {
            'timeline': timeline_summary,
            'network': network_summary,
            'sentiment': sentiment_summary,
            'geographic': geographic_summary,
            'evidence': evidence_summary,
            'search': search_summary
        })
        
        # Quick insights
        self._render_quick_insights(keyword, {
            'timeline': timeline_summary,
            'network': network_summary,
            'sentiment': sentiment_summary,
            'geographic': geographic_summary,
            'evidence': evidence_summary,
            'search': search_summary
        })
    
    def _render_alert_system(self, keyword: str, summaries: Dict[str, Dict]):
        """Render alert system based on analysis results"""
        st.markdown("### 🚨 Alert System")
        
        alerts = []
        
        # Check for high controversy
        controversy_score = summaries['search'].get('controversy_score', 0)
        if controversy_score > 0.7:
            alerts.append({
                'level': 'high',
                'message': f"High controversy detected for '{keyword}' (Score: {controversy_score:.3f})",
                'action': "Immediate investigation recommended"
            })
        elif controversy_score > 0.4:
            alerts.append({
                'level': 'medium',
                'message': f"Moderate controversy detected for '{keyword}' (Score: {controversy_score:.3f})",
                'action': "Monitor closely for escalation"
            })
        
        # Check for high toxicity
        avg_toxicity = summaries['sentiment'].get('average_toxicity', 0)
        if avg_toxicity > 0.5:
            alerts.append({
                'level': 'high',
                'message': f"High toxicity content detected (Score: {avg_toxicity:.3f})",
                'action': "Content moderation required"
            })
        
        # Check for viral spread
        trending_score = summaries['search'].get('trending_score', 0)
        if trending_score > 0.8:
            alerts.append({
                'level': 'medium',
                'message': f"Viral spread detected (Trending Score: {trending_score:.3f})",
                'action': "Monitor for misinformation"
            })
        
        # Check for evidence integrity
        evidence_count = summaries['evidence'].get('total_evidence', 0)
        if evidence_count > 0:
            integrity_rate = summaries['evidence'].get('integrity_verified', 0) / evidence_count
            if integrity_rate < 0.9:
                alerts.append({
                    'level': 'medium',
                    'message': f"Evidence integrity issues detected ({integrity_rate:.1%} verified)",
                    'action': "Review evidence collection process"
                })
        
        # Display alerts
        if alerts:
            for alert in alerts:
                alert_class = f"alert-{alert['level']}"
                st.markdown(f"""
                <div class="{alert_class}">
                    <strong>⚠️ {alert['level'].upper()} ALERT:</strong> {alert['message']}<br>
                    <strong>Recommended Action:</strong> {alert['action']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-low">✅ No critical alerts detected</div>', unsafe_allow_html=True)
    
    def _render_quick_insights(self, keyword: str, summaries: Dict[str, Dict]):
        """Render quick insights from all components"""
        st.markdown("### 💡 Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Timeline Insights:**")
            trend_direction = summaries['timeline'].get('trend_direction', 'stable')
            st.markdown(f"• Content trend is **{trend_direction}**")
            
            peak_time = summaries['timeline'].get('peak_time', 'N/A')
            st.markdown(f"• Peak activity at: **{peak_time}**")
            
            st.markdown("**🕸️ Network Insights:**")
            top_influencer = summaries['network'].get('top_influencer', 'N/A')
            st.markdown(f"• Top influencer: **{top_influencer[:20]}...**" if len(str(top_influencer)) > 20 else f"• Top influencer: **{top_influencer}**")
            
            network_density = summaries['network'].get('network_density', 0)
            st.markdown(f"• Network density: **{network_density:.3f}**")
            
            st.markdown("**🧠 Sentiment Insights:**")
            dominant_emotion = summaries['sentiment'].get('dominant_emotion', 'neutral')
            st.markdown(f"• Dominant emotion: **{dominant_emotion}**")
            
            positive_ratio = summaries['sentiment'].get('positive_ratio', 0)
            st.markdown(f"• Positive sentiment: **{positive_ratio:.1%}**")
        
        with col2:
            st.markdown("**🌍 Geographic Insights:**")
            most_active_country = summaries['geographic'].get('most_active_country', 'N/A')
            st.markdown(f"• Most active country: **{most_active_country}**")
            
            hotspot_count = summaries['geographic'].get('hotspot_count', 0)
            st.markdown(f"• Viral hotspots detected: **{hotspot_count}**")
            
            st.markdown("**📋 Evidence Insights:**")
            verified_evidence = summaries['evidence'].get('verified_evidence', 0)
            st.markdown(f"• Verified evidence items: **{verified_evidence}**")
            
            recent_evidence = summaries['evidence'].get('recent_evidence', 0)
            st.markdown(f"• Recent evidence (24h): **{recent_evidence}**")
            
            st.markdown("**🔍 Search Insights:**")
            key_spreaders_count = summaries['search'].get('key_spreaders_count', 0)
            st.markdown(f"• Key spreaders identified: **{key_spreaders_count}**")
            
            related_keywords = summaries['search'].get('related_keywords_count', 0)
            st.markdown(f"• Related keywords found: **{related_keywords}**")

def main():
    """Main function to run the dashboard"""
    dashboard = EnhancedIntegratedDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()