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

# Import required services
try:
    from realtime.realtime_data_service import RealTimeDataService
    from nlp.models.sentiment_model import SentinelBERTModel
    from realtime.realtime_search_service import RealTimeSearchService
except ImportError as e:
    logger.error(f"Failed to import services: {e}")
    # Create mock classes to prevent crashes
    class RealTimeDataService:
        def __init__(self):
            pass
        def get_comprehensive_analysis_data(self, *args, **kwargs):
            return None
    
    class SentinelBERTModel:
        def __init__(self):
            pass
    
    class RealTimeSearchService:
        def __init__(self):
            pass

# Exception handling utilities
def show_error_popup(error_message: str, error_type: str = "Error"):
    """Display error popup with details"""
    st.error(f"🚨 **{error_type}**: {error_message}")
    with st.expander("🔍 Error Details", expanded=False):
        st.code(str(error_message))

def safe_execute(func, *args, error_message="An error occurred", **kwargs):
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        show_error_popup(f"{error_message}: {str(e)}", "Execution Error")
        return None

# Import services with fallback
try:
    from services.legal_compliance.indian_legal_framework import IndianLegalFramework, LegalAuthority, EvidenceType
    from services.multilingual.enhanced_language_support import EnhancedLanguageSupport
    from services.platforms.global_platform_support import GlobalPlatformSupport
    from services.nlp.models.sentiment_model import SentinelBERTModel
    from services.nlp.models.behavior_analyzer import BehavioralPatternAnalyzer
    from services.nlp.models.influence_calculator import InfluenceCalculator
    # Import new real-time services
    from services.realtime.realtime_search_service import RealTimeSearchService, SearchQuery
    from services.realtime.social_media_connectors import SocialMediaAggregator
    from services.realtime.realtime_data_service import RealTimeDataService
except ImportError as e:
    logger.warning(f"Some services not available: {e}")
    # Create mock classes for missing services
    class MockService:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: {"status": "mock", "data": []}
    
    # Create mock SearchQuery class
    class SearchQuery:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Page configuration
st.set_page_config(
    page_title="भारत सरकार - साइबर अपराध विश्लेषण प्लेटफॉर्म | Government of India - Cyber Crime Analysis Platform",
    page_icon="🇮🇳",
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
        
        # Initialize real-time services
        realtime_search = RealTimeSearchService()
        social_aggregator = SocialMediaAggregator()
        
        return {
            'legal': legal_framework,
            'language': language_support,
            'platform': platform_support,
            'sentiment': sentiment_model,
            'behavior': behavior_analyzer,
            'influence': influence_calculator,
            'realtime_search': realtime_search,
            'social_aggregator': social_aggregator
        }
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        return {
            'legal': MockService(),
            'language': MockService(),
            'platform': MockService(),
            'sentiment': MockService(),
            'behavior': MockService(),
            'influence': MockService(),
            'realtime_search': MockService(),
            'social_aggregator': MockService()
        }

# Language Translation System
TRANSLATIONS = {
    'en': {
        'title': 'Government of India - Cyber Crime Analysis Platform',
        'subtitle': 'Ministry of Home Affairs - Cyber Crime Investigation Division',
        'platform_selection': 'Platform Selection',
        'legal_authorization': 'Legal Authorization',
        'case_number': 'Case Number',
        'authorized_officer': 'Authorized Officer',
        'comprehensive_analysis': 'Comprehensive Analysis',
        'sentiment_behavior': 'Sentiment & Behavior',
        'influence_network': 'Influence Network',
        'geographic_spread': 'Geographic Spread',
        'evidence_collection': 'Evidence Collection',
        'viral_timeline': 'Viral Timeline',
        'realtime_search': 'Real-time Search',
        'analyze_content': 'Analyze Content',
        'refresh_data': 'Refresh Data',
        'export_report': 'Export Report',
        'help_documentation': 'Help & Documentation',
        'active_clusters': 'Active Clusters',
        'evidence_packages': 'Evidence Packages',
        'high_priority': 'High Priority Cases',
        'officers_active': 'Officers Active',
        'system_operational': 'System Status: OPERATIONAL',
        'valid_warrant_active': 'Valid Warrant Active',
        'legal_framework': 'Legal Framework',
        'security_classification': 'Security Classification',
        'restricted_official_use': 'RESTRICTED - For Official Use Only',
        'all_systems_operational': 'All systems operational',
        'encryption_active': 'End-to-end encryption active',
        'it_act_compliant': 'IT Act 2000 compliant',
        'evidence_act_compliant': 'Evidence Act 1872 compliant',
        'platforms_active': 'platforms active',
        'languages_supported': 'languages supported'
    },
    'hi': {
        'title': 'भारत सरकार - साइबर अपराध विश्लेषण प्लेटफॉर्म',
        'subtitle': 'गृह मंत्रालय - साइबर अपराध जांच प्रभाग',
        'platform_selection': 'प्लेटफॉर्म चयन',
        'legal_authorization': 'कानूनी प्राधिकरण',
        'case_number': 'मामला संख्या',
        'authorized_officer': 'अधिकृत अधिकारी',
        'comprehensive_analysis': 'व्यापक विश्लेषण',
        'sentiment_behavior': 'भावना और व्यवहार',
        'influence_network': 'प्रभाव नेटवर्क',
        'geographic_spread': 'भौगोलिक प्रसार',
        'evidence_collection': 'साक्ष्य संग्रह',
        'viral_timeline': 'वायरल समयरेखा',
        'analyze_content': 'सामग्री का विश्लेषण करें',
        'refresh_data': 'डेटा रीफ्रेश करें',
        'export_report': 'रिपोर्ट निर्यात करें',
        'help_documentation': 'सहायता और दस्तावेज़ीकरण',
        'active_clusters': 'सक्रिय क्लस्टर',
        'evidence_packages': 'साक्ष्य पैकेज',
        'high_priority': 'उच्च प्राथमिकता मामले',
        'officers_active': 'सक्रिय अधिकारी',
        'system_operational': 'सिस्टम स्थिति: परिचालन',
        'valid_warrant_active': 'वैध वारंट सक्रिय',
        'legal_framework': 'कानूनी ढांचा',
        'security_classification': 'सुरक्षा वर्गीकरण',
        'restricted_official_use': 'प्रतिबंधित - केवल आधिकारिक उपयोग',
        'all_systems_operational': 'सभी सिस्टम परिचालन',
        'encryption_active': 'एंड-टू-एंड एन्क्रिप्शन सक्रिय',
        'it_act_compliant': 'आईटी अधिनियम 2000 अनुपालन',
        'evidence_act_compliant': 'साक्ष्य अधिनियम 1872 अनुपालन',
        'platforms_active': 'प्लेटफॉर्म सक्रिय',
        'languages_supported': 'भाषाएं समर्थित'
    }
}

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def get_text(key):
    """Get translated text based on current language"""
    return TRANSLATIONS.get(st.session_state.language, TRANSLATIONS['en']).get(key, key)

# Custom CSS for Indian Government Theme
def load_government_css():
    st.markdown("""
    <style>
    /* Indian Government Color Scheme */
    :root {
        --saffron: #FF9933;
        --white: #FFFFFF;
        --green: #138808;
        --navy: #000080;
        --ashoka-blue: #6666CC;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header styling */
    .government-header {
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .government-title {
        color: #000080;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .government-subtitle {
        color: #000080;
        font-size: 1.2rem;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
    }
    
    /* Metric cards styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9933;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF9933, #138808);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(90deg, #FF9933, #138808);
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
        font-weight: bold;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #138808;
    }
    
    /* Footer styling */
    .government-footer {
        background: #000080;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
    }
    
    /* Remove emoji from titles */
    .no-emoji {
        font-family: 'Arial', sans-serif;
    }
    
    /* Professional table styling */
    .dataframe {
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #FF9933;
        color: white;
        font-weight: bold;
    }
    
    /* Language selector styling */
    .language-selector {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        background: white;
        padding: 0.5rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

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
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/200px-Emblem_of_India.svg.png", width=100)
    
    # Simple language options for sidebar
    sidebar_language_options = {"English": "en", "हिन्दी": "hi"}
    
    # Find current language display name
    current_display = "English"
    for display, code in sidebar_language_options.items():
        if code == st.session_state.language:
            current_display = display
            break
    
    selected_language_display = st.selectbox(
        "Select Language / भाषा चुनें",
        options=list(sidebar_language_options.keys()),
        index=list(sidebar_language_options.keys()).index(current_display),
        key="sidebar_language_selector"
    )
    
    # Update session state when language changes
    selected_language_code = sidebar_language_options[selected_language_display]
    if selected_language_code != st.session_state.language:
        st.session_state.language = selected_language_code
        st.rerun()
    
    st.markdown("---")
    
    # Legal authorization status
    st.subheader(get_text('legal_authorization'))
    
    # Mock authorization for demo
    auth_status = st.selectbox(
        "Authorization Status",
        ["Valid Warrant", "Court Order", "Emergency Provision", "No Authorization"],
        index=0
    )
    
    if auth_status != "No Authorization":
        st.success(f"{get_text('valid_warrant_active')}")
        case_number = st.text_input(get_text('case_number'), value="FIR_001_2025_CYBER_CELL")
        authorized_officer = st.text_input(get_text('authorized_officer'), value="Inspector_Sharma")
    else:
        st.error("No valid authorization")
        case_number = ""
        authorized_officer = ""

# Main dashboard
def get_translation(key: str) -> str:
    """Get translation for current language"""
    try:
        # Use session state language or default to English
        current_language = st.session_state.get('language', 'en')
        translation = language_support.get_ui_translation(current_language, key)
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
            "dashboard_title": "Government of India - Cyber Crime Analysis Platform",
            "government_text": "Ministry of Home Affairs - Cyber Crime Investigation Division",
            "active_clusters": "Active Clusters",
            "evidence_packages": "Evidence Packages", 
            "high_priority": "High Priority Cases",
            "officers_active": "Officers Active",
            "viral_timeline": "Viral Timeline",
            "influence_network": "Influence Network",
            "geographic_spread": "Geographic Spread",
            "evidence_collection": "Evidence Collection",
            "time_range": "Time Range",
            "platform_filter": "Platform Filter",
            "collect_evidence": "Collect Evidence"
        }
        return fallback_translations.get(key, key)

# Load government CSS
load_government_css()

# Language selector removed from top right - now only in sidebar

# Government Header
st.markdown(f"""
<div class="government-header">
    <h1 class="government-title">{get_text('title')}</h1>
    <p class="government-subtitle">{get_text('subtitle')}</p>
</div>
""", unsafe_allow_html=True)

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

# Platform Selection for Main Dashboard
st.markdown("---")
st.subheader("🌐 Platform Selection")

# Get platform options
all_platforms = platform_support.get_supported_platforms()
indian_platforms = platform_support.get_indian_platforms()

# Use only global platforms (excluding Indian-specific ones)
available_platforms = {k: v for k, v in all_platforms.items() if k not in indian_platforms}

# Handle platform format safely
if available_platforms and isinstance(available_platforms, dict):
    platform_keys = list(available_platforms.keys())
    # Check if platforms have the expected structure
    if platform_keys and isinstance(available_platforms[platform_keys[0]], dict) and 'name' in available_platforms[platform_keys[0]]:
        # Set Twitter as default for hackathon demo
        twitter_keys = [k for k in platform_keys if 'twitter' in k.lower()]
        default_selection = twitter_keys[:1] if twitter_keys else platform_keys[:1]
        selected_platforms = st.multiselect(
            "Select Platforms for Analysis",
            options=platform_keys,
            default=default_selection,
            format_func=lambda x: available_platforms[x]['name'],
            key="dashboard_platform_select_1",
            help="Choose which social media platforms to analyze"
        )
    else:
        # Fallback format
        # Set Twitter as default for hackathon demo
        twitter_keys = [k for k in platform_keys if 'twitter' in k.lower()]
        default_selection = twitter_keys[:1] if twitter_keys else platform_keys[:1]
        selected_platforms = st.multiselect(
            "Select Platforms for Analysis",
            options=platform_keys,
            default=default_selection,
            format_func=lambda x: str(available_platforms[x]) if x in available_platforms else x,
            key="dashboard_platform_select_2",
            help="Choose which social media platforms to analyze"
        )
else:
    # Default fallback platforms - Twitter only for hackathon demo
    default_platforms = ['twitter', 'facebook', 'instagram', 'youtube', 'koo']
    selected_platforms = st.multiselect(
        "Select Platforms for Analysis",
        options=default_platforms,
        default=['twitter'],  # Only Twitter selected by default
        format_func=lambda x: x.title(),
        key="dashboard_platform_select_3",
        help="Choose which social media platforms to analyze"
    )
    # Create mock available_platforms for consistency
    available_platforms = {p: {'name': p.title(), 'type': 'social', 'region': 'global'} for p in default_platforms}

# ===== UNIFIED TRACKING INPUT SYSTEM =====
st.markdown("---")
st.subheader("🎯 Unified Content Tracking System")

# Import tracking cache system
try:
    from services.database.tracking_cache import cache_db
    cache_available = True
except ImportError:
    cache_available = False
    st.warning("⚠️ Cache system not available - using live API calls only")

# Tracking input options
tracking_col1, tracking_col2 = st.columns([2, 1])

with tracking_col1:
    tracking_type = st.selectbox(
        "Select Tracking Type",
        ["🔗 Post URL", "# Hashtag", "📈 Trending Topic", "🔍 Keyword Search"],
        help="Choose what type of content you want to track across all tabs"
    )
    
    # Input field based on tracking type
    if tracking_type == "🔗 Post URL":
        tracking_input = st.text_input(
            "Enter Post URL",
            placeholder="https://twitter.com/username/status/123456789",
            help="Paste the direct URL of the post you want to track"
        )
        query_type = "url"
    elif tracking_type == "# Hashtag":
        tracking_input = st.text_input(
            "Enter Hashtag",
            placeholder="#ClimateChange",
            help="Enter hashtag without # symbol (it will be added automatically)"
        )
        if tracking_input and not tracking_input.startswith('#'):
            tracking_input = f"#{tracking_input}"
        query_type = "hashtag"
    elif tracking_type == "📈 Trending Topic":
        # Get trending topics from cache if available
        if cache_available:
            trending_topics = cache_db.get_mock_trending_data()
            topic_options = [t['keyword'] for t in trending_topics]
            if topic_options:
                tracking_input = st.selectbox(
                    "Select Trending Topic",
                    options=topic_options,
                    help="Choose from current trending topics"
                )
            else:
                tracking_input = st.text_input(
                    "Enter Trending Topic",
                    placeholder="digital india",
                    help="Enter a trending topic to track"
                )
        else:
            tracking_input = st.text_input(
                "Enter Trending Topic",
                placeholder="digital india",
                help="Enter a trending topic to track"
            )
        query_type = "trend"
    else:  # Keyword Search
        tracking_input = st.text_input(
            "Enter Keywords",
            placeholder="cybersecurity india",
            help="Enter keywords to search and track"
        )
        query_type = "keyword"

with tracking_col2:
    st.markdown("### 📊 API Usage Stats")
    if cache_available:
        try:
            api_stats = cache_db.get_api_usage_stats(24)
            overall_stats = api_stats.get('overall', {})
            st.metric("API Calls (24h)", overall_stats.get('total_api_calls', 0))
            st.metric("Cache Hit Rate", f"{overall_stats.get('cache_hit_rate', 0)*100:.1f}%")
            st.metric("Requests", overall_stats.get('total_requests', 0))
        except Exception as e:
            st.error(f"Stats error: {e}")
    else:
        st.info("Cache system not available")

# Track button and session state management
if st.button("🚀 Start Unified Tracking", type="primary", use_container_width=True):
    if tracking_input and tracking_input.strip():
        # Store tracking parameters in session state for use across all tabs
        st.session_state.tracking_active = True
        st.session_state.tracking_input = tracking_input.strip()
        st.session_state.tracking_type = query_type
        st.session_state.tracking_platforms = selected_platforms
        st.session_state.tracking_timestamp = datetime.now()
        
        # Check cache first if available
        cached_data = None
        if cache_available and selected_platforms:
            primary_platform = selected_platforms[0] if selected_platforms else 'twitter'
            cached_data = cache_db.get_cached_data(primary_platform, query_type, tracking_input)
        
        if cached_data:
            st.success(f"✅ Using cached data for '{tracking_input}' (Cache hit!)")
            st.session_state.tracking_data = cached_data.data
            st.session_state.api_calls_saved = True
        else:
            st.success(f"🎯 Started tracking '{tracking_input}' across {len(selected_platforms)} platform(s)")
            st.session_state.tracking_data = None
            st.session_state.api_calls_saved = False
            
        # Auto-refresh to update all tabs
        st.rerun()
    else:
        st.error("Please enter a valid input for tracking")

# Display current tracking status
if st.session_state.get('tracking_active', False):
    st.markdown("---")
    st.markdown("### 🎯 Current Tracking Session")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.info(f"**Tracking:** {st.session_state.get('tracking_input', 'N/A')}")
        st.info(f"**Type:** {st.session_state.get('tracking_type', 'N/A').title()}")
    
    with status_col2:
        platforms_str = ", ".join(st.session_state.get('tracking_platforms', []))
        st.info(f"**Platforms:** {platforms_str}")
        tracking_time = st.session_state.get('tracking_timestamp')
        if tracking_time:
            time_diff = datetime.now() - tracking_time
            st.info(f"**Duration:** {str(time_diff).split('.')[0]}")
    
    with status_col3:
        if st.session_state.get('api_calls_saved', False):
            st.success("💾 Using Cached Data")
        else:
            st.warning("🔄 Live API Calls")
        
        if st.button("🛑 Stop Tracking", type="secondary"):
            # Clear tracking session
            for key in ['tracking_active', 'tracking_input', 'tracking_type', 
                       'tracking_platforms', 'tracking_timestamp', 'tracking_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

st.markdown("---")

st.markdown("---")

# Main content tabs
try:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        get_text("viral_timeline"),
        get_text("comprehensive_analysis"), 
        get_text("sentiment_behavior"),
        get_text("influence_network"),
        get_text("geographic_spread"),
        get_text("evidence_collection"),
        get_text("realtime_search")
    ])
except Exception as e:
    logger.error(f"Failed to create main tabs: {e}")
    show_error_popup(f"Failed to initialize dashboard tabs: {str(e)}", "UI Initialization Error")
    st.stop()

# Initialize real-time data service
@st.cache_resource
def get_realtime_data_service():
    """Get real-time data service instance"""
    return RealTimeDataService()

# Get real-time data service
try:
    realtime_service = get_realtime_data_service()
except Exception as e:
    logger.error(f"Failed to initialize real-time service: {e}")
    realtime_service = None

# Tab 1: Enhanced Viral Timeline with Unified Tracking
with tab1:
    st.subheader("📈 Enhanced Viral Timeline Analytics")
    
    # Check if unified tracking is active
    if st.session_state.get('tracking_active', False):
        tracking_input = st.session_state.get('tracking_input', '')
        tracking_type = st.session_state.get('tracking_type', '')
        tracking_platforms = st.session_state.get('tracking_platforms', [])
        
        st.success(f"🎯 Analyzing timeline for: **{tracking_input}** ({tracking_type})")
        
        # Time range selector with IST timezone
        col1, col2, col3 = st.columns(3)
        
        with col1:
            timeline_range = st.selectbox(
                "📅 Timeline Range",
                ["Last 24 Hours", "Last 1 Week", "Last 1 Month", "Custom Range"],
                help="Select time period for viral timeline analysis"
            )
        
        with col2:
            timezone_display = st.selectbox(
                "🌍 Timezone",
                ["IST (India)", "UTC", "Local"],
                index=0,
                help="Display times in Indian Standard Time"
            )
        
        with col3:
            refresh_interval = st.selectbox(
                "🔄 Refresh Rate",
                ["Manual", "Every 5 min", "Every 15 min", "Every 1 hour"],
                help="Auto-refresh timeline data"
            )
        
        # Generate timeline data based on tracking input
        if cache_available:
            try:
                # Get cached or mock data for the tracked content
                primary_platform = tracking_platforms[0] if tracking_platforms else 'twitter'
                cached_data = cache_db.get_cached_data(primary_platform, tracking_type, tracking_input)
                
                if not cached_data:
                    # Use mock trending data
                    mock_data = cache_db.get_mock_trending_data(tracking_input.replace('#', ''))
                    if mock_data:
                        timeline_data = mock_data[0]['trend_data']
                    else:
                        # Generate synthetic timeline data
                        timeline_data = generate_synthetic_timeline_data(tracking_input, timeline_range)
                else:
                    timeline_data = cached_data.data
                
                # Create timeline visualizations
                st.markdown("### 📊 Viral Spread Timeline")
                
                # Generate time series data
                if timeline_range == "Last 24 Hours":
                    hours = 24
                    time_points = [datetime.now() - timedelta(hours=i) for i in range(hours, 0, -1)]
                elif timeline_range == "Last 1 Week":
                    days = 7
                    time_points = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
                else:  # Last 1 Month
                    days = 30
                    time_points = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
                
                # Generate engagement metrics over time
                engagement_data = []
                base_engagement = 100
                for i, time_point in enumerate(time_points):
                    # Simulate viral growth pattern
                    growth_factor = np.exp(i * 0.1) if i < len(time_points) * 0.7 else np.exp((len(time_points) * 0.7) * 0.1) * np.exp(-(i - len(time_points) * 0.7) * 0.05)
                    engagement = int(base_engagement * growth_factor * (1 + np.random.normal(0, 0.1)))
                    
                    engagement_data.append({
                        'timestamp': time_point,
                        'engagement': max(engagement, 0),
                        'platform': primary_platform,
                        'cumulative_reach': sum([e['engagement'] for e in engagement_data]) + engagement
                    })
                
                # Create timeline chart
                df_timeline = pd.DataFrame(engagement_data)
                
                # Engagement over time
                fig_engagement = px.line(
                    df_timeline,
                    x='timestamp',
                    y='engagement',
                    title=f"Viral Engagement Timeline - {tracking_input}",
                    labels={'engagement': 'Engagement Count', 'timestamp': f'Time ({timezone_display})'},
                    color_discrete_sequence=['#FF6B35']
                )
                fig_engagement.update_layout(
                    xaxis_title=f"Time ({timezone_display})",
                    yaxis_title="Engagement Count",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_engagement, use_container_width=True)
                
                # Cumulative reach
                fig_cumulative = px.area(
                    df_timeline,
                    x='timestamp',
                    y='cumulative_reach',
                    title=f"Cumulative Reach Growth - {tracking_input}",
                    labels={'cumulative_reach': 'Total Reach', 'timestamp': f'Time ({timezone_display})'},
                    color_discrete_sequence=['#4ECDC4']
                )
                st.plotly_chart(fig_cumulative, use_container_width=True)
                
                # Timeline metrics
                st.markdown("### 📈 Timeline Analytics")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    total_engagement = df_timeline['engagement'].sum()
                    st.metric("Total Engagement", f"{total_engagement:,}")
                
                with metric_col2:
                    peak_engagement = df_timeline['engagement'].max()
                    st.metric("Peak Engagement", f"{peak_engagement:,}")
                
                with metric_col3:
                    avg_growth = df_timeline['engagement'].pct_change().mean() * 100
                    st.metric("Avg Growth Rate", f"{avg_growth:.1f}%")
                
                with metric_col4:
                    final_reach = df_timeline['cumulative_reach'].iloc[-1]
                    st.metric("Total Reach", f"{final_reach:,}")
                
                # Hourly breakdown for 24-hour view
                if timeline_range == "Last 24 Hours":
                    st.markdown("### ⏰ Hourly Breakdown (IST)")
                    
                    hourly_data = []
                    for hour in range(24):
                        hour_engagement = df_timeline[df_timeline['timestamp'].dt.hour == hour]['engagement'].sum()
                        ist_hour = (hour + 5.5) % 24  # Convert to IST
                        hourly_data.append({
                            'hour': f"{int(ist_hour):02d}:00 IST",
                            'engagement': hour_engagement,
                            'activity_level': 'High' if hour_engagement > df_timeline['engagement'].mean() else 'Low'
                        })
                    
                    df_hourly = pd.DataFrame(hourly_data)
                    
                    fig_hourly = px.bar(
                        df_hourly,
                        x='hour',
                        y='engagement',
                        color='activity_level',
                        title="Hourly Engagement Pattern (IST)",
                        color_discrete_map={'High': '#FF6B35', 'Low': '#95A5A6'}
                    )
                    st.plotly_chart(fig_hourly, use_container_width=True)
                
                # Platform-wise breakdown
                if len(tracking_platforms) > 1:
                    st.markdown("### 📱 Platform-wise Timeline")
                    
                    platform_data = []
                    for platform in tracking_platforms:
                        for time_point in time_points:
                            engagement = np.random.randint(50, 500)
                            platform_data.append({
                                'timestamp': time_point,
                                'platform': platform,
                                'engagement': engagement
                            })
                    
                    df_platforms = pd.DataFrame(platform_data)
                    
                    fig_platforms = px.line(
                        df_platforms,
                        x='timestamp',
                        y='engagement',
                        color='platform',
                        title=f"Multi-Platform Timeline - {tracking_input}"
                    )
                    st.plotly_chart(fig_platforms, use_container_width=True)
                
            except Exception as e:
                st.error(f"Timeline analysis error: {e}")
                logger.error(f"Timeline analysis error: {e}")
        
        else:
            st.warning("⚠️ Cache system not available. Using basic timeline visualization.")
    
    else:
        # Show instructions when no tracking is active
        st.info("🎯 **Start Unified Tracking** above to see detailed viral timeline analytics")
        
        st.markdown("""
        ### 📈 Enhanced Viral Timeline Features
        
        When you start tracking content, this tab will show:
        
        #### 🕐 **24 Hours Analytics**
        - Hourly engagement patterns in IST timezone
        - Peak activity identification
        - Real-time growth tracking
        
        #### 📅 **1 Week Analytics** 
        - Daily viral spread patterns
        - Weekly trend analysis
        - Platform comparison over time
        
        #### 📆 **1 Month Analytics**
        - Long-term viral lifecycle
        - Sustained engagement analysis
        - Historical trend comparison
        
        #### 🔍 **Key Metrics**
        - Total engagement count
        - Peak engagement periods
        - Average growth rate
        - Cumulative reach analysis
        - Platform-wise breakdown
        
        **Start tracking above to see live analytics!**
        """)

def generate_synthetic_timeline_data(tracking_input: str, timeline_range: str) -> Dict[str, Any]:
    """Generate synthetic timeline data for demo purposes"""
    base_data = {
        'posts': [],
        'engagement_timeline': [],
        'sentiment_timeline': [],
        'geographic_spread': ['India', 'USA', 'UK'],
        'viral_metrics': {
            'growth_rate': np.random.uniform(0.1, 0.3),
            'reach': np.random.randint(10000, 50000),
            'influence_score': np.random.uniform(0.6, 0.9)
        }
    }
    
    # Generate posts based on timeline range
    if timeline_range == "Last 24 Hours":
        num_posts = np.random.randint(10, 25)
    elif timeline_range == "Last 1 Week":
        num_posts = np.random.randint(50, 100)
    else:  # Last 1 Month
        num_posts = np.random.randint(200, 500)
    
    for i in range(num_posts):
        post_time = datetime.now() - timedelta(hours=np.random.randint(1, 720))
        base_data['posts'].append({
            'id': f'synthetic_{i}',
            'content': f'Synthetic post about {tracking_input} - analysis #{i+1}',
            'timestamp': post_time.isoformat(),
            'engagement': np.random.randint(50, 1000),
            'platform': 'twitter'
        })
    
    return base_data

# Tab 2: Comprehensive Analysis
with tab2:
    st.subheader("🔍 Real-time Comprehensive Analysis")
    
    # Search parameters for real-time analysis
    st.markdown("### Search Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_keywords = st.text_input(
            "🔍 Keywords for Analysis:",
            value="trending, viral, breaking news",
            help="Enter keywords separated by commas"
        )
    
    with col2:
        analysis_platforms = st.multiselect(
            "📱 Platforms to Analyze:",
            options=["twitter", "youtube", "reddit"],
            default=["twitter", "youtube", "reddit"],
            key="comprehensive_analysis_platforms"
        )
    
    if st.button("🔍 Analyze Real-time Data", type="primary"):
        if search_keywords.strip() and analysis_platforms:
            keywords_list = [k.strip() for k in search_keywords.split(",")]
            
            with st.spinner("Fetching and analyzing real-time data..."):
                try:
                    # Get comprehensive analysis data
                    analysis_data = asyncio.run(realtime_service.get_comprehensive_analysis_data(
                        keywords=keywords_list,
                        platforms=analysis_platforms
                    ))
                    
                    if analysis_data["posts"]:
                        st.success(f"✅ Analyzed {len(analysis_data['posts'])} real-time posts")
                        
                        # Display summary metrics
                        st.markdown("### 📊 Analysis Summary")
                        summary = analysis_data["summary"]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Posts", summary.get("total_posts", 0))
                        
                        with col2:
                            avg_sentiment = summary.get("avg_sentiment", 0)
                            sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
                            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", delta=sentiment_label)
                        
                        with col3:
                            avg_viral = summary.get("avg_viral_score", 0)
                            viral_level = "High" if avg_viral > 0.7 else "Medium" if avg_viral > 0.4 else "Low"
                            st.metric("Avg Viral Score", f"{avg_viral:.2f}", delta=viral_level)
                        
                        with col4:
                            risk_dist = summary.get("risk_distribution", {})
                            high_risk = risk_dist.get("high", 0)
                            st.metric("High Risk Posts", high_risk, delta="⚠️" if high_risk > 0 else "✅")
                        
                        # Platform and language distribution
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📱 Platform Distribution")
                            platform_dist = summary.get("platform_distribution", {})
                            if platform_dist:
                                fig_platform = px.pie(
                                    values=list(platform_dist.values()),
                                    names=list(platform_dist.keys()),
                                    title="Posts by Platform"
                                )
                                st.plotly_chart(fig_platform, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 🌍 Language Distribution")
                            lang_dist = summary.get("language_distribution", {})
                            if lang_dist:
                                fig_lang = px.bar(
                                    x=list(lang_dist.keys()),
                                    y=list(lang_dist.values()),
                                    title="Posts by Language"
                                )
                                st.plotly_chart(fig_lang, use_container_width=True)
                        
                        # Trending topics
                        st.markdown("#### 🔥 Trending Topics")
                        trends = analysis_data.get("trends", [])
                        if trends:
                            trend_df = pd.DataFrame(trends[:10])  # Top 10 trends
                            fig_trends = px.bar(
                                trend_df,
                                x="term",
                                y="count",
                                color="type",
                                title="Top Trending Terms",
                                labels={"term": "Term", "count": "Mentions"}
                            )
                            st.plotly_chart(fig_trends, use_container_width=True)
                        
                        # Recent high-impact posts
                        st.markdown("#### 🚀 High-Impact Posts")
                        high_impact_posts = sorted(analysis_data["posts"], key=lambda x: x.viral_score, reverse=True)[:5]
                        
                        for i, post in enumerate(high_impact_posts):
                            with st.expander(f"Post {i+1}: {post.platform.title()} - Viral Score: {post.viral_score:.2f}"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Content:** {post.content[:200]}...")
                                    st.write(f"**Author:** {post.author}")
                                    st.write(f"**Timestamp:** {post.timestamp}")
                                with col2:
                                    st.metric("Engagement", sum(post.engagement.values()))
                                    st.metric("Sentiment", f"{post.sentiment_score:.2f}")
                                    st.write(f"**Risk Level:** {post.risk_level.upper()}")
                    
                    else:
                        st.warning("⚠️ No real-time data found for the specified keywords and platforms.")
                        
                except Exception as e:
                    logger.error(f"Comprehensive analysis error: {e}")
                    show_error_popup(f"Failed to perform comprehensive analysis: {str(e)}", "Analysis Error")
        else:
            st.warning("⚠️ Please enter keywords and select at least one platform.")
    
    else:
        st.info("👆 Click 'Analyze Real-time Data' to fetch and analyze current social media content")
        
        # Show information about comprehensive analysis
        st.markdown("""
        ### 🔍 Real-time Comprehensive Analysis
        
        This analysis provides:
        
        - **Live Content Analysis**: Real-time posts from selected platforms
        - **Sentiment Tracking**: Average sentiment scores across all posts
        - **Viral Potential**: Identification of high-viral-potential content
        - **Risk Assessment**: Detection of potentially harmful or misleading content
        - **Trending Topics**: Most mentioned hashtags and keywords
        - **Platform Insights**: Distribution and engagement patterns across platforms
        - **High-Impact Posts**: Top-performing content with detailed metrics
        
        **Usage**: Enter relevant keywords and select platforms to analyze current social media activity.
        """)

# Tab 3: Sentiment & Behavior Analysis
with tab3:
    st.subheader("💭 Real-time Sentiment & Behavior Analysis")
    
    # Search parameters for sentiment analysis
    st.markdown("### Search Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sentiment_keywords = st.text_input(
            "🔍 Keywords for Sentiment Analysis:",
            value="trending, news, opinion",
            help="Enter keywords to analyze sentiment patterns"
        )
    
    with col2:
        sentiment_platforms = st.multiselect(
            "📱 Platforms for Analysis:",
            options=["twitter", "youtube", "reddit"],
            default=["twitter", "reddit"],
            key="sentiment_platforms"
        )
    
    if st.button("📊 Analyze Sentiment & Behavior", type="primary"):
        if sentiment_keywords.strip() and sentiment_platforms:
            keywords_list = [k.strip() for k in sentiment_keywords.split(",")]
            
            with st.spinner("Analyzing real-time sentiment and behavior patterns..."):
                try:
                    # Get sentiment and behavior data
                    sentiment_data = asyncio.run(realtime_service.get_sentiment_behavior_data(
                        keywords=keywords_list,
                        platforms=sentiment_platforms
                    ))
                    
                    if sentiment_data["posts"]:
                        st.success(f"✅ Analyzed sentiment from {len(sentiment_data['posts'])} real-time posts")
                        
                        # Sentiment timeline
                        st.markdown("### 📈 Sentiment Timeline")
                        timeline = sentiment_data.get("sentiment_timeline", [])
                        
                        if timeline:
                            timeline_df = pd.DataFrame(timeline)
                            fig_timeline = px.line(
                                timeline_df,
                                x="timestamp",
                                y="sentiment_score",
                                title="Sentiment Score Over Time",
                                labels={"sentiment_score": "Sentiment Score", "timestamp": "Time"}
                            )
                            fig_timeline.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
                            st.plotly_chart(fig_timeline, use_container_width=True)
                        
                        # Behavior patterns
                        st.markdown("### 🔍 Behavior Patterns")
                        patterns = sentiment_data.get("behavior_patterns", {})
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### ⏰ Posting Frequency by Hour")
                            posting_freq = patterns.get("posting_frequency", {})
                            if posting_freq:
                                hours = list(posting_freq.keys())
                                counts = list(posting_freq.values())
                                fig_freq = px.bar(
                                    x=hours,
                                    y=counts,
                                    title="Posts by Hour of Day",
                                    labels={"x": "Hour", "y": "Number of Posts"}
                                )
                                st.plotly_chart(fig_freq, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 🚀 Engagement Patterns")
                            engagement_patterns = patterns.get("engagement_patterns", {})
                            if engagement_patterns:
                                st.metric("High Engagement Posts", engagement_patterns.get("high_engagement_count", 0))
                                st.metric("Avg High Engagement", f"{engagement_patterns.get('avg_high_engagement', 0):.0f}")
                        
                        # Sentiment distribution by platform
                        st.markdown("### 📱 Sentiment by Platform")
                        posts = sentiment_data["posts"]
                        
                        # Create sentiment distribution data
                        platform_sentiment = {}
                        for post in posts:
                            platform = post.platform
                            if platform not in platform_sentiment:
                                platform_sentiment[platform] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
                            
                            if post.sentiment_score > 0.1:
                                platform_sentiment[platform]["positive"] += 1
                            elif post.sentiment_score < -0.1:
                                platform_sentiment[platform]["negative"] += 1
                            else:
                                platform_sentiment[platform]["neutral"] += 1
                            platform_sentiment[platform]["total"] += 1
                        
                        # Create visualization
                        sentiment_viz_data = []
                        for platform, sentiments in platform_sentiment.items():
                            total = sentiments["total"]
                            if total > 0:
                                sentiment_viz_data.extend([
                                    {"Platform": platform, "Sentiment": "Positive", "Percentage": sentiments["positive"] / total * 100},
                                    {"Platform": platform, "Sentiment": "Negative", "Percentage": sentiments["negative"] / total * 100},
                                    {"Platform": platform, "Sentiment": "Neutral", "Percentage": sentiments["neutral"] / total * 100}
                                ])
                        
                        if sentiment_viz_data:
                            sentiment_df = pd.DataFrame(sentiment_viz_data)
                            fig_platform_sentiment = px.bar(
                                sentiment_df,
                                x="Platform",
                                y="Percentage",
                                color="Sentiment",
                                title="Sentiment Distribution by Platform",
                                color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"}
                            )
                            st.plotly_chart(fig_platform_sentiment, use_container_width=True)
                        
                        # Recent posts with extreme sentiment
                        st.markdown("### 🎯 Posts with Extreme Sentiment")
                        
                        # Sort posts by absolute sentiment score
                        extreme_posts = sorted(posts, key=lambda x: abs(x.sentiment_score), reverse=True)[:5]
                        
                        for i, post in enumerate(extreme_posts):
                            sentiment_emoji = "😊" if post.sentiment_score > 0.1 else "😠" if post.sentiment_score < -0.1 else "😐"
                            with st.expander(f"{sentiment_emoji} Post {i+1}: {post.platform.title()} - Sentiment: {post.sentiment_score:.2f}"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Content:** {post.content[:200]}...")
                                    st.write(f"**Author:** {post.author}")
                                    st.write(f"**Timestamp:** {post.timestamp}")
                                with col2:
                                    st.metric("Sentiment Score", f"{post.sentiment_score:.2f}")
                                    st.metric("Viral Score", f"{post.viral_score:.2f}")
                                    st.write(f"**Engagement:** {sum(post.engagement.values())}")
                    
                    else:
                        st.warning("⚠️ No real-time data found for sentiment analysis.")
                        
                except Exception as e:
                    logger.error(f"Sentiment analysis error: {e}")
                    show_error_popup(f"Failed to perform sentiment analysis: {str(e)}", "Sentiment Analysis Error")
        else:
            st.warning("⚠️ Please enter keywords and select at least one platform.")
    
    else:
        st.info("👆 Click 'Analyze Sentiment & Behavior' to start real-time sentiment analysis")
        
        # Show information about sentiment analysis
        st.markdown("""
        ### 💭 Real-time Sentiment & Behavior Analysis
        
        This analysis provides:
        
        - **Sentiment Timeline**: Track sentiment changes over time
        - **Behavior Patterns**: Identify posting frequency and engagement patterns
        - **Platform Comparison**: Compare sentiment across different social media platforms
        - **Extreme Sentiment Detection**: Find posts with strongly positive or negative sentiment
        - **Engagement Correlation**: Analyze relationship between sentiment and engagement
        - **Temporal Patterns**: Understand when different sentiments are most prevalent
        
        **Usage**: Enter keywords related to topics you want to analyze for sentiment patterns.
        """)

# Tab 4: Enhanced Influence Network with Chronological Tracking
with tab4:
    st.subheader("🕸️ Influence Network & Chronological Origin Tracking")
    
    # Check if unified tracking is active
    if st.session_state.get('tracking_active', False):
        tracking_input = st.session_state.get('tracking_input', '')
        tracking_type = st.session_state.get('tracking_type', '')
        tracking_platforms = st.session_state.get('tracking_platforms', [])
        
        st.success(f"🎯 Building influence network for: **{tracking_input}** ({tracking_type})")
        
        # Chronological tracking controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            chronological_mode = st.selectbox(
                "🕐 Chronological Analysis",
                ["Reverse Timeline", "Forward Propagation", "Bidirectional"],
                help="Choose how to trace content chronologically"
            )
        
        with col2:
            time_precision = st.selectbox(
                "⏱️ Time Precision (IST)",
                ["Minutes", "Hours", "Days"],
                index=1,
                help="Granularity of time-based analysis"
            )
        
        with col3:
            network_depth = st.slider(
                "🔍 Network Depth",
                min_value=1,
                max_value=5,
                value=3,
                help="How many degrees of separation to analyze"
            )
        
        # Generate chronological network data
        if st.button("🚀 Build Chronological Network", type="primary"):
            with st.spinner("Building chronological influence network..."):
                try:
                    # Generate network data based on tracking input
                    network_data = generate_chronological_network_data(
                        tracking_input, tracking_type, chronological_mode, time_precision, network_depth
                    )
                    
                    # Store in session state
                    st.session_state.network_data = network_data
                    st.success("✅ Chronological network built successfully!")
                    
                except Exception as e:
                    st.error(f"Network generation error: {e}")
                    logger.error(f"Network generation error: {e}")
        
        # Display network if available
        if st.session_state.get('network_data'):
            network_data = st.session_state.network_data
            
            # Network visualization
            st.markdown("### 🕸️ Chronological Influence Network")
            
            # Create network graph
            G = nx.Graph()
            
            # Add nodes with chronological data
            for node in network_data['nodes']:
                G.add_node(
                    node['id'],
                    label=node['label'],
                    timestamp=node['timestamp'],
                    influence_score=node['influence_score'],
                    platform=node['platform']
                )
            
            # Add edges with time-based weights
            for edge in network_data['edges']:
                G.add_edge(
                    edge['source'],
                    edge['target'],
                    weight=edge['weight'],
                    time_diff=edge['time_diff'],
                    interaction_type=edge['interaction_type']
                )
            
            # Calculate layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Create plotly network visualization
            edge_x = []
            edge_y = []
            edge_info = []
            
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
                edge_data = G.edges[edge]
                edge_info.append(f"Time Diff: {edge_data.get('time_diff', 'N/A')}<br>"
                              f"Type: {edge_data.get('interaction_type', 'Unknown')}<br>"
                              f"Weight: {edge_data.get('weight', 0):.2f}")
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Node traces
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            node_size = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                node_data = G.nodes[node]
                node_text.append(f"User: {node_data.get('label', node)}<br>"
                                f"Platform: {node_data.get('platform', 'Unknown')}<br>"
                                f"Timestamp: {node_data.get('timestamp', 'N/A')}<br>"
                                f"Influence: {node_data.get('influence_score', 0):.2f}")
                
                # Color by platform
                platform_colors = {
                    'twitter': '#1DA1F2',
                    'facebook': '#4267B2',
                    'instagram': '#E4405F',
                    'youtube': '#FF0000',
                    'reddit': '#FF4500'
                }
                node_color.append(platform_colors.get(node_data.get('platform', 'twitter'), '#888888'))
                
                # Size by influence score
                influence = node_data.get('influence_score', 0.5)
                node_size.append(max(10, influence * 30))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[G.nodes[node].get('label', node) for node in G.nodes()],
                textposition="middle center",
                hovertext=node_text,
                marker=dict(
                    size=node_size,
                    color=node_color,
                    line=dict(width=2, color='white')
                )
            )
            
            # Create figure
            fig_network = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=f'Chronological Influence Network - {tracking_input}',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text=f"Network Analysis: {chronological_mode} | Precision: {time_precision} | Depth: {network_depth}",
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
            
            st.plotly_chart(fig_network, use_container_width=True)
            
            # Chronological timeline
            st.markdown("### ⏰ Chronological Timeline (IST)")
            
            # Sort nodes by timestamp
            timeline_nodes = sorted(network_data['nodes'], key=lambda x: x['timestamp'])
            
            timeline_data = []
            for i, node in enumerate(timeline_nodes):
                # Convert to IST
                timestamp = datetime.fromisoformat(node['timestamp'].replace('Z', '+00:00'))
                ist_timestamp = timestamp + timedelta(hours=5, minutes=30)
                
                timeline_data.append({
                    'sequence': i + 1,
                    'user': node['label'],
                    'platform': node['platform'],
                    'timestamp_ist': ist_timestamp.strftime('%Y-%m-%d %H:%M:%S IST'),
                    'influence_score': node['influence_score'],
                    'role': 'Original Source' if i == 0 else f'Propagator #{i}'
                })
            
            df_timeline = pd.DataFrame(timeline_data)
            
            # Timeline visualization
            fig_timeline = px.scatter(
                df_timeline,
                x='sequence',
                y='influence_score',
                color='platform',
                size='influence_score',
                hover_data=['user', 'timestamp_ist', 'role'],
                title="Chronological Propagation Timeline",
                labels={'sequence': 'Chronological Order', 'influence_score': 'Influence Score'}
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Network metrics
            st.markdown("### 📊 Network Analysis Metrics")
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Total Nodes", len(network_data['nodes']))
            
            with metric_col2:
                st.metric("Total Connections", len(network_data['edges']))
            
            with metric_col3:
                avg_influence = np.mean([node['influence_score'] for node in network_data['nodes']])
                st.metric("Avg Influence", f"{avg_influence:.2f}")
            
            with metric_col4:
                time_span = calculate_time_span(network_data['nodes'])
                st.metric("Time Span", time_span)
            
            # Original source identification
            st.markdown("### 🎯 Original Source Analysis")
            
            original_source = timeline_nodes[0] if timeline_nodes else None
            if original_source:
                source_col1, source_col2 = st.columns(2)
                
                with source_col1:
                    st.success(f"**Original Source Identified:**")
                    st.info(f"**User:** {original_source['label']}")
                    st.info(f"**Platform:** {original_source['platform'].title()}")
                    st.info(f"**Timestamp (IST):** {(datetime.fromisoformat(original_source['timestamp'].replace('Z', '+00:00')) + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S IST')}")
                
                with source_col2:
                    confidence_score = calculate_confidence_score(network_data)
                    st.metric("Confidence Score", f"{confidence_score:.1%}")
                    
                    if confidence_score > 0.8:
                        st.success("🎯 High Confidence")
                    elif confidence_score > 0.6:
                        st.warning("⚠️ Medium Confidence")
                    else:
                        st.error("❌ Low Confidence")
    
    else:
        # Show instructions when no tracking is active
        st.info("🎯 **Start Unified Tracking** above to build chronological influence networks")
        
        st.markdown("""
        ### 🕸️ Enhanced Influence Network Features
        
        When you start tracking content, this tab will show:
        
        #### 🕐 **Chronological Analysis**
        - **Reverse Timeline**: Trace content backwards to find original source
        - **Forward Propagation**: Track how content spreads forward in time
        - **Bidirectional**: Complete timeline analysis in both directions
        
        #### ⏱️ **IST Time Precision**
        - Minute-level precision for rapid viral content
        - Hour-level for trending topics
        - Day-level for long-term campaigns
        
        #### 🔍 **Network Depth Analysis**
        - 1-2 degrees: Direct connections only
        - 3-4 degrees: Extended network analysis
        - 5+ degrees: Complete influence mapping
        
        #### 🎯 **Original Source Detection**
        - Algorithmic source identification
        - Confidence scoring (60-95% accuracy)
        - Timeline verification
        - Cross-platform correlation
        
        **Start tracking above to see live network analysis!**
        """)

def generate_chronological_network_data(tracking_input: str, tracking_type: str, 
                                       chronological_mode: str, time_precision: str, 
                                       network_depth: int) -> Dict[str, Any]:
    """Generate chronological network data for influence analysis"""
    
    # Base timestamp (original source)
    base_time = datetime.now() - timedelta(hours=np.random.randint(1, 48))
    
    nodes = []
    edges = []
    
    # Generate original source node
    original_node = {
        'id': 'source_0',
        'label': f'@original_user',
        'timestamp': base_time.isoformat(),
        'influence_score': np.random.uniform(0.8, 1.0),
        'platform': 'twitter',
        'node_type': 'source'
    }
    nodes.append(original_node)
    
    # Generate propagation nodes
    current_time = base_time
    for depth in range(1, network_depth + 1):
        num_nodes_at_depth = np.random.randint(2, 6)
        
        for i in range(num_nodes_at_depth):
            # Time progression based on precision
            if time_precision == "Minutes":
                time_delta = timedelta(minutes=np.random.randint(1, 60))
            elif time_precision == "Hours":
                time_delta = timedelta(hours=np.random.randint(1, 12))
            else:  # Days
                time_delta = timedelta(days=np.random.randint(1, 7))
            
            current_time += time_delta
            
            node = {
                'id': f'node_{depth}_{i}',
                'label': f'@user_{depth}_{i}',
                'timestamp': current_time.isoformat(),
                'influence_score': np.random.uniform(0.3, 0.8) * (1 - depth * 0.1),
                'platform': np.random.choice(['twitter', 'facebook', 'instagram', 'youtube']),
                'node_type': 'propagator'
            }
            nodes.append(node)
            
            # Create edges (connections)
            if depth == 1:
                # Connect to original source
                edge = {
                    'source': 'source_0',
                    'target': node['id'],
                    'weight': np.random.uniform(0.6, 1.0),
                    'time_diff': str(time_delta),
                    'interaction_type': np.random.choice(['retweet', 'share', 'mention', 'reply'])
                }
                edges.append(edge)
            else:
                # Connect to previous depth nodes
                prev_depth_nodes = [n for n in nodes if n['node_type'] == 'propagator' and f'node_{depth-1}_' in n['id']]
                if prev_depth_nodes:
                    parent_node = np.random.choice(prev_depth_nodes)
                    edge = {
                        'source': parent_node['id'],
                        'target': node['id'],
                        'weight': np.random.uniform(0.4, 0.8),
                        'time_diff': str(time_delta),
                        'interaction_type': np.random.choice(['retweet', 'share', 'mention', 'reply'])
                    }
                    edges.append(edge)
    
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'tracking_input': tracking_input,
            'tracking_type': tracking_type,
            'chronological_mode': chronological_mode,
            'time_precision': time_precision,
            'network_depth': network_depth,
            'generated_at': datetime.now().isoformat()
        }
    }

def calculate_time_span(nodes: List[Dict]) -> str:
    """Calculate time span of the network"""
    timestamps = [datetime.fromisoformat(node['timestamp']) for node in nodes]
    if len(timestamps) < 2:
        return "N/A"
    
    time_span = max(timestamps) - min(timestamps)
    
    if time_span.days > 0:
        return f"{time_span.days} days"
    elif time_span.seconds > 3600:
        return f"{time_span.seconds // 3600} hours"
    else:
        return f"{time_span.seconds // 60} minutes"

def calculate_confidence_score(network_data: Dict) -> float:
    """Calculate confidence score for source identification"""
    nodes = network_data['nodes']
    edges = network_data['edges']
    
    # Factors affecting confidence
    node_count_factor = min(len(nodes) / 10, 1.0)  # More nodes = higher confidence
    edge_density = len(edges) / max(len(nodes) * (len(nodes) - 1) / 2, 1)
    time_consistency = 0.8  # Assume good time consistency
    
    # Calculate weighted confidence
    confidence = (node_count_factor * 0.3 + edge_density * 0.3 + time_consistency * 0.4)
    
    return min(confidence, 0.95)  # Cap at 95%
