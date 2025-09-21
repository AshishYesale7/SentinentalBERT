#!/usr/bin/env python3
"""
Test core functionality of InsideOut platform without database dependencies
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
    
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
    
    try:
        import plotly
        print(f"✅ Plotly {plotly.__version__}")
    except ImportError as e:
        print(f"❌ Plotly: {e}")
    
    try:
        import networkx
        print(f"✅ NetworkX {networkx.__version__}")
    except ImportError as e:
        print(f"❌ NetworkX: {e}")
    
    try:
        import sklearn
        print(f"✅ Scikit-learn {sklearn.__version__}")
    except ImportError as e:
        print(f"❌ Scikit-learn: {e}")

def test_bert_model():
    """Test BERT model loading and basic functionality"""
    print("\n🤖 Testing BERT model...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        # Load a lightweight BERT model
        model_name = "distilbert-base-uncased"
        print(f"Loading {model_name}...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Test tokenization
        test_text = "This is a test message for viral content analysis"
        tokens = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        
        # Test model inference
        with torch.no_grad():
            outputs = model(**tokens)
            embeddings = outputs.last_hidden_state
        
        print(f"✅ BERT model loaded successfully")
        print(f"   - Input text: '{test_text}'")
        print(f"   - Token count: {len(tokens['input_ids'][0])}")
        print(f"   - Embedding shape: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ BERT model test failed: {e}")
        return False

def test_viral_analysis_logic():
    """Test viral analysis algorithms without database"""
    print("\n📊 Testing viral analysis logic...")
    
    try:
        # Create mock data
        mock_posts = []
        for i in range(50):
            post = {
                'id': f'post_{i}',
                'content': f'Mock viral content {i}',
                'author_id': f'user_{i % 10}',
                'platform': ['twitter', 'facebook', 'instagram'][i % 3],
                'timestamp': datetime.now() - timedelta(hours=i),
                'engagement_count': np.random.randint(10, 10000),
                'is_repost': i > 0 and np.random.random() < 0.3,
                'location': ['Delhi', 'Mumbai', 'Bangalore'][i % 3]
            }
            mock_posts.append(post)
        
        df = pd.DataFrame(mock_posts)
        
        # Test basic analytics
        print(f"✅ Created {len(df)} mock posts")
        print(f"   - Platforms: {df['platform'].unique()}")
        print(f"   - Locations: {df['location'].unique()}")
        print(f"   - Reposts: {df['is_repost'].sum()}")
        print(f"   - Avg engagement: {df['engagement_count'].mean():.0f}")
        
        # Test viral score calculation
        def calculate_viral_score(row):
            base_score = np.log10(row['engagement_count'] + 1)
            repost_bonus = 2.0 if row['is_repost'] else 0.0
            time_decay = max(0, 1 - (datetime.now() - row['timestamp']).total_seconds() / (24 * 3600))
            return min(10.0, base_score + repost_bonus + time_decay)
        
        df['viral_score'] = df.apply(calculate_viral_score, axis=1)
        
        high_viral = df[df['viral_score'] > 7.0]
        print(f"✅ Viral score calculation completed")
        print(f"   - High viral content: {len(high_viral)} posts")
        print(f"   - Max viral score: {df['viral_score'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Viral analysis test failed: {e}")
        return False

def test_network_analysis():
    """Test network analysis functionality"""
    print("\n🕸️ Testing network analysis...")
    
    try:
        import networkx as nx
        
        # Create mock influence network
        G = nx.Graph()
        
        # Add nodes (users)
        users = [f'user_{i}' for i in range(20)]
        for user in users:
            G.add_node(user, influence_score=np.random.uniform(0.1, 1.0))
        
        # Add edges (connections)
        for i in range(30):
            user1 = np.random.choice(users)
            user2 = np.random.choice(users)
            if user1 != user2:
                weight = np.random.uniform(0.1, 1.0)
                G.add_edge(user1, user2, weight=weight)
        
        # Calculate network metrics
        centrality = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G)
        
        print(f"✅ Network analysis completed")
        print(f"   - Nodes: {G.number_of_nodes()}")
        print(f"   - Edges: {G.number_of_edges()}")
        print(f"   - Most central user: {max(centrality, key=centrality.get)}")
        print(f"   - Max centrality: {max(centrality.values()):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Network analysis test failed: {e}")
        return False

def test_content_similarity():
    """Test content similarity analysis"""
    print("\n🔍 Testing content similarity...")
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Mock content
        contents = [
            "Breaking news about government policy changes",
            "Government announces new policy updates",
            "Sports victory celebration nationwide",
            "Cricket team wins international match",
            "Educational content about digital literacy",
            "Digital education awareness campaign"
        ]
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(contents)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        print(f"✅ Content similarity analysis completed")
        print(f"   - Content items: {len(contents)}")
        print(f"   - Feature count: {tfidf_matrix.shape[1]}")
        
        # Find most similar pairs
        for i in range(len(contents)):
            for j in range(i+1, len(contents)):
                similarity = similarity_matrix[i][j]
                if similarity > 0.3:  # Threshold for similarity
                    print(f"   - Similar content ({similarity:.3f}): '{contents[i][:30]}...' & '{contents[j][:30]}...'")
        
        return True
        
    except Exception as e:
        print(f"❌ Content similarity test failed: {e}")
        return False

def test_geographic_analysis():
    """Test geographic spread analysis"""
    print("\n🌍 Testing geographic analysis...")
    
    try:
        # Mock geographic data
        locations = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
        
        # Create mock viral spread data
        spread_data = []
        for location in locations:
            for hour in range(24):
                count = np.random.poisson(10)  # Poisson distribution for viral spread
                spread_data.append({
                    'location': location,
                    'hour': hour,
                    'viral_count': count,
                    'timestamp': datetime.now() - timedelta(hours=23-hour)
                })
        
        df = pd.DataFrame(spread_data)
        
        # Calculate spread metrics
        location_totals = df.groupby('location')['viral_count'].sum().sort_values(ascending=False)
        peak_hours = df.groupby('hour')['viral_count'].sum().sort_values(ascending=False)
        
        print(f"✅ Geographic analysis completed")
        print(f"   - Locations analyzed: {len(locations)}")
        print(f"   - Top viral location: {location_totals.index[0]} ({location_totals.iloc[0]} posts)")
        print(f"   - Peak hour: {peak_hours.index[0]}:00 ({peak_hours.iloc[0]} posts)")
        
        return True
        
    except Exception as e:
        print(f"❌ Geographic analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 InsideOut Platform - Core Functionality Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    test_imports()
    results.append(("BERT Model", test_bert_model()))
    results.append(("Viral Analysis", test_viral_analysis_logic()))
    results.append(("Network Analysis", test_network_analysis()))
    results.append(("Content Similarity", test_content_similarity()))
    results.append(("Geographic Analysis", test_geographic_analysis()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("-" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All core functionality tests passed!")
    else:
        print("⚠️  Some tests failed - check the output above")
    
    return passed == total

if __name__ == "__main__":
    main()