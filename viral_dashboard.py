#!/usr/bin/env python3
"""
InsideOut Viral Dashboard - Interactive Demo
Demonstrates viral content detection and influence mapping capabilities
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
import random
from typing import List, Dict, Any
import requests
import time

# Configure Streamlit page
st.set_page_config(
    page_title="InsideOut - Viral Content Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Indian Government theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6600 0%, #FFFFFF 50%, #138808 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6600;
    }
    .priority-high {
        border-left-color: #FF4444 !important;
    }
    .priority-medium {
        border-left-color: #FFAA00 !important;
    }
    .priority-low {
        border-left-color: #44AA44 !important;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Language support
LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'bn': 'বাংলা'
}

TRANSLATIONS = {
    'en': {
        'title': 'InsideOut - Viral Content Analysis Platform',
        'subtitle': 'Government of India | भारत सरकार',
        'viral_clusters': 'Active Viral Clusters',
        'evidence_packages': 'Evidence Packages',
        'high_priority': 'High Priority Cases',
        'officers_active': 'Officers Active',
        'search_placeholder': 'Enter keywords to search viral content...',
        'platform_filter': 'Platform Filter',
        'time_range': 'Time Range',
        'location_filter': 'Location Filter',
        'viral_timeline': 'Viral Content Timeline',
        'influence_network': 'Influence Network Analysis',
        'geographic_spread': 'Geographic Spread',
        'evidence_collection': 'Evidence Collection Status',
        'original_source': 'Original Source',
        'viral_score': 'Viral Score',
        'propagation_chain': 'Propagation Chain',
        'collect_evidence': 'Collect Evidence',
        'view_details': 'View Details'
    },
    'hi': {
        'title': 'इनसाइडआउट - वायरल सामग्री विश्लेषण प्लेटफॉर्म',
        'subtitle': 'भारत सरकार | Government of India',
        'viral_clusters': 'सक्रिय वायरल क्लस्टर',
        'evidence_packages': 'साक्ष्य पैकेज',
        'high_priority': 'उच्च प्राथमिकता मामले',
        'officers_active': 'सक्रिय अधिकारी',
        'search_placeholder': 'वायरल सामग्री खोजने के लिए कीवर्ड दर्ज करें...',
        'platform_filter': 'प्लेटफॉर्म फिल्टर',
        'time_range': 'समय सीमा',
        'location_filter': 'स्थान फिल्टर',
        'viral_timeline': 'वायरल सामग्री समयरेखा',
        'influence_network': 'प्रभाव नेटवर्क विश्लेषण',
        'geographic_spread': 'भौगोलिक प्रसार',
        'evidence_collection': 'साक्ष्य संग्रह स्थिति',
        'original_source': 'मूल स्रोत',
        'viral_score': 'वायरल स्कोर',
        'propagation_chain': 'प्रसार श्रृंखला',
        'collect_evidence': 'साक्ष्य एकत्रित करें',
        'view_details': 'विवरण देखें'
    }
}

class ViralAnalysisDemo:
    def __init__(self):
        self.mock_data = self.generate_mock_data()
        
    def generate_mock_data(self):
        """Generate realistic mock data for demonstration"""
        
        # Mock viral clusters
        viral_clusters = []
        platforms = ['Twitter', 'Facebook', 'Instagram', 'YouTube', 'WhatsApp']
        priorities = ['high', 'medium', 'low']
        
        for i in range(50):
            cluster = {
                'id': f'cluster_{i+1}',
                'content': self.generate_mock_content(),
                'original_source': f'@user_{random.randint(1000, 9999)}',
                'viral_score': round(random.uniform(1.0, 10.0), 1),
                'propagation_count': random.randint(100, 50000),
                'platforms': random.sample(platforms, random.randint(1, 3)),
                'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
                'priority': random.choice(priorities),
                'evidence_collected': random.choice([True, False]),
                'geographic_spread': self.generate_geographic_data(),
                'influence_network': self.generate_influence_network()
            }
            viral_clusters.append(cluster)
        
        return {
            'viral_clusters': viral_clusters,
            'indian_states': self.get_indian_states_data()
        }
    
    def generate_mock_content(self):
        """Generate realistic mock content"""
        content_templates = [
            "Breaking: Major political announcement creates social media storm",
            "Viral video of traffic incident spreads across platforms",
            "Misinformation about government policy circulating",
            "Celebrity controversy triggers massive online debate",
            "Natural disaster footage goes viral, authorities verify authenticity",
            "Educational content about digital literacy gains traction",
            "Fake news about economic policy debunked by fact-checkers",
            "Cultural festival celebration video spreads joy online",
            "Technology innovation announcement creates buzz",
            "Sports victory celebration unites the nation online"
        ]
        return random.choice(content_templates)
    
    def generate_geographic_data(self):
        """Generate mock geographic spread data"""
        states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal', 
                 'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh', 'Kerala']
        
        spread_data = {}
        num_states = random.randint(1, 5)
        selected_states = random.sample(states, num_states)
        
        for state in selected_states:
            spread_data[state] = {
                'post_count': random.randint(10, 1000),
                'influence_score': round(random.uniform(1.0, 10.0), 1)
            }
        
        return spread_data
    
    def generate_influence_network(self):
        """Generate mock influence network data"""
        return {
            'total_nodes': random.randint(50, 500),
            'total_edges': random.randint(100, 1000),
            'key_influencers': [
                {
                    'user_id': f'@influencer_{i}',
                    'follower_count': random.randint(10000, 1000000),
                    'influence_score': round(random.uniform(5.0, 10.0), 1)
                }
                for i in range(5)
            ]
        }
    
    def get_indian_states_data(self):
        """Get Indian states data for mapping"""
        return {
            'Delhi': {'lat': 28.6139, 'lng': 77.2090, 'population': 32941000},
            'Maharashtra': {'lat': 19.0760, 'lng': 72.8777, 'population': 112374333},
            'Karnataka': {'lat': 12.9716, 'lng': 77.5946, 'population': 61095297},
            'Tamil Nadu': {'lat': 13.0827, 'lng': 80.2707, 'population': 72147030},
            'West Bengal': {'lat': 22.5726, 'lng': 88.3639, 'population': 91276115},
            'Gujarat': {'lat': 23.0225, 'lng': 72.5714, 'population': 60439692},
            'Rajasthan': {'lat': 26.9124, 'lng': 75.7873, 'population': 68548437},
            'Uttar Pradesh': {'lat': 26.8467, 'lng': 80.9462, 'population': 199812341},
            'Madhya Pradesh': {'lat': 23.2599, 'lng': 77.4126, 'population': 72626809},
            'Kerala': {'lat': 10.8505, 'lng': 76.2711, 'population': 33406061}
        }

def main():
    # Initialize demo
    demo = ViralAnalysisDemo()
    
    # Sidebar for language and filters
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/200px-Emblem_of_India.svg.png", width=100)
        
        # Language selection
        selected_lang = st.selectbox("Language / भाषा", list(LANGUAGES.keys()), 
                                   format_func=lambda x: LANGUAGES[x])
        
        t = TRANSLATIONS.get(selected_lang, TRANSLATIONS['en'])
        
        st.markdown("---")
        
        # Filters
        st.subheader("Filters")
        
        search_query = st.text_input(t['search_placeholder'])
        
        platform_filter = st.multiselect(
            t['platform_filter'],
            ['All', 'Twitter', 'Facebook', 'Instagram', 'YouTube', 'WhatsApp'],
            default=['All']
        )
        
        time_range = st.selectbox(
            t['time_range'],
            ['Last 24 Hours', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days']
        )
        
        location_filter = st.selectbox(
            t['location_filter'],
            ['All India', 'Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal']
        )
        
        priority_filter = st.multiselect(
            "Priority Level",
            ['High', 'Medium', 'Low'],
            default=['High', 'Medium', 'Low']
        )
    
    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>{t['title']}</h1>
        <p>{t['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=t['viral_clusters'],
            value="1,247",
            delta="↑ 23 from yesterday"
        )
    
    with col2:
        st.metric(
            label=t['evidence_packages'],
            value="89",
            delta="↑ 5 from yesterday"
        )
    
    with col3:
        st.metric(
            label=t['high_priority'],
            value="23",
            delta="↓ 2 from yesterday"
        )
    
    with col4:
        st.metric(
            label=t['officers_active'],
            value="156",
            delta="↑ 8 from yesterday"
        )
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs([
        t['viral_timeline'], 
        t['influence_network'], 
        t['geographic_spread'], 
        t['evidence_collection']
    ])
    
    with tab1:
        st.subheader(t['viral_timeline'])
        
        # Filter data based on selections
        filtered_clusters = demo.mock_data['viral_clusters']
        
        if search_query:
            filtered_clusters = [c for c in filtered_clusters if search_query.lower() in c['content'].lower()]
        
        if 'All' not in platform_filter:
            filtered_clusters = [c for c in filtered_clusters if any(p in c['platforms'] for p in platform_filter)]
        
        priority_map = {'High': 'high', 'Medium': 'medium', 'Low': 'low'}
        selected_priorities = [priority_map[p] for p in priority_filter]
        filtered_clusters = [c for c in filtered_clusters if c['priority'] in selected_priorities]
        
        # Display viral content timeline
        for cluster in filtered_clusters[:10]:  # Show top 10
            priority_class = f"priority-{cluster['priority']}"
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card {priority_class}">
                        <h4>{cluster['content']}</h4>
                        <p><strong>{t['original_source']}:</strong> {cluster['original_source']}</p>
                        <p><strong>{t['viral_score']}:</strong> {cluster['viral_score']}/10 | 
                           <strong>{t['propagation_chain']}:</strong> {cluster['propagation_count']:,}</p>
                        <p><strong>Platforms:</strong> {', '.join(cluster['platforms'])}</p>
                        <p><strong>Time:</strong> {cluster['timestamp'].strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(t['collect_evidence'], key=f"collect_{cluster['id']}"):
                        st.success("Evidence collection initiated!")
                
                with col3:
                    if st.button(t['view_details'], key=f"details_{cluster['id']}"):
                        st.info("Detailed analysis view opened")
                
                st.markdown("---")
    
    with tab2:
        st.subheader(t['influence_network'])
        
        # Create network visualization
        G = nx.random_geometric_graph(50, 0.3)
        pos = nx.spring_layout(G)
        
        # Extract node and edge data
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create network plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=[f'User {i}' for i in range(len(node_x))],
            marker=dict(
                showscale=True,
                colorscale='YlOrRd',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    len=0.5,
                    x=0.9,
                    title="Influence Score"
                ),
                line_width=2
            )
        ))
        
        fig.update_layout(
            title="Influence Network Graph",
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Network shows user interactions and influence propagation",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#888', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key influencers table
        st.subheader("Key Influencers")
        
        influencer_data = []
        for cluster in demo.mock_data['viral_clusters'][:5]:
            for influencer in cluster['influence_network']['key_influencers'][:1]:
                influencer_data.append({
                    'User': influencer['user_id'],
                    'Followers': f"{influencer['follower_count']:,}",
                    'Influence Score': influencer['influence_score'],
                    'Content': cluster['content'][:50] + "..."
                })
        
        st.dataframe(pd.DataFrame(influencer_data), use_container_width=True)
    
    with tab3:
        st.subheader(t['geographic_spread'])
        
        # Create India map visualization
        state_data = []
        for cluster in demo.mock_data['viral_clusters']:
            for state, data in cluster['geographic_spread'].items():
                if state in demo.mock_data['indian_states']:
                    state_info = demo.mock_data['indian_states'][state]
                    state_data.append({
                        'State': state,
                        'Latitude': state_info['lat'],
                        'Longitude': state_info['lng'],
                        'Viral Posts': data['post_count'],
                        'Influence Score': data['influence_score']
                    })
        
        if state_data:
            df_states = pd.DataFrame(state_data)
            df_states = df_states.groupby('State').agg({
                'Latitude': 'first',
                'Longitude': 'first',
                'Viral Posts': 'sum',
                'Influence Score': 'mean'
            }).reset_index()
            
            # Create map
            fig = px.scatter_mapbox(
                df_states,
                lat="Latitude",
                lon="Longitude",
                size="Viral Posts",
                color="Influence Score",
                hover_name="State",
                hover_data={"Viral Posts": True, "Influence Score": ":.1f"},
                color_continuous_scale="Reds",
                size_max=50,
                zoom=4,
                center={"lat": 20.5937, "lon": 78.9629},
                mapbox_style="open-street-map",
                title="Geographic Distribution of Viral Content"
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # State-wise statistics
            st.subheader("State-wise Statistics")
            st.dataframe(df_states.sort_values('Viral Posts', ascending=False), use_container_width=True)
    
    with tab4:
        st.subheader(t['evidence_collection'])
        
        # Evidence collection status
        col1, col2 = st.columns(2)
        
        with col1:
            # Evidence collection pie chart
            evidence_status = {
                'Collected': 45,
                'Pending Warrant': 23,
                'In Progress': 12,
                'Analyzed': 9
            }
            
            fig = px.pie(
                values=list(evidence_status.values()),
                names=list(evidence_status.keys()),
                title="Evidence Collection Status"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Recent evidence collections
            st.subheader("Recent Evidence Collections")
            
            evidence_data = [
                {
                    'Collection ID': 'EC-20240115-001',
                    'Case Number': 'FIR-2024-001',
                    'Officer': 'Inspector Sharma',
                    'Items': 15,
                    'Status': 'Collected'
                },
                {
                    'Collection ID': 'EC-20240114-002',
                    'Case Number': 'FIR-2024-002',
                    'Officer': 'Sub-Inspector Patel',
                    'Items': 8,
                    'Status': 'Analyzed'
                },
                {
                    'Collection ID': 'EC-20240113-003',
                    'Case Number': 'FIR-2024-003',
                    'Officer': 'Inspector Kumar',
                    'Items': 23,
                    'Status': 'In Progress'
                }
            ]
            
            st.dataframe(pd.DataFrame(evidence_data), use_container_width=True)
        
        # Chain of custody verification
        st.subheader("Chain of Custody Verification")
        
        if st.button("Verify Evidence Integrity"):
            with st.spinner("Verifying blockchain records..."):
                time.sleep(2)
                st.success("✅ All evidence packages verified successfully")
                st.info("🔗 Blockchain hash: 0x1a2b3c4d5e6f7890abcdef...")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>InsideOut Platform v1.0 | Developed for Indian Law Enforcement</p>
        <p>🔒 Secure • 🌐 Multi-lingual • ⚖️ Legally Compliant</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()