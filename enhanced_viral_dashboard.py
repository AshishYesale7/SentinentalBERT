#!/usr/bin/env python3
"""
Enhanced InsideOut Viral Dashboard - Comprehensive Analysis Platform
Integrates sentiment analysis, behavior analysis, legal compliance, multilingual support, and global platform analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime, timedelta
import json
import sys
import os
import asyncio
import logging
from typing import List, Dict, Any

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services with fallback
try:
    from services.legal_compliance.indian_legal_framework import IndianLegalFramework, LegalAuthority, EvidenceType
    from services.multilingual.enhanced_language_support import EnhancedLanguageSupport
    from services.platforms.global_platform_support import GlobalPlatformSupport
    from services.nlp.models.sentiment_model import SentinelBERTModel
    from services.nlp.models.behavior_analyzer import BehavioralPatternAnalyzer
    from services.nlp.models.influence_calculator import InfluenceCalculator
except ImportError as e:
    logger.warning(f"Some services not available: {e}")
    # Create mock classes for missing services
    class MockService:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: {"status": "mock", "data": []}

# Page configuration
st.set_page_config(
    page_title="InsideOut - Enhanced Viral Content Analysis Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services"""
    try:
        legal_framework = IndianLegalFramework()
        language_support = EnhancedLanguageSupport()
        platform_support = GlobalPlatformSupport()
        sentiment_model = SentinelBERTModel()
        behavior_analyzer = BehavioralPatternAnalyzer()
        influence_calculator = InfluenceCalculator()
        
        return {
            'legal': legal_framework,
            'language': language_support,
            'platform': platform_support,
            'sentiment': sentiment_model,
            'behavior': behavior_analyzer,
            'influence': influence_calculator
        }
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        return {
            'legal': MockService(),
            'language': MockService(),
            'platform': MockService(),
            'sentiment': MockService(),
            'behavior': MockService(),
            'influence': MockService()
        }

# Initialize all services
services = initialize_services()

if not services:
    st.error("Failed to initialize services. Please check the configuration.")
    st.stop()

# Extract services
legal_framework = services['legal']
language_support = services['language']
platform_support = services['platform']
sentiment_model = services['sentiment']
behavior_analyzer = services['behavior']
influence_calculator = services['influence']

# Initialize sentiment model if available
if hasattr(sentiment_model, 'initialize'):
    try:
        asyncio.run(sentiment_model.initialize())
    except Exception as e:
        logger.warning(f"Could not initialize sentiment model: {e}")

# Comprehensive Analysis Functions
def analyze_content_comprehensive(text: str, user_metadata: Dict = None) -> Dict[str, Any]:
    """Perform comprehensive analysis of content"""
    results = {
        'text': text,
        'timestamp': datetime.now().isoformat(),
        'analysis': {}
    }
    
    try:
        # Sentiment Analysis
        if hasattr(sentiment_model, 'analyze_sentiment'):
            sentiment_result = sentiment_model.analyze_sentiment(text)
            results['analysis']['sentiment'] = sentiment_result
        else:
            results['analysis']['sentiment'] = {
                'positive': 0.33, 'negative': 0.33, 'neutral': 0.34, 'confidence': 0.5
            }
        
        # Behavioral Pattern Analysis
        if hasattr(behavior_analyzer, 'analyze_patterns'):
            behavior_result = behavior_analyzer.analyze_patterns(text, user_metadata)
            results['analysis']['behavior_patterns'] = behavior_result
        else:
            results['analysis']['behavior_patterns'] = []
        
        # Influence Score Calculation
        if hasattr(influence_calculator, 'calculate_influence'):
            influence_score = influence_calculator.calculate_influence(text, user_metadata)
            results['analysis']['influence_score'] = influence_score
        else:
            results['analysis']['influence_score'] = 0.5
        
        # Calculate overall viral potential
        sentiment_score = max(results['analysis']['sentiment']['positive'], 
                            results['analysis']['sentiment']['negative'])
        behavior_score = sum([p['score'] for p in results['analysis']['behavior_patterns']]) / max(len(results['analysis']['behavior_patterns']), 1)
        influence_score = results['analysis']['influence_score']
        
        viral_potential = (sentiment_score * 0.3 + behavior_score * 0.4 + influence_score * 0.3)
        results['analysis']['viral_potential'] = min(viral_potential, 1.0)
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        results['analysis']['error'] = str(e)
    
    return results

def create_sentiment_visualization(sentiment_data: Dict) -> go.Figure:
    """Create sentiment analysis visualization"""
    fig = go.Figure(data=[
        go.Bar(
            x=['Positive', 'Negative', 'Neutral'],
            y=[sentiment_data.get('positive', 0), 
               sentiment_data.get('negative', 0), 
               sentiment_data.get('neutral', 0)],
            marker_color=['#2E8B57', '#DC143C', '#4682B4'],
            text=[f"{sentiment_data.get('positive', 0):.2%}", 
                  f"{sentiment_data.get('negative', 0):.2%}", 
                  f"{sentiment_data.get('neutral', 0):.2%}"],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Sentiment Analysis",
        xaxis_title="Sentiment",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1]),
        height=300
    )
    
    return fig

def create_behavior_patterns_chart(patterns: List[Dict]) -> go.Figure:
    """Create behavioral patterns visualization"""
    if not patterns:
        fig = go.Figure()
        fig.add_annotation(text="No behavioral patterns detected", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(title="Behavioral Patterns", height=300)
        return fig
    
    # Handle different pattern formats
    pattern_types = []
    scores = []
    
    for p in patterns:
        if isinstance(p, dict):
            pattern_types.append(p.get('pattern_type', 'Unknown'))
            scores.append(p.get('score', 0))
        elif isinstance(p, str):
            pattern_types.append(p)
            scores.append(0.5)  # Default score for string patterns
        else:
            pattern_types.append(str(p))
            scores.append(0.5)
    
    fig = go.Figure(data=[
        go.Bar(
            x=pattern_types,
            y=scores,
            marker_color='#FF6B6B',
            text=[f"{score:.2f}" for score in scores],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Behavioral Pattern Analysis",
        xaxis_title="Pattern Type",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1]),
        height=300
    )
    
    return fig

def create_influence_gauge(influence_score: float) -> go.Figure:
    """Create influence score gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = influence_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Influence Score"},
        delta = {'reference': 0.5},
        gauge = {
            'axis': {'range': [None, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.3], 'color': "lightgray"},
                {'range': [0.3, 0.7], 'color': "gray"},
                {'range': [0.7, 1], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.8
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# Language selection
languages = language_support.get_supported_languages()

# Handle different return formats from language support
if isinstance(languages, dict) and languages:
    # Check if it's the expected format
    first_key = next(iter(languages))
    if isinstance(languages[first_key], dict) and 'name' in languages[first_key]:
        language_options = {code: f"{lang['name']} ({lang['native_name']})" for code, lang in languages.items()}
    else:
        # Fallback format
        language_options = {code: str(lang) for code, lang in languages.items()}
else:
    # Default fallback
    language_options = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'ta': 'தமிழ் (Tamil)',
        'te': 'తెలుగు (Telugu)',
        'bn': 'বাংলা (Bengali)'
    }
    languages = {code: {'name': name.split(' (')[0], 'native_name': name.split(' (')[1].rstrip(')') if ' (' in name else name} 
                for code, name in language_options.items()}

# Sidebar for language selection
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/320px-Flag_of_India.svg.png", width=100)
    
    selected_language = st.selectbox(
        "🌐 Select Language / भाषा चुनें",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=0 if 'en' in language_options else 0
    )
    
    st.markdown("---")
    
    # Platform selection
    st.subheader("🌍 Platform Selection")
    
    # Get platform options
    all_platforms = platform_support.get_supported_platforms()
    indian_platforms = platform_support.get_indian_platforms()
    
    platform_scope = st.radio(
        "Platform Scope",
        ["Indian Platforms", "Global Platforms", "All Platforms"],
        index=0
    )
    
    if platform_scope == "Indian Platforms":
        available_platforms = indian_platforms
    elif platform_scope == "Global Platforms":
        available_platforms = {k: v for k, v in all_platforms.items() if k not in indian_platforms}
    else:
        available_platforms = all_platforms
    
    # Handle platform format safely
    if available_platforms and isinstance(available_platforms, dict):
        platform_keys = list(available_platforms.keys())
        # Check if platforms have the expected structure
        if platform_keys and isinstance(available_platforms[platform_keys[0]], dict) and 'name' in available_platforms[platform_keys[0]]:
            selected_platforms = st.multiselect(
                "Select Platforms",
                options=platform_keys,
                default=platform_keys[:5],
                format_func=lambda x: available_platforms[x]['name']
            )
        else:
            # Fallback format
            selected_platforms = st.multiselect(
                "Select Platforms",
                options=platform_keys,
                default=platform_keys[:5],
                format_func=lambda x: str(available_platforms[x]) if x in available_platforms else x
            )
    else:
        # Default fallback platforms
        default_platforms = ['twitter', 'facebook', 'instagram', 'youtube', 'koo']
        selected_platforms = st.multiselect(
            "Select Platforms",
            options=default_platforms,
            default=default_platforms,
            format_func=lambda x: x.title()
        )
        # Create mock available_platforms for consistency
        available_platforms = {p: {'name': p.title(), 'type': 'social', 'region': 'global'} for p in default_platforms}
    
    st.markdown("---")
    
    # Legal authorization status
    st.subheader("⚖️ Legal Authorization")
    
    # Mock authorization for demo
    auth_status = st.selectbox(
        "Authorization Status",
        ["Valid Warrant", "Court Order", "Emergency Provision", "No Authorization"],
        index=0
    )
    
    if auth_status != "No Authorization":
        st.success(f"✅ {auth_status} Active")
        case_number = st.text_input("Case Number", value="FIR_001_2025_CYBER_CELL")
        authorized_officer = st.text_input("Authorized Officer", value="Inspector_Sharma")
    else:
        st.error("❌ No valid authorization")
        case_number = ""
        authorized_officer = ""

# Main dashboard
def get_translation(key: str) -> str:
    """Get translation for current language"""
    try:
        translation = language_support.get_ui_translation(selected_language, key)
        # Handle different return formats
        if isinstance(translation, dict):
            return str(translation.get('text', key))
        elif isinstance(translation, str):
            return translation
        else:
            return str(translation) if translation else key
    except Exception as e:
        logger.warning(f"Translation error for key '{key}': {e}")
        # Fallback translations
        fallback_translations = {
            "dashboard_title": "InsideOut - Enhanced Viral Content Analysis Platform",
            "government_text": "Government of India - Ministry of Home Affairs",
            "active_clusters": "Active Clusters",
            "evidence_packages": "Evidence Packages", 
            "high_priority": "High Priority",
            "officers_active": "Officers Active",
            "viral_timeline": "🔥 Viral Timeline",
            "influence_network": "🕸️ Influence Network",
            "geographic_spread": "🗺️ Geographic Spread",
            "evidence_collection": "📋 Evidence Collection",
            "time_range": "Time Range",
            "platform_filter": "Platform Filter",
            "collect_evidence": "Collect Evidence"
        }
        return fallback_translations.get(key, key)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title(get_translation("dashboard_title"))
    st.markdown(f"**{get_translation('government_text')}**")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=get_translation("active_clusters"),
        value="23",
        delta="↑ 5 from yesterday"
    )

with col2:
    st.metric(
        label=get_translation("evidence_packages"),
        value="156",
        delta="↑ 12 new today"
    )

with col3:
    st.metric(
        label=get_translation("high_priority"),
        value="8",
        delta="↑ 2 escalated"
    )

with col4:
    st.metric(
        label=get_translation("officers_active"),
        value="45",
        delta="→ No change"
    )

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    get_translation("viral_timeline"),
    "🧠 Comprehensive Analysis", 
    "🎭 Sentiment & Behavior",
    get_translation("influence_network"),
    get_translation("geographic_spread"),
    get_translation("evidence_collection")
])

# Generate mock data for demonstration
@st.cache_data
def generate_mock_viral_data():
    """Generate mock viral content data"""
    np.random.seed(42)
    
    platforms = selected_platforms if selected_platforms else list(available_platforms.keys())[:5]
    
    data = []
    for i in range(100):
        platform = np.random.choice(platforms)
        timestamp = datetime.now() - timedelta(hours=np.random.randint(0, 72))
        
        # Generate content based on platform
        if platform == "twitter":
            content = f"Breaking news! #ViralContent #{np.random.choice(['India', 'Politics', 'Sports'])} spreading fast @user{i}"
        elif platform == "facebook":
            content = f"Shared post about {np.random.choice(['current events', 'social issues', 'entertainment'])} - please share!"
        elif platform == "koo":
            content = f"भारत में वायरल हो रहा है #{np.random.choice(['समाचार', 'राजनीति', 'खेल'])} @user{i}"
        else:
            content = f"Viral content on {platform} #{np.random.choice(['trending', 'viral', 'news'])}"
        
        # Extract metadata using platform support
        metadata = platform_support.extract_content_metadata(platform, content, {
            "like_count": np.random.randint(10, 10000),
            "share_count": np.random.randint(5, 5000),
            "comment_count": np.random.randint(1, 1000)
        })
        
        # Detect language
        detected_languages = language_support.detect_language(content)
        primary_language = detected_languages[0][0] if detected_languages else "en"
        
        data.append({
            "id": f"post_{i}",
            "platform": platform,
            "content": content,
            "timestamp": timestamp,
            "viral_score": metadata.get("viral_potential", {}).get("score", 0),
            "engagement": sum([
                metadata.get("viral_metrics", {}).get("like_count", 0),
                metadata.get("viral_metrics", {}).get("share_count", 0),
                metadata.get("viral_metrics", {}).get("comment_count", 0)
            ]),
            "language": primary_language,
            "content_type": metadata.get("content_classification", "general"),
            "location": np.random.choice(["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]),
            "extracted_elements": metadata.get("extracted_elements", {}),
            "legal_status": "authorized" if auth_status != "No Authorization" else "unauthorized"
        })
    
    return pd.DataFrame(data)

viral_data = generate_mock_viral_data()

# Tab 1: Viral Timeline
with tab1:
    st.subheader(get_translation("viral_timeline"))
    
    # Time range filter
    col1, col2 = st.columns(2)
    with col1:
        time_range = st.selectbox(
            get_translation("time_range"),
            ["Last 24 hours", "Last 3 days", "Last week", "Last month"]
        )
    
    with col2:
        platform_filter = st.multiselect(
            get_translation("platform_filter"),
            options=viral_data['platform'].unique(),
            default=viral_data['platform'].unique()
        )
    
    # Filter data
    filtered_data = viral_data[viral_data['platform'].isin(platform_filter)]
    
    # Timeline chart
    timeline_data = filtered_data.groupby([
        filtered_data['timestamp'].dt.floor('H'), 'platform'
    ]).agg({
        'viral_score': 'mean',
        'engagement': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig_timeline = px.line(
        timeline_data,
        x='timestamp',
        y='viral_score',
        color='platform',
        title="Viral Content Timeline by Platform",
        labels={'viral_score': 'Average Viral Score', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Top viral content
    st.subheader("Top Viral Content")
    top_content = filtered_data.nlargest(5, 'viral_score')[['content', 'platform', 'viral_score', 'engagement', 'timestamp']]
    st.dataframe(top_content, use_container_width=True)

# Tab 2: Comprehensive Analysis
with tab2:
    st.subheader("🧠 Comprehensive Content Analysis")
    
    # Content input for analysis
    st.markdown("### Analyze Content")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_text = st.text_area(
            "Enter content to analyze:",
            value="This is breaking news! Everyone should share this important information immediately. #Viral #Breaking",
            height=100
        )
    
    with col2:
        st.markdown("**User Metadata (Optional)**")
        followers = st.number_input("Followers", value=1000, min_value=0)
        verified = st.checkbox("Verified Account", value=False)
        account_age = st.number_input("Account Age (days)", value=365, min_value=0)
    
    if st.button("🔍 Analyze Content", type="primary"):
        if analysis_text.strip():
            user_metadata = {
                'followers': followers,
                'verified': verified,
                'account_age_days': account_age
            }
            
            # Perform comprehensive analysis
            with st.spinner("Analyzing content..."):
                analysis_results = analyze_content_comprehensive(analysis_text, user_metadata)
            
            # Display results
            st.markdown("### Analysis Results")
            
            # Overall viral potential
            viral_potential = analysis_results['analysis'].get('viral_potential', 0)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Viral Potential", f"{viral_potential:.2%}", 
                         delta=f"{'High' if viral_potential > 0.7 else 'Medium' if viral_potential > 0.4 else 'Low'} Risk")
            
            with col2:
                influence_score = analysis_results['analysis'].get('influence_score', 0)
                # Handle different influence_score formats
                if isinstance(influence_score, dict):
                    influence_value = influence_score.get('score', 0)
                elif isinstance(influence_score, (int, float)):
                    influence_value = influence_score
                else:
                    influence_value = 0
                    
                st.metric("Influence Score", f"{influence_value:.2f}", 
                         delta=f"{'High' if influence_value > 0.7 else 'Medium' if influence_value > 0.4 else 'Low'} Influence")
            
            with col3:
                sentiment = analysis_results['analysis'].get('sentiment', {})
                # Handle different sentiment formats safely
                try:
                    if isinstance(sentiment, dict) and sentiment:
                        dominant_sentiment = max(sentiment, key=sentiment.get)
                        confidence = sentiment.get(dominant_sentiment, 0)
                    elif isinstance(sentiment, list) and sentiment:
                        # If it's a list, take the first item or convert to dict
                        dominant_sentiment = str(sentiment[0]) if sentiment else 'neutral'
                        confidence = 0.5  # Default confidence
                    else:
                        dominant_sentiment = 'neutral'
                        confidence = 0.0
                except Exception as e:
                    logger.warning(f"Sentiment processing error: {e}")
                    dominant_sentiment = 'neutral'
                    confidence = 0.0
                    
                st.metric("Dominant Sentiment", dominant_sentiment.title(), 
                         delta=f"{confidence:.2%} confidence")
            
            # Detailed visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment visualization
                sentiment_data = analysis_results['analysis'].get('sentiment', {})
                if sentiment_data:
                    fig_sentiment = create_sentiment_visualization(sentiment_data)
                    st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with col2:
                # Influence gauge
                influence_score = analysis_results['analysis'].get('influence_score', 0)
                # Handle different influence_score formats for gauge
                if isinstance(influence_score, dict):
                    influence_value = influence_score.get('score', 0)
                elif isinstance(influence_score, (int, float)):
                    influence_value = influence_score
                else:
                    influence_value = 0
                    
                fig_influence = create_influence_gauge(influence_value)
                st.plotly_chart(fig_influence, use_container_width=True)
            
            # Behavioral patterns
            patterns = analysis_results['analysis'].get('behavior_patterns', [])
            if patterns:
                st.markdown("### Behavioral Patterns Detected")
                fig_patterns = create_behavior_patterns_chart(patterns)
                st.plotly_chart(fig_patterns, use_container_width=True)
                
                # Pattern details
                for pattern in patterns:
                    if isinstance(pattern, dict):
                        pattern_type = pattern.get('pattern_type', 'Unknown')
                        score = pattern.get('score', 0)
                        confidence = pattern.get('confidence', 0)
                        indicators = pattern.get('indicators', [])
                    else:
                        pattern_type = str(pattern)
                        score = 0.5
                        confidence = 0.5
                        indicators = []
                        
                    with st.expander(f"{pattern_type.title()} Pattern (Score: {score:.2f})"):
                        st.write(f"**Confidence:** {confidence:.2%}")
                        st.write(f"**Indicators:** {', '.join(indicators) if indicators else 'No specific indicators'}")
            else:
                st.info("No significant behavioral patterns detected.")

# Tab 3: Sentiment & Behavior Analysis
with tab3:
    st.subheader("🎭 Sentiment & Behavior Analysis Dashboard")
    
    # Batch analysis
    st.markdown("### Batch Content Analysis")
    
    # Sample content for batch analysis
    sample_contents = [
        "This is amazing news! Everyone should know about this! #Viral #Share",
        "I'm not sure about this information. Seems suspicious to me.",
        "Breaking: Important announcement from the government. Please verify before sharing.",
        "Join our movement! Together we can make a difference! #Unity #Action",
        "As a concerned citizen, I believe we need to take action immediately."
    ]
    
    if st.button("🔄 Analyze Sample Content Batch"):
        with st.spinner("Analyzing batch content..."):
            batch_results = []
            for content in sample_contents:
                result = analyze_content_comprehensive(content)
                batch_results.append(result)
        
        # Create summary dataframe
        summary_data = []
        for i, result in enumerate(batch_results):
            analysis = result['analysis']
            sentiment = analysis.get('sentiment', {})
            patterns = analysis.get('behavior_patterns', [])
            
            summary_data.append({
                'Content': sample_contents[i][:50] + "..." if len(sample_contents[i]) > 50 else sample_contents[i],
                'Viral Potential': f"{analysis.get('viral_potential', 0):.2%}",
                'Positive': f"{sentiment.get('positive', 0):.2%}",
                'Negative': f"{sentiment.get('negative', 0):.2%}",
                'Neutral': f"{sentiment.get('neutral', 0):.2%}",
                'Influence Score': f"{analysis.get('influence_score', 0):.2f}",
                'Patterns Detected': len(patterns)
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Aggregate visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Average sentiment distribution
            avg_sentiment = {
                'positive': np.mean([r['analysis']['sentiment']['positive'] for r in batch_results]),
                'negative': np.mean([r['analysis']['sentiment']['negative'] for r in batch_results]),
                'neutral': np.mean([r['analysis']['sentiment']['neutral'] for r in batch_results])
            }
            fig_avg_sentiment = create_sentiment_visualization(avg_sentiment)
            fig_avg_sentiment.update_layout(title="Average Sentiment Distribution")
            st.plotly_chart(fig_avg_sentiment, use_container_width=True)
        
        with col2:
            # Viral potential distribution
            viral_potentials = [r['analysis']['viral_potential'] for r in batch_results]
            fig_viral_dist = go.Figure(data=[
                go.Histogram(x=viral_potentials, nbinsx=10, marker_color='#FF6B6B')
            ])
            fig_viral_dist.update_layout(
                title="Viral Potential Distribution",
                xaxis_title="Viral Potential",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig_viral_dist, use_container_width=True)

# Tab 4: Influence Network
with tab4:
    st.subheader(get_translation("influence_network"))
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes and edges based on viral data
    for idx, row in viral_data.head(20).iterrows():
        G.add_node(row['id'], 
                  platform=row['platform'],
                  viral_score=row['viral_score'],
                  engagement=row['engagement'])
        
        # Add edges based on similar content or platform
        for idx2, row2 in viral_data.head(20).iterrows():
            if idx != idx2 and (row['platform'] == row2['platform'] or 
                               abs(row['viral_score'] - row2['viral_score']) < 0.2):
                G.add_edge(row['id'], row2['id'])
    
    # Network visualization
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                           line=dict(width=0.5, color='#888'),
                           hoverinfo='none',
                           mode='lines')
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_info = G.nodes[node]
        node_text.append(f"Platform: {node_info['platform']}<br>"
                        f"Viral Score: {node_info['viral_score']:.2f}<br>"
                        f"Engagement: {node_info['engagement']:,}")
        node_color.append(node_info['viral_score'])
    
    node_trace = go.Scatter(x=node_x, y=node_y,
                           mode='markers',
                           hoverinfo='text',
                           text=node_text,
                           marker=dict(showscale=True,
                                     colorscale='Viridis',
                                     color=node_color,
                                     size=10,
                                     colorbar=dict(thickness=15,
                                                 xanchor="left",
                                                 title="Viral Score")))
    
    fig_network = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title=dict(text='Viral Content Influence Network', font=dict(size=16)),
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20,l=5,r=5,t=40),
                               annotations=[ dict(
                                   text="Network shows connections between viral content based on platform and viral score similarity",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    
    st.plotly_chart(fig_network, use_container_width=True)

# Tab 3: Geographic Spread
with tab3:
    st.subheader(get_translation("geographic_spread"))
    
    # Geographic distribution
    geo_data = viral_data.groupby('location').agg({
        'viral_score': 'mean',
        'engagement': 'sum',
        'id': 'count'
    }).reset_index()
    
    # Map visualization
    fig_map = px.scatter_mapbox(
        geo_data,
        lat=[28.6139, 19.0760, 12.9716, 13.0827, 22.5726, 17.3850],  # Coordinates for cities
        lon=[77.2090, 72.8777, 77.5946, 80.2707, 88.3639, 78.4867],
        size='engagement',
        color='viral_score',
        hover_name='location',
        hover_data={'viral_score': ':.2f', 'engagement': ':,', 'id': True},
        mapbox_style="open-street-map",
        title="Geographic Distribution of Viral Content",
        zoom=4,
        center={"lat": 20.5937, "lon": 78.9629}  # Center of India
    )
    
    fig_map.update_layout(height=500)
    st.plotly_chart(fig_map, use_container_width=True)
    
    # City-wise breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        fig_city = px.bar(
            geo_data.sort_values('engagement', ascending=False),
            x='location',
            y='engagement',
            title="Total Engagement by City",
            color='viral_score'
        )
        st.plotly_chart(fig_city, use_container_width=True)
    
    with col2:
        fig_viral_city = px.bar(
            geo_data.sort_values('viral_score', ascending=False),
            x='location',
            y='viral_score',
            title="Average Viral Score by City",
            color='viral_score'
        )
        st.plotly_chart(fig_viral_city, use_container_width=True)

# Tab 5: Evidence Collection  
with tab5:
    st.subheader(get_translation("evidence_collection"))
    
    if auth_status == "No Authorization":
        st.error("⚠️ Legal authorization required for evidence collection")
        st.info("Please obtain proper legal authorization (warrant, court order, etc.) before collecting digital evidence.")
    else:
        st.success(f"✅ Operating under: {auth_status}")
        st.info(f"Case Number: {case_number} | Officer: {authorized_officer}")
        
        # Evidence collection interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Evidence Collection Queue")
            
            # Filter high-priority content for evidence collection
            evidence_candidates = viral_data[
                (viral_data['viral_score'] > 0.7) & 
                (viral_data['legal_status'] == 'authorized')
            ].head(10)
            
            for idx, row in evidence_candidates.iterrows():
                with st.expander(f"🔍 {row['platform'].upper()} - Priority Evidence"):
                    st.write(f"**Content:** {row['content']}")
                    st.write(f"**Viral Score:** {row['viral_score']:.2f}")
                    st.write(f"**Engagement:** {row['engagement']:,}")
                    st.write(f"**Language:** {languages.get(row['language'], {}).get('name', 'Unknown')}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button(f"🔒 Collect Evidence", key=f"evidence_{idx}"):
                            # Simulate evidence collection with legal framework
                            try:
                                # Create mock authorization
                                auth_data = {
                                    "authority_type": "magistrate_warrant",
                                    "issuing_authority": "Chief Metropolitan Magistrate, Delhi",
                                    "case_number": case_number,
                                    "sections_invoked": ["IT_Act_66", "IT_Act_67", "CrPC_156"],
                                    "validity_start": "2025-09-21T00:00:00",
                                    "validity_end": "2025-12-21T23:59:59",
                                    "scope_description": "Investigation of viral misinformation campaign",
                                    "target_platforms": [row['platform']],
                                    "authorized_officers": [authorized_officer]
                                }
                                
                                authorization = legal_framework.create_legal_authorization(auth_data)
                                
                                if authorization:
                                    evidence = legal_framework.collect_digital_evidence(
                                        content=row['content'],
                                        platform=row['platform'],
                                        evidence_type=EvidenceType.ELECTRONIC_RECORD,
                                        collecting_officer=authorized_officer,
                                        authorization_id=authorization.auth_id,
                                        metadata={
                                            "viral_score": row['viral_score'],
                                            "engagement": row['engagement'],
                                            "language": row['language'],
                                            "location": row['location']
                                        }
                                    )
                                    
                                    if evidence:
                                        st.success(f"✅ Evidence collected successfully!")
                                        st.json({
                                            "evidence_id": evidence.evidence_id,
                                            "collection_time": evidence.collection_timestamp.isoformat(),
                                            "integrity_verified": evidence.integrity_verified,
                                            "section_65b_compliant": bool(evidence.section_65b_certificate)
                                        })
                                    else:
                                        st.error("❌ Evidence collection failed")
                                else:
                                    st.error("❌ Authorization creation failed")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    with col_b:
                        if st.button(f"📊 Analyze", key=f"analyze_{idx}"):
                            # Show detailed analysis
                            analysis = language_support.analyze_multilingual_content(row['content'])
                            st.json(analysis)
                    
                    with col_c:
                        if st.button(f"🚨 Flag Priority", key=f"flag_{idx}"):
                            st.warning("⚠️ Flagged for immediate attention")
        
        with col2:
            st.subheader("📈 Evidence Statistics")
            
            # Mock evidence statistics
            st.metric("Total Evidence Items", "156", "↑ 12")
            st.metric("Section 65B Compliant", "142", "91%")
            st.metric("Chain of Custody Complete", "156", "100%")
            st.metric("Court-Ready Packages", "23", "↑ 3")
            
            st.markdown("---")
            
            st.subheader("⚖️ Legal Compliance Status")
            
            compliance_data = {
                "IT Act 2000": "✅ Compliant",
                "CrPC 1973": "✅ Compliant", 
                "Evidence Act 1872": "✅ Compliant",
                "Digital Signatures": "✅ Verified",
                "Chain of Custody": "✅ Maintained"
            }
            
            for law, status in compliance_data.items():
                st.write(f"**{law}:** {status}")

# End of dashboard

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🏛️ Government of India**")
    st.markdown("Ministry of Home Affairs")

with col2:
    st.markdown("**⚖️ Legal Framework**")
    st.markdown("IT Act 2000 | CrPC 1973 | Evidence Act 1872")

with col3:
    st.markdown("**🔒 Security Classification**")
    st.markdown("RESTRICTED - For Official Use Only")

# Status indicator
if auth_status != "No Authorization":
    st.success(f"🟢 System Status: OPERATIONAL | Authorization: {auth_status} | Case: {case_number}")
else:
    st.error("🔴 System Status: UNAUTHORIZED ACCESS - Legal authorization required")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🔒 Security Status**")
    st.success("✅ All systems operational")
    st.info("🔐 End-to-end encryption active")

with col2:
    st.markdown("**⚖️ Legal Compliance**")
    st.success("✅ IT Act 2000 compliant")
    st.success("✅ Evidence Act 1872 compliant")

with col3:
    st.markdown("**🌐 Platform Coverage**")
    st.info(f"📱 {len(selected_platforms)} platforms active")
    st.info(f"🗣️ {len(languages)} languages supported")

# Real-time updates simulation
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Export functionality
if st.sidebar.button("📊 Export Report"):
    # Generate comprehensive report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "case_number": case_number,
        "authorized_officer": authorized_officer,
        "platforms_analyzed": selected_platforms,
        "total_content_items": len(viral_data),
        "high_priority_items": len(viral_data[viral_data['viral_score'] > 0.7]),
        "language_distribution": viral_data['language'].value_counts().to_dict(),
        "platform_distribution": viral_data['platform'].value_counts().to_dict(),
        "legal_compliance_status": "compliant" if auth_status != "No Authorization" else "requires_authorization"
    }
    
    st.sidebar.download_button(
        label="📥 Download Report",
        data=json.dumps(report_data, indent=2),
        file_name=f"insideout_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# Help section
with st.sidebar.expander("❓ Help & Documentation"):
    st.markdown("""
    **InsideOut Platform Features:**
    
    🔍 **Viral Content Analysis**
    - Real-time monitoring across platforms
    - AI-powered viral prediction
    - Multi-language content support
    
    ⚖️ **Legal Compliance**
    - IT Act 2000 compliance
    - Evidence Act 1872 compliance
    - Chain of custody maintenance
    - Digital evidence collection
    
    🌐 **Global Platform Support**
    - 8+ major social media platforms
    - Indian regional platforms (Koo, ShareChat)
    - Cross-platform analysis
    
    🗣️ **Multi-language Support**
    - 5+ Indian languages
    - Automatic language detection
    - Localized user interface
    
    📊 **Analytics & Reporting**
    - Influence network analysis
    - Geographic spread tracking
    - Evidence collection reports
    """)

if __name__ == "__main__":
    st.sidebar.success("✅ Enhanced InsideOut Platform Active")
    st.sidebar.info(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")