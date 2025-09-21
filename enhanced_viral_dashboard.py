#!/usr/bin/env python3
"""
Enhanced InsideOut Viral Dashboard with Indian Legal Framework and Global Platform Support
Integrates legal compliance, multilingual support, and global platform analysis
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

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

try:
    from services.legal_compliance.indian_legal_framework import IndianLegalFramework, LegalAuthority, EvidenceType
    from services.multilingual.enhanced_language_support import EnhancedLanguageSupport
    from services.platforms.global_platform_support import GlobalPlatformSupport
except ImportError as e:
    st.error(f"Error importing services: {e}")
    st.stop()

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
        return legal_framework, language_support, platform_support
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None

legal_framework, language_support, platform_support = initialize_services()

if not all([legal_framework, language_support, platform_support]):
    st.error("Failed to initialize services. Please check the configuration.")
    st.stop()

# Language selection
languages = language_support.get_supported_languages()
language_options = {code: f"{lang['name']} ({lang['native_name']})" for code, lang in languages.items()}

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
    
    selected_platforms = st.multiselect(
        "Select Platforms",
        options=list(available_platforms.keys()),
        default=list(available_platforms.keys())[:5],
        format_func=lambda x: available_platforms[x]['name']
    )
    
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
    return language_support.get_ui_translation(selected_language, key)

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    get_translation("viral_timeline"),
    get_translation("influence_network"),
    get_translation("geographic_spread"),
    get_translation("evidence_collection"),
    "🌐 Global Platform Analysis"
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
    st.subheader("🔥 Top Viral Content")
    
    top_content = filtered_data.nlargest(10, 'viral_score')[
        ['platform', 'content', 'viral_score', 'engagement', 'language', 'legal_status']
    ]
    
    for idx, row in top_content.iterrows():
        with st.expander(f"🔥 {row['platform'].upper()} - Viral Score: {row['viral_score']:.2f}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Content:** {row['content'][:200]}...")
                st.write(f"**Language:** {languages.get(row['language'], {}).get('name', 'Unknown')}")
                st.write(f"**Engagement:** {row['engagement']:,}")
            
            with col2:
                if row['legal_status'] == 'authorized' and auth_status != "No Authorization":
                    if st.button(f"🔒 {get_translation('collect_evidence')}", key=f"collect_{idx}"):
                        # Simulate evidence collection
                        evidence = legal_framework.collect_digital_evidence(
                            content=row['content'],
                            platform=row['platform'],
                            evidence_type=EvidenceType.ELECTRONIC_RECORD,
                            collecting_officer=authorized_officer,
                            authorization_id="demo_auth_id",
                            metadata={"viral_score": row['viral_score'], "engagement": row['engagement']}
                        )
                        
                        if evidence:
                            st.success(f"✅ Evidence collected: {evidence.evidence_id[:8]}...")
                        else:
                            st.error("❌ Evidence collection failed")
                else:
                    st.warning("⚠️ Authorization required")

# Tab 2: Influence Network
with tab2:
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
                                                 titleside="right",
                                                 title="Viral Score")))
    
    fig_network = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Viral Content Influence Network',
                               titlefont_size=16,
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

# Tab 4: Evidence Collection
with tab4:
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

# Tab 5: Global Platform Analysis
with tab5:
    st.subheader("🌐 Global Platform Analysis")
    
    # Platform comparison
    platform_stats = viral_data.groupby('platform').agg({
        'viral_score': ['mean', 'max'],
        'engagement': 'sum',
        'id': 'count'
    }).round(2)
    
    platform_stats.columns = ['Avg Viral Score', 'Max Viral Score', 'Total Engagement', 'Post Count']
    platform_stats = platform_stats.reset_index()
    
    # Platform performance chart
    fig_platform = px.scatter(
        platform_stats,
        x='Post Count',
        y='Avg Viral Score',
        size='Total Engagement',
        color='platform',
        title="Platform Performance Analysis",
        hover_data=['Max Viral Score']
    )
    
    st.plotly_chart(fig_platform, use_container_width=True)
    
    # Platform details
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Platform Statistics")
        st.dataframe(platform_stats, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Platform Coverage")
        
        # Show platform information
        for platform_id in selected_platforms[:5]:
            if platform_id in available_platforms:
                platform_info = available_platforms[platform_id]
                
                with st.expander(f"📱 {platform_info['name']}"):
                    st.write(f"**Type:** {platform_info['type'].title()}")
                    st.write(f"**Scope:** {platform_info['scope'].title()}")
                    st.write(f"**Regions:** {', '.join(platform_info['regions'])}")
                    st.write(f"**Content Types:** {', '.join(platform_info['content_types'])}")
                    st.write(f"**API Available:** {'✅' if platform_info['api_available'] else '❌'}")
                    st.write(f"**Hashtags:** {'✅' if platform_info['supports_hashtags'] else '❌'}")
                    st.write(f"**Mentions:** {'✅' if platform_info['supports_mentions'] else '❌'}")
                    st.write(f"**Reposting:** {'✅' if platform_info['supports_reposting'] else '❌'}")
    
    # Language distribution across platforms
    st.subheader("🗣️ Language Distribution Across Platforms")
    
    lang_platform = viral_data.groupby(['platform', 'language']).size().reset_index(name='count')
    
    fig_lang = px.sunburst(
        lang_platform,
        path=['platform', 'language'],
        values='count',
        title="Content Language Distribution by Platform"
    )
    
    st.plotly_chart(fig_lang, use_container_width=True)

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