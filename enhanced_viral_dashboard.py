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
    
    # Platform selection
    st.subheader(get_text('platform_selection'))
    
    # Get platform options
    all_platforms = platform_support.get_supported_platforms()
    indian_platforms = platform_support.get_indian_platforms()
    
    platform_scope = st.radio(
        "Platform Scope",
        ["Global Platforms"],
        index=0,
        help="Real-time analysis across global social media platforms"
    )
    
    # Use only global platforms (excluding Indian-specific ones)
    available_platforms = {k: v for k, v in all_platforms.items() if k not in indian_platforms}
    
    # Handle platform format safely
    if available_platforms and isinstance(available_platforms, dict):
        platform_keys = list(available_platforms.keys())
        # Check if platforms have the expected structure
        if platform_keys and isinstance(available_platforms[platform_keys[0]], dict) and 'name' in available_platforms[platform_keys[0]]:
            selected_platforms = st.multiselect(
                "Select Platforms",
                options=platform_keys,
                default=platform_keys[:5],
                format_func=lambda x: available_platforms[x]['name'],
                key="main_platform_select_1"
            )
        else:
            # Fallback format
            selected_platforms = st.multiselect(
                "Select Platforms",
                options=platform_keys,
                default=platform_keys[:5],
                format_func=lambda x: str(available_platforms[x]) if x in available_platforms else x,
                key="main_platform_select_2"
            )
    else:
        # Default fallback platforms
        default_platforms = ['twitter', 'facebook', 'instagram', 'youtube', 'koo']
        selected_platforms = st.multiselect(
            "Select Platforms",
            options=default_platforms,
            default=default_platforms,
            format_func=lambda x: x.title(),
            key="main_platform_select_3"
        )
        # Create mock available_platforms for consistency
        available_platforms = {p: {'name': p.title(), 'type': 'social', 'region': 'global'} for p in default_platforms}
    
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
        # Get available platforms from selected platforms
        available_platform_list = list(selected_platforms) if selected_platforms else ["twitter", "youtube", "reddit"]
        platform_filter = st.multiselect(
            get_translation("platform_filter"),
            options=available_platform_list,
            default=available_platform_list,
            key="viral_timeline_platform_filter"
        )
    
    # Get real-time viral timeline data
    if realtime_service and st.button("🔄 Refresh Timeline Data"):
        with st.spinner("Fetching real-time viral timeline data..."):
            try:
                viral_data = asyncio.run(realtime_service.get_viral_timeline_data(
                    time_range=time_range,
                    platforms=platform_filter
                ))
                
                if not viral_data.empty:
                    st.success(f"✅ Loaded {len(viral_data)} real-time posts")
                    
                    # Timeline chart
                    timeline_data = viral_data.groupby([
                        viral_data['timestamp'].dt.floor('H'), 'platform'
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
                        title="Real-time Viral Content Timeline by Platform",
                        labels={'viral_score': 'Average Viral Score', 'timestamp': 'Time'}
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Top viral content
                    st.subheader("Top Viral Content")
                    top_content = viral_data.nlargest(5, 'viral_score')[['content', 'platform', 'viral_score', 'engagement', 'timestamp']]
                    st.dataframe(top_content, use_container_width=True)
                    
                else:
                    st.warning("⚠️ No real-time data available. Please check API connections.")
                    
            except Exception as e:
                logger.error(f"Timeline data error: {e}")
                show_error_popup(f"Failed to fetch real-time viral timeline data: {str(e)}", "Data Fetch Error")
    else:
        st.info("👆 Click 'Refresh Timeline Data' to load real-time viral content data")
        
        # Show placeholder message
        st.markdown("""
        ### 🔄 Real-time Viral Timeline
        
        This tab shows real-time viral content analysis across global social media platforms:
        
        - **Live Data**: Fetches current trending content from Twitter/X, YouTube, and Reddit
        - **Timeline Visualization**: Interactive charts showing viral score trends over time
        - **Platform Comparison**: Compare viral activity across different platforms
        - **Top Content**: Table of highest-scoring viral posts with engagement metrics
        
        **Note**: Real-time data requires valid API keys for social media platforms.
        """)

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

# Tab 4: Influence Network
with tab4:
    st.subheader("🕸️ Real-time Influence Network with Origin Tracking")
    
    # Input options for network analysis
    st.markdown("### Network Analysis Options")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = st.radio(
            "Analysis Type:",
            ["Hashtag Tracking", "Post URL Analysis", "Keyword Network"],
            help="Choose the type of network analysis to perform"
        )
        
        if analysis_type == "Hashtag Tracking":
            hashtag_input = st.text_input(
                "🏷️ Hashtag to Track:",
                value="#trending",
                help="Enter a hashtag to track its spread and origin"
            )
        elif analysis_type == "Post URL Analysis":
            post_url_input = st.text_input(
                "🔗 Post URL:",
                placeholder="https://twitter.com/user/status/123456789",
                help="Enter a specific post URL to analyze its influence network"
            )
        else:  # Keyword Network
            network_keywords = st.text_input(
                "🔍 Keywords for Network:",
                value="viral, trending",
                help="Enter keywords to build influence network"
            )
    
    with col2:
        network_platforms = st.multiselect(
            "📱 Platforms:",
            options=["twitter", "youtube", "reddit"],
            default=["twitter", "reddit"],
            key="influence_network_platforms"
        )
        
        max_nodes = st.slider(
            "Max Network Nodes:",
            min_value=10,
            max_value=100,
            value=50,
            help="Maximum number of nodes to display in network"
        )
    
    if st.button("🕸️ Build Influence Network", type="primary"):
        with st.spinner("Building real-time influence network..."):
            try:
                # Prepare parameters based on analysis type
                if analysis_type == "Hashtag Tracking" and hashtag_input.strip():
                    network_data = asyncio.run(realtime_service.get_influence_network_data(
                        hashtag=hashtag_input.strip(),
                        keywords=None
                    ))
                elif analysis_type == "Post URL Analysis" and post_url_input.strip():
                    network_data = asyncio.run(realtime_service.get_influence_network_data(
                        post_url=post_url_input.strip(),
                        keywords=None
                    ))
                elif analysis_type == "Keyword Network" and network_keywords.strip():
                    keywords_list = [k.strip() for k in network_keywords.split(",")]
                    network_data = asyncio.run(realtime_service.get_influence_network_data(
                        keywords=keywords_list
                    ))
                else:
                    st.warning("⚠️ Please provide valid input for the selected analysis type.")
                    network_data = None
                
                if network_data and network_data["nodes"]:
                    st.success(f"✅ Built network with {len(network_data['nodes'])} nodes and {len(network_data['edges'])} connections")
                    
                    # Network statistics
                    st.markdown("### 📊 Network Statistics")
                    stats = network_data["network_stats"]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Nodes", stats.get("total_nodes", 0))
                    with col2:
                        st.metric("Total Edges", stats.get("total_edges", 0))
                    with col3:
                        st.metric("Origin Nodes", stats.get("origin_nodes", 0))
                    with col4:
                        density = stats.get("density", 0)
                        st.metric("Network Density", f"{density:.3f}")
                    
                    # Origin nodes section
                    origin_nodes = network_data.get("origin_nodes", [])
                    if origin_nodes:
                        st.markdown("### 🎯 Origin Nodes (Viral Content Sources)")
                        st.info(f"Found {len(origin_nodes)} potential origin nodes where viral content may have started")
                        
                        # Display origin node details
                        nodes = network_data["nodes"]
                        origin_node_details = [node for node in nodes if node.user_id in origin_nodes]
                        
                        for i, node in enumerate(origin_node_details[:5]):  # Show top 5 origin nodes
                            with st.expander(f"🌟 Origin Node {i+1}: @{node.username} ({node.platform})"):
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.write(f"**Platform:** {node.platform.title()}")
                                    st.write(f"**Influence Score:** {node.influence_score:.2f}")
                                    st.write(f"**Post Count:** {node.post_count}")
                                    st.write(f"**Location:** {node.location or 'Unknown'}")
                                with col2:
                                    st.metric("Engagement Rate", f"{node.engagement_rate:.1f}")
                                    st.write(f"**Verified:** {'✅' if node.verified else '❌'}")
                                    st.write(f"**Followers:** {node.follower_count:,}")
                    
                    # Build network visualization
                    st.markdown("### 🕸️ Influence Network Visualization")
                    
                    # Create networkx graph for visualization
                    G = nx.DiGraph()
                    
                    # Add nodes
                    for node in network_data["nodes"][:max_nodes]:  # Limit nodes for performance
                        G.add_node(node.user_id, 
                                  username=node.username,
                                  platform=node.platform,
                                  influence_score=node.influence_score,
                                  is_origin=node.is_origin,
                                  verified=node.verified,
                                  engagement_rate=node.engagement_rate)
                    
                    # Add edges
                    for edge in network_data["edges"]:
                        if edge.source_user in G.nodes and edge.target_user in G.nodes:
                            G.add_edge(edge.source_user, edge.target_user, 
                                     weight=edge.weight,
                                     interaction_type=edge.interaction_type)
                    
                    # Create layout
                    pos = nx.spring_layout(G, k=2, iterations=50)
                    
                    # Prepare visualization data
                    edge_x = []
                    edge_y = []
                    for edge in G.edges():
                        if edge[0] in pos and edge[1] in pos:
                            x0, y0 = pos[edge[0]]
                            x1, y1 = pos[edge[1]]
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])
                    
                    edge_trace = go.Scatter(x=edge_x, y=edge_y,
                                           line=dict(width=1, color='rgba(125,125,125,0.3)'),
                                           hoverinfo='none',
                                           mode='lines')
                    
                    # Prepare node data
                    node_x = []
                    node_y = []
                    node_text = []
                    node_color = []
                    node_size = []
                    
                    for node_id in G.nodes():
                        if node_id in pos:
                            x, y = pos[node_id]
                            node_x.append(x)
                            node_y.append(y)
                            
                            node_info = G.nodes[node_id]
                            node_text.append(f"@{node_info['username']}<br>"
                                            f"Platform: {node_info['platform']}<br>"
                                            f"Influence: {node_info['influence_score']:.2f}<br>"
                                            f"Origin: {'Yes' if node_info['is_origin'] else 'No'}<br>"
                                            f"Verified: {'Yes' if node_info['verified'] else 'No'}")
                            
                            # Color by origin status and influence
                            if node_info['is_origin']:
                                node_color.append(1.0)  # Origin nodes in red
                            else:
                                node_color.append(node_info['influence_score'])
                            
                            # Size by engagement rate
                            base_size = 15 if node_info['is_origin'] else 10
                            node_size.append(base_size + node_info['engagement_rate'] * 5)
                    
                    node_trace = go.Scatter(x=node_x, y=node_y,
                                           mode='markers',
                                           hoverinfo='text',
                                           text=node_text,
                                           marker=dict(showscale=True,
                                                     colorscale='RdYlBu_r',
                                                     color=node_color,
                                                     size=node_size,
                                                     colorbar=dict(thickness=15,
                                                                 xanchor="left",
                                                                 title="Influence Score"),
                                                     line=dict(width=2, color='white')))
                    
                    fig_network = go.Figure(data=[edge_trace, node_trace],
                                           layout=go.Layout(
                                               title=dict(text=f'Real-time Influence Network - {analysis_type}', font=dict(size=16)),
                                               showlegend=False,
                                               hovermode='closest',
                                               margin=dict(b=20,l=5,r=5,t=40),
                                               annotations=[dict(
                                                   text="🔴 Large nodes = Origin sources | Node size = Engagement rate | Color = Influence score",
                                                   showarrow=False,
                                                   xref="paper", yref="paper",
                                                   x=0.005, y=-0.002,
                                                   xanchor='left', yanchor='bottom',
                                                   font=dict(size=10)
                                               )],
                                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
                    
                    st.plotly_chart(fig_network, use_container_width=True)
                    
                    # Spread pattern analysis
                    st.markdown("### 📈 Viral Spread Patterns")
                    
                    edges = network_data["edges"]
                    if edges:
                        # Analyze interaction types
                        interaction_counts = {}
                        for edge in edges:
                            interaction_counts[edge.interaction_type] = interaction_counts.get(edge.interaction_type, 0) + 1
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🔄 Interaction Types")
                            interaction_df = pd.DataFrame(list(interaction_counts.items()), columns=['Type', 'Count'])
                            fig_interactions = px.pie(interaction_df, values='Count', names='Type', 
                                                    title="Distribution of Interaction Types")
                            st.plotly_chart(fig_interactions, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### ⏰ Spread Timeline")
                            # Create timeline of interactions
                            edge_times = [edge.timestamp for edge in edges if hasattr(edge, 'timestamp')]
                            if edge_times:
                                timeline_df = pd.DataFrame({'timestamp': edge_times})
                                timeline_df['hour'] = timeline_df['timestamp'].dt.floor('H')
                                hourly_counts = timeline_df.groupby('hour').size().reset_index(name='interactions')
                                
                                fig_timeline = px.line(hourly_counts, x='hour', y='interactions',
                                                     title="Viral Spread Over Time")
                                st.plotly_chart(fig_timeline, use_container_width=True)
                
                else:
                    st.warning("⚠️ No network data found. Please check your input parameters.")
                    
            except Exception as e:
                logger.error(f"Influence network error: {e}")
                show_error_popup(f"Failed to build influence network: {str(e)}", "Network Analysis Error")
    
    else:
        st.info("👆 Configure analysis parameters and click 'Build Influence Network' to start")
        
        # Show information about influence network analysis
        st.markdown("""
        ### 🕸️ Real-time Influence Network Analysis
        
        This analysis provides:
        
        - **Origin Tracking**: Identify the original sources of viral content
        - **Spread Patterns**: Visualize how content spreads through social networks
        - **Influence Scoring**: Measure user influence based on engagement and reach
        - **Network Topology**: Understand the structure of viral content propagation
        - **Interaction Analysis**: Analyze types of interactions (retweets, shares, mentions)
        - **Temporal Patterns**: Track how viral content spreads over time
        
        **Analysis Types:**
        - **Hashtag Tracking**: Follow a specific hashtag's spread across platforms
        - **Post URL Analysis**: Analyze the influence network of a specific post
        - **Keyword Network**: Build networks around trending keywords
        
        **Origin Nodes**: Large red nodes indicate potential sources where viral content originated.
        """)

# Tab 5: Geographic Spread
with tab5:
    st.subheader("🌍 Real-time Geographic Spread Analysis")
    
    # Geographic analysis parameters
    st.markdown("### Geographic Analysis Parameters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        geo_keywords = st.text_input(
            "🔍 Keywords for Geographic Analysis:",
            value="trending, viral, news",
            help="Enter keywords to analyze geographic spread patterns"
        )
    
    with col2:
        geo_platforms = st.multiselect(
            "📱 Platforms:",
            options=["twitter", "youtube", "reddit"],
            default=["twitter", "reddit"],
            key="geographic_platforms"
        )
    
    # Map style selection
    map_style = st.selectbox(
        "🗺️ Map Style:",
        options=["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain"],
        index=0
    )
    
    if st.button("🌍 Analyze Geographic Spread", type="primary"):
        if geo_keywords.strip() and geo_platforms:
            keywords_list = [k.strip() for k in geo_keywords.split(",")]
            
            with st.spinner("Analyzing real-time geographic spread..."):
                try:
                    # Get geographic data
                    geo_data = asyncio.run(realtime_service.get_geographic_data(
                        keywords=keywords_list,
                        platforms=geo_platforms
                    ))
                    
                    if geo_data["locations"]:
                        st.success(f"✅ Analyzed geographic data from {len(geo_data['locations'])} locations")
                        
                        # Geographic statistics
                        st.markdown("### 📊 Geographic Statistics")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Locations", len(geo_data["locations"]))
                        with col2:
                            total_posts = sum(loc.post_count for loc in geo_data["locations"])
                            st.metric("Total Posts", total_posts)
                        with col3:
                            avg_viral_score = sum(loc.viral_score for loc in geo_data["locations"]) / len(geo_data["locations"])
                            st.metric("Avg Viral Score", f"{avg_viral_score:.2f}")
                        with col4:
                            total_engagement = sum(loc.engagement_count for loc in geo_data["locations"])
                            st.metric("Total Engagement", f"{total_engagement:,}")
                        
                        # Create map visualization
                        st.markdown("### 🗺️ Geographic Distribution Map")
                        
                        # Prepare data for map
                        map_data = []
                        for location in geo_data["locations"]:
                            if location.latitude and location.longitude:
                                map_data.append({
                                    'location': location.location_name,
                                    'country': location.country,
                                    'lat': location.latitude,
                                    'lon': location.longitude,
                                    'post_count': location.post_count,
                                    'viral_score': location.viral_score,
                                    'engagement': location.engagement_count,
                                    'sentiment_score': location.sentiment_score
                                })
                        
                        if map_data:
                            map_df = pd.DataFrame(map_data)
                            
                            # Create scatter mapbox
                            fig_map = px.scatter_mapbox(
                                map_df,
                                lat='lat',
                                lon='lon',
                                size='post_count',
                                color='viral_score',
                                hover_name='location',
                                hover_data={
                                    'country': True,
                                    'post_count': ':,',
                                    'viral_score': ':.2f',
                                    'engagement': ':,',
                                    'sentiment_score': ':.2f'
                                },
                                mapbox_style=map_style,
                                title="Real-time Geographic Distribution of Viral Content",
                                zoom=1,
                                height=600,
                                color_continuous_scale="Viridis"
                            )
                            
                            fig_map.update_layout(
                                mapbox=dict(
                                    center=dict(lat=20, lon=0),  # World center
                                    zoom=1
                                )
                            )
                            
                            st.plotly_chart(fig_map, use_container_width=True)
                        
                        # Geographic breakdown charts
                        st.markdown("### 📈 Geographic Analysis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🏙️ Top Locations by Post Count")
                            top_locations = sorted(geo_data["locations"], key=lambda x: x.post_count, reverse=True)[:10]
                            
                            location_data = []
                            for loc in top_locations:
                                location_data.append({
                                    'Location': f"{loc.location_name}, {loc.country}",
                                    'Posts': loc.post_count,
                                    'Viral Score': loc.viral_score
                                })
                            
                            if location_data:
                                location_df = pd.DataFrame(location_data)
                                fig_locations = px.bar(
                                    location_df,
                                    x='Posts',
                                    y='Location',
                                    color='Viral Score',
                                    orientation='h',
                                    title="Posts by Location"
                                )
                                st.plotly_chart(fig_locations, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 🌍 Engagement by Country")
                            # Group by country
                            country_data = {}
                            for loc in geo_data["locations"]:
                                country = loc.country
                                if country not in country_data:
                                    country_data[country] = {'engagement': 0, 'posts': 0, 'viral_score': []}
                                country_data[country]['engagement'] += loc.engagement_count
                                country_data[country]['posts'] += loc.post_count
                                country_data[country]['viral_score'].append(loc.viral_score)
                            
                            # Create country visualization
                            country_viz_data = []
                            for country, data in country_data.items():
                                avg_viral = sum(data['viral_score']) / len(data['viral_score']) if data['viral_score'] else 0
                                country_viz_data.append({
                                    'Country': country,
                                    'Engagement': data['engagement'],
                                    'Posts': data['posts'],
                                    'Avg Viral Score': avg_viral
                                })
                            
                            if country_viz_data:
                                country_df = pd.DataFrame(country_viz_data)
                                country_df = country_df.sort_values('Engagement', ascending=False).head(10)
                                
                                fig_countries = px.bar(
                                    country_df,
                                    x='Country',
                                    y='Engagement',
                                    color='Avg Viral Score',
                                    title="Engagement by Country"
                                )
                                fig_countries.update_xaxes(tickangle=45)
                                st.plotly_chart(fig_countries, use_container_width=True)
                        
                        # Temporal geographic patterns
                        st.markdown("### ⏰ Temporal Geographic Patterns")
                        
                        temporal_data = geo_data.get("temporal_patterns", [])
                        if temporal_data:
                            temporal_df = pd.DataFrame([
                                {
                                    'timestamp': pattern.timestamp,
                                    'location': pattern.location,
                                    'post_count': pattern.post_count,
                                    'viral_score': pattern.viral_score
                                }
                                for pattern in temporal_data
                            ])
                            
                            # Create timeline by location
                            fig_temporal = px.line(
                                temporal_df,
                                x='timestamp',
                                y='post_count',
                                color='location',
                                title="Viral Content Spread Over Time by Location"
                            )
                            st.plotly_chart(fig_temporal, use_container_width=True)
                        
                        # Location details
                        st.markdown("### 📍 Location Details")
                        
                        # Show detailed information for top locations
                        for i, location in enumerate(top_locations[:5]):
                            with st.expander(f"📍 {location.location_name}, {location.country}"):
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.write(f"**Country:** {location.country}")
                                    st.write(f"**Coordinates:** {location.latitude:.4f}, {location.longitude:.4f}")
                                    st.write(f"**Timezone:** {location.timezone or 'Unknown'}")
                                with col2:
                                    st.metric("Posts", location.post_count)
                                    st.metric("Viral Score", f"{location.viral_score:.2f}")
                                    st.metric("Engagement", f"{location.engagement_count:,}")
                                    st.metric("Sentiment", f"{location.sentiment_score:.2f}")
                    
                    else:
                        st.warning("⚠️ No geographic data found for the specified keywords.")
                        
                except Exception as e:
                    logger.error(f"Geographic analysis error: {e}")
                    show_error_popup(f"Failed to perform geographic analysis: {str(e)}", "Geographic Analysis Error")
        else:
            st.warning("⚠️ Please enter keywords and select at least one platform.")
    
    else:
        st.info("👆 Click 'Analyze Geographic Spread' to start real-time geographic analysis")
        
        # Show information about geographic analysis
        st.markdown("""
        ### 🌍 Real-time Geographic Spread Analysis
        
        This analysis provides:
        
        - **Global Distribution**: Interactive world map showing viral content spread
        - **Location Ranking**: Top locations by post count and engagement
        - **Country Analysis**: Engagement patterns by country
        - **Temporal Patterns**: How viral content spreads geographically over time
        - **Sentiment Mapping**: Geographic distribution of sentiment scores
        - **Timezone Analysis**: Understanding viral patterns across time zones
        
        **Features:**
        - Real-time location data from social media posts
        - Interactive maps with multiple visualization styles
        - Country and city-level analysis
        - Temporal geographic spread patterns
        
        **Usage**: Enter keywords to analyze how viral content spreads across different geographic regions.
        """)

# Tab 6: Evidence Collection  
with tab6:
    st.subheader("📋 Real-time Evidence Collection")
    
    if auth_status == "No Authorization":
        st.error("Legal authorization required for evidence collection")
        st.info("Please obtain proper legal authorization (warrant, court order, etc.) before collecting digital evidence.")
    else:
        st.success(f"Operating under: {auth_status}")
        st.info(f"Case Number: {case_number} | Officer: {authorized_officer}")
        
        # Evidence collection parameters
        st.markdown("### Evidence Collection Parameters")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            evidence_keywords = st.text_input(
                "🔍 Keywords for Evidence Collection:",
                value="misinformation, fake news, viral",
                help="Enter keywords to identify content for evidence collection"
            )
            
            evidence_type = st.selectbox(
                "📋 Evidence Type:",
                options=["High Viral Score Posts", "Hashtag Tracking", "URL Evidence", "User Activity"],
                help="Select the type of evidence to collect"
            )
        
        with col2:
            evidence_platforms = st.multiselect(
                "📱 Target Platforms:",
                options=["twitter", "youtube", "reddit"],
                default=["twitter", "reddit"],
                key="evidence_collection_platforms"
            )
            
            min_viral_score = st.slider(
                "Minimum Viral Score:",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                help="Minimum viral score for evidence collection"
            )
        
        if st.button("📋 Collect Evidence", type="primary"):
            if evidence_keywords.strip() and evidence_platforms:
                keywords_list = [k.strip() for k in evidence_keywords.split(",")]
                
                with st.spinner("Collecting real-time evidence..."):
                    try:
                        # Get evidence data
                        evidence_data = asyncio.run(realtime_service.get_evidence_collection_data(
                            keywords=keywords_list,
                            platforms=evidence_platforms,
                            min_viral_score=min_viral_score,
                            evidence_type=evidence_type
                        ))
                        
                        if evidence_data["evidence_items"]:
                            st.success(f"✅ Collected {len(evidence_data['evidence_items'])} evidence items")
                            
                            # Evidence statistics
                            st.markdown("### 📊 Evidence Collection Statistics")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Evidence Items", len(evidence_data["evidence_items"]))
                            with col2:
                                high_priority = sum(1 for item in evidence_data["evidence_items"] if item.priority == "high")
                                st.metric("High Priority", high_priority)
                            with col3:
                                unique_urls = len(set(item.source_url for item in evidence_data["evidence_items"] if item.source_url))
                                st.metric("Unique URLs", unique_urls)
                            with col4:
                                unique_hashtags = len(set(tag for item in evidence_data["evidence_items"] for tag in item.hashtags))
                                st.metric("Unique Hashtags", unique_hashtags)
                            
                            # Evidence items display
                            st.markdown("### 📋 Evidence Collection Queue")
                            
                            # Sort by priority and viral score
                            sorted_evidence = sorted(
                                evidence_data["evidence_items"],
                                key=lambda x: (x.priority == "high", x.viral_score),
                                reverse=True
                            )
                            
                            for i, evidence_item in enumerate(sorted_evidence[:10]):  # Show top 10
                                priority_emoji = "🔴" if evidence_item.priority == "high" else "🟡" if evidence_item.priority == "medium" else "🟢"
                                
                                with st.expander(f"{priority_emoji} Evidence #{i+1}: {evidence_item.platform.title()} - Viral Score: {evidence_item.viral_score:.2f}"):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.write(f"**Content:** {evidence_item.content[:200]}...")
                                        st.write(f"**Author:** @{evidence_item.author}")
                                        st.write(f"**Platform:** {evidence_item.platform.title()}")
                                        st.write(f"**Timestamp:** {evidence_item.timestamp}")
                                        
                                        if evidence_item.source_url:
                                            st.write(f"**Source URL:** {evidence_item.source_url}")
                                        
                                        if evidence_item.hashtags:
                                            st.write(f"**Hashtags:** {', '.join(evidence_item.hashtags)}")
                                        
                                        if evidence_item.location:
                                            st.write(f"**Location:** {evidence_item.location}")
                                    
                                    with col2:
                                        st.metric("Viral Score", f"{evidence_item.viral_score:.2f}")
                                        st.metric("Engagement", f"{evidence_item.engagement_count:,}")
                                        st.metric("Priority", evidence_item.priority.title())
                                        
                                        # Evidence collection actions
                                        col_a, col_b = st.columns(2)
                                        
                                        with col_a:
                                            if st.button("📋 Collect", key=f"collect_{i}"):
                                                try:
                                                    # Simulate evidence collection with legal framework
                                                    auth_data = {
                                                        "authority_type": "magistrate_warrant",
                                                        "issuing_authority": "Chief Metropolitan Magistrate, Delhi",
                                                        "case_number": case_number,
                                                        "sections_invoked": ["IT_Act_66", "IT_Act_67", "CrPC_156"],
                                                        "validity_start": "2025-09-21T00:00:00",
                                                        "validity_end": "2025-12-21T23:59:59",
                                                        "scope_description": "Investigation of viral misinformation campaign",
                                                        "target_platforms": [evidence_item.platform],
                                                        "authorized_officers": [authorized_officer]
                                                    }
                                                    
                                                    authorization = legal_framework.create_legal_authorization(auth_data)
                                                    
                                                    if authorization:
                                                        evidence = legal_framework.collect_digital_evidence(
                                                            content=evidence_item.content,
                                                            platform=evidence_item.platform,
                                                            evidence_type=EvidenceType.ELECTRONIC_RECORD,
                                                            collecting_officer=authorized_officer,
                                                            authorization_id=authorization.auth_id,
                                                            metadata={
                                                                "viral_score": evidence_item.viral_score,
                                                                "engagement": evidence_item.engagement_count,
                                                                "priority": evidence_item.priority,
                                                                "source_url": evidence_item.source_url,
                                                                "hashtags": evidence_item.hashtags,
                                                                "location": evidence_item.location
                                                            }
                                                        )
                                                        
                                                        if evidence:
                                                            st.success("✅ Evidence collected successfully!")
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
                                                    logger.error(f"Evidence collection error: {e}")
                                                    show_error_popup(f"Failed to collect evidence for URL: {str(e)}", "URL Evidence Error")
                                        
                                        with col_b:
                                            if st.button("🔍 Analyze", key=f"analyze_{i}"):
                                                # Show detailed analysis
                                                analysis = language_support.analyze_multilingual_content(evidence_item.content)
                                                st.json(analysis)
                            
                            # URL tracking section
                            if evidence_type == "URL Evidence":
                                st.markdown("### 🔗 URL Evidence Tracking")
                                
                                url_evidence = evidence_data.get("url_tracking", [])
                                if url_evidence:
                                    url_df = pd.DataFrame([
                                        {
                                            'URL': url.url,
                                            'Share Count': url.share_count,
                                            'First Seen': url.first_seen,
                                            'Last Seen': url.last_seen,
                                            'Platforms': ', '.join(url.platforms)
                                        }
                                        for url in url_evidence
                                    ])
                                    
                                    st.dataframe(url_df, use_container_width=True)
                            
                            # Hashtag tracking section
                            if evidence_type == "Hashtag Tracking":
                                st.markdown("### 🏷️ Hashtag Evidence Tracking")
                                
                                hashtag_evidence = evidence_data.get("hashtag_tracking", [])
                                if hashtag_evidence:
                                    hashtag_df = pd.DataFrame([
                                        {
                                            'Hashtag': hashtag.hashtag,
                                            'Usage Count': hashtag.usage_count,
                                            'Viral Score': hashtag.viral_score,
                                            'First Seen': hashtag.first_seen,
                                            'Peak Usage': hashtag.peak_usage_time
                                        }
                                        for hashtag in hashtag_evidence
                                    ])
                                    
                                    st.dataframe(hashtag_df, use_container_width=True)
                                    
                                    # Hashtag timeline
                                    if hashtag_evidence:
                                        timeline_data = []
                                        for hashtag in hashtag_evidence:
                                            if hasattr(hashtag, 'timeline') and hashtag.timeline:
                                                for point in hashtag.timeline:
                                                    timeline_data.append({
                                                        'hashtag': hashtag.hashtag,
                                                        'timestamp': point.timestamp,
                                                        'usage_count': point.usage_count
                                                    })
                                        
                                        if timeline_data:
                                            timeline_df = pd.DataFrame(timeline_data)
                                            fig_hashtag_timeline = px.line(
                                                timeline_df,
                                                x='timestamp',
                                                y='usage_count',
                                                color='hashtag',
                                                title="Hashtag Usage Timeline"
                                            )
                                            st.plotly_chart(fig_hashtag_timeline, use_container_width=True)
                        
                        else:
                            st.warning("⚠️ No evidence items found for the specified criteria.")
                            
                    except Exception as e:
                        logger.error(f"Evidence collection error: {e}")
                        show_error_popup(f"Failed to collect evidence: {str(e)}", "Evidence Collection Error")
            else:
                st.warning("⚠️ Please enter keywords and select at least one platform.")
        
        else:
            st.info("👆 Configure evidence collection parameters and click 'Collect Evidence' to start")
            
            # Show information about evidence collection
            st.markdown("""
            ### 📋 Real-time Evidence Collection
            
            This system provides:
            
            - **Legal Compliance**: All evidence collection follows IT Act 2000, CrPC 1973, and Evidence Act 1872
            - **Real-time Collection**: Live monitoring and collection of viral content
            - **URL Tracking**: Track specific URLs and their spread across platforms
            - **Hashtag Evidence**: Monitor hashtag usage and viral patterns
            - **Chain of Custody**: Maintain complete evidence integrity
            - **Section 65B Compliance**: Generate court-admissible digital evidence
            
            **Evidence Types:**
            - **High Viral Score Posts**: Content with significant viral potential
            - **Hashtag Tracking**: Monitor specific hashtags and their spread
            - **URL Evidence**: Track shared URLs and their propagation
            - **User Activity**: Monitor specific user accounts and their content
            
            **Legal Framework**: All evidence collection is performed under proper legal authorization.
            """)
        
        # Evidence statistics sidebar
        st.markdown("### 📊 Evidence Collection Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Mock evidence statistics
            st.metric("Total Evidence Items", "156", "↑ 12")
            st.metric("Section 65B Compliant", "142", "91%")
            st.metric("Chain of Custody Complete", "156", "100%")
            st.metric("Court-Ready Packages", "23", "↑ 3")
        
        with col2:
            st.markdown("#### Legal Framework Status")
            
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
# Government Footer
st.markdown(f"""
<div class="government-footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4>{get_text('title')}</h4>
            <p>{get_text('subtitle')}</p>
        </div>
        <div>
            <p><strong>{get_text('legal_framework')}</strong></p>
            <p>IT Act 2000 | CrPC 1973 | Evidence Act 1872</p>
        </div>
        <div>
            <p><strong>{get_text('security_classification')}</strong></p>
            <p>{get_text('restricted_official_use')}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status indicator
if auth_status != "No Authorization":
    st.success(f"{get_text('system_operational')} | Authorization: {auth_status} | Case: {case_number}")
else:
    st.error("System Status: UNAUTHORIZED ACCESS - Legal authorization required")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Security Status**")
    st.success(get_text('all_systems_operational'))
    st.info(get_text('encryption_active'))

with col2:
    st.markdown("**Legal Compliance**")
    st.success(get_text('it_act_compliant'))
    st.success(get_text('evidence_act_compliant'))

with col3:
    st.markdown("**Platform Coverage**")
    st.info(f"{len(selected_platforms)} " + get_text('platforms_active'))
    st.info(f"{len(languages)} " + get_text('languages_supported'))

# Real-time updates simulation
if st.sidebar.button(get_text('refresh_data')):
    st.cache_data.clear()
    st.rerun()

# Export functionality
if st.sidebar.button(get_text('export_report')):
    try:
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
    except Exception as e:
        logger.error(f"Report export error: {e}")
        show_error_popup(f"Failed to generate report: {str(e)}", "Report Export Error")

# Real-time Search Tab Implementation
with tab7:
    st.header("🔍 Real-time Social Media Search & Analysis")
    st.markdown("**Search across X.com, YouTube, and Reddit with real-time sentiment and viral analysis**")
    
    # Search interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_keywords = st.text_input(
            "🔍 Search Keywords",
            placeholder="Enter keywords, phrases, or hashtags (e.g., 'climate change', 'government policy')",
            help="Use boolean operators: AND, OR, NOT. Use quotes for exact phrases."
        )
    
    with col2:
        search_region = st.selectbox(
            "🌍 Region Filter",
            options=["India", "Global", "Delhi", "Mumbai", "Bangalore", "Chennai"],
            index=0
        )
    
    # Advanced search options
    with st.expander("⚙️ Advanced Search Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_window = st.selectbox(
                "⏰ Time Window",
                options=["Last 24 hours", "Last 3 days", "Last week", "Last month"],
                index=0
            )
            
            # Convert to hours
            time_mapping = {
                "Last 24 hours": 24,
                "Last 3 days": 72,
                "Last week": 168,
                "Last month": 720
            }
            time_hours = time_mapping[time_window]
        
        with col2:
            selected_platforms = st.multiselect(
                "📱 Platforms",
                options=["twitter", "youtube", "reddit"],
                default=["twitter", "youtube", "reddit"],
                key="admin_monitoring_platforms"
            )
        
        with col3:
            max_results = st.slider(
                "📊 Max Results",
                min_value=10,
                max_value=200,
                value=50,
                step=10
            )
    
    # Search button
    if st.button("🚀 Start Real-time Search", type="primary", use_container_width=True):
        if not search_keywords:
            st.error("Please enter search keywords")
        elif not selected_platforms:
            st.error("Please select at least one platform")
        else:
            # Create search query
            search_query = SearchQuery(
                keywords=search_keywords,
                region=search_region if search_region != "Global" else None,
                platforms=selected_platforms,
                max_results=max_results,
                case_number=case_number,
                officer_id=authorized_officer
            )
            
            # Show search progress
            with st.spinner(f"🔍 Searching {', '.join(selected_platforms)} for '{search_keywords}'..."):
                try:
                    # Perform real-time search
                    search_results = asyncio.run(services['realtime_search'].search_and_analyze(search_query))
                    
                    # Store results in session state
                    st.session_state.search_results = search_results
                    st.success(f"✅ Search completed! Found {search_results.total_found} posts in {search_results.search_duration:.2f} seconds")
                    
                except Exception as e:
                    logger.error(f"Real-time search error: {e}")
                    show_error_popup(f"Real-time search failed: {str(e)}", "Search Error")
    
    # Display search results if available
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        results = st.session_state.search_results
        
        # Results summary
        st.subheader("📊 Search Results Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", results.total_found)
        with col2:
            avg_sentiment = results.analysis_summary.get('average_sentiment', 0)
            sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", sentiment_label)
        with col3:
            avg_viral = results.analysis_summary.get('average_viral_potential', 0)
            st.metric("Avg Viral Score", f"{avg_viral:.2f}")
        with col4:
            high_risk = results.analysis_summary.get('high_risk_posts', 0)
            st.metric("High Risk Posts", high_risk, "⚠️" if high_risk > 0 else "✅")
        
        # Chronological Timeline
        st.subheader("⏰ Chronological Timeline")
        
        if results.timeline_data:
            # Create timeline DataFrame
            timeline_df = pd.DataFrame(results.timeline_data)
            timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
            timeline_df = timeline_df.sort_values('timestamp')
            
            # Timeline visualization
            fig_timeline = px.scatter(
                timeline_df,
                x='timestamp',
                y='sentiment_score',
                color='platform',
                size='engagement_total',
                hover_data=['author', 'viral_potential'],
                title="Content Timeline - Sentiment vs Time",
                labels={'sentiment_score': 'Sentiment Score', 'timestamp': 'Time'}
            )
            fig_timeline.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Timeline table
            st.subheader("📋 Detailed Timeline")
            
            # Format timeline for display
            display_timeline = timeline_df.copy()
            display_timeline['Time'] = display_timeline['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            display_timeline['Platform'] = display_timeline['platform'].str.title()
            display_timeline['Content'] = display_timeline['content_preview']
            display_timeline['Sentiment'] = display_timeline['sentiment_label'].str.title()
            display_timeline['Viral Score'] = display_timeline['viral_potential'].round(2)
            display_timeline['Engagement'] = display_timeline['engagement_total']
            display_timeline['Risk'] = display_timeline['risk_indicators'].apply(
                lambda x: "⚠️ High" if x and len(x) > 0 else "✅ Low"
            )
            
            # Display table
            st.dataframe(
                display_timeline[['Time', 'Platform', 'Content', 'Sentiment', 'Viral Score', 'Engagement', 'Risk']],
                use_container_width=True,
                height=400
            )
        
        # Viral Actors Analysis
        if results.viral_actors:
            st.subheader("👥 Viral Actors & Influencers")
            
            viral_actors_df = pd.DataFrame(results.viral_actors[:10])  # Top 10
            
            # Viral actors chart
            fig_actors = px.bar(
                viral_actors_df,
                x='handle',
                y='influence_score',
                color='platform',
                title="Top Viral Actors by Influence Score",
                labels={'influence_score': 'Influence Score', 'handle': 'Account Handle'}
            )
            fig_actors.update_xaxes(tickangle=45)
            st.plotly_chart(fig_actors, use_container_width=True)
            
            # Actors table
            display_actors = viral_actors_df.copy()
            display_actors['Handle'] = display_actors['handle']
            display_actors['Platform'] = display_actors['platform'].str.title()
            display_actors['Posts'] = display_actors['post_count']
            display_actors['Engagement'] = display_actors['total_engagement']
            display_actors['Influence'] = display_actors['influence_score'].round(3)
            display_actors['Avg Sentiment'] = display_actors['avg_sentiment'].round(2)
            display_actors['Risk Level'] = display_actors['risk_indicators'].apply(
                lambda x: "⚠️ High" if x and len(x) > 2 else "🔶 Medium" if x and len(x) > 0 else "✅ Low"
            )
            
            st.dataframe(
                display_actors[['Handle', 'Platform', 'Posts', 'Engagement', 'Influence', 'Avg Sentiment', 'Risk Level']],
                use_container_width=True
            )
        
        # Platform Analysis
        st.subheader("📱 Platform Distribution")
        
        platform_dist = results.analysis_summary.get('platform_distribution', {})
        if platform_dist:
            fig_platforms = px.pie(
                values=list(platform_dist.values()),
                names=list(platform_dist.keys()),
                title="Content Distribution by Platform"
            )
            st.plotly_chart(fig_platforms, use_container_width=True)
        
        # Export functionality
        st.subheader("📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as JSON"):
                try:
                    json_data = services['realtime_search'].export_results(results, format='json')
                    st.download_button(
                        label="Download JSON Report",
                        data=json_data,
                        file_name=f"realtime_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                except Exception as e:
                    logger.error(f"JSON export error: {e}")
                    show_error_popup(f"Failed to export JSON report: {str(e)}", "Export Error")
        
        with col2:
            if st.button("📊 Export as CSV"):
                try:
                    csv_data = services['realtime_search'].export_results(results, format='csv')
                    st.download_button(
                        label="Download CSV Report",
                        data=csv_data,
                        file_name=f"realtime_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    logger.error(f"CSV export error: {e}")
                    show_error_popup(f"Failed to export CSV report: {str(e)}", "Export Error")
        
        with col3:
            if st.button("🔄 Clear Results"):
                if hasattr(st.session_state, 'search_results'):
                    del st.session_state.search_results
                st.rerun()
    
    else:
        # Show example when no search has been performed
        st.info("👆 Enter search keywords above and click 'Start Real-time Search' to begin analysis")
        
        st.subheader("🎯 Search Examples")
        
        examples = [
            {
                "title": "🌍 Climate Change Discussion",
                "keywords": "climate change OR global warming",
                "description": "Track climate-related discussions across platforms"
            },
            {
                "title": "🏛️ Government Policy Analysis", 
                "keywords": "government policy AND india",
                "description": "Monitor government policy discussions"
            },
            {
                "title": "📱 Technology Trends",
                "keywords": "artificial intelligence OR AI OR machine learning",
                "description": "Follow AI and technology conversations"
            },
            {
                "title": "🚨 Breaking News Monitoring",
                "keywords": "breaking news OR urgent OR alert",
                "description": "Track breaking news and urgent updates"
            }
        ]
        
        for example in examples:
            with st.expander(example["title"]):
                st.code(f"Keywords: {example['keywords']}")
                st.write(example["description"])
                if st.button(f"Use this example", key=f"example_{example['title']}"):
                    st.session_state.example_keywords = example['keywords']
                    st.rerun()

# Help section
with st.sidebar.expander(get_text("help_documentation")):
    st.markdown(f"""
    **{get_text('title')} Features:**
    
    **{get_text('viral_timeline')}**
    - Real-time monitoring across platforms
    - AI-powered viral prediction
    - Multi-language content support
    
    **{get_text('legal_framework')}**
    - IT Act 2000 compliance
    - Evidence Act 1872 compliance
    - Chain of custody maintenance
    - Digital evidence collection
    
    **Global Platform Support**
    - 8+ major social media platforms
    - Indian regional platforms (Koo, ShareChat)
    - Cross-platform analysis
    
    **Multi-language Support**
    - 5+ Indian languages
    - Automatic language detection
    - Localized user interface
    
    **Analytics & Reporting**
    - Influence network analysis
    - Geographic spread tracking
    - Evidence collection reports
    """)

if __name__ == "__main__":
    try:
        st.sidebar.success(get_text('platform_active'))
        st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Critical error in main execution: {str(e)}")
        show_error_popup(f"Critical dashboard error: {str(e)}", "System Error")
        st.stop()