#!/usr/bin/env python3
"""
Enhanced Sentiment & Behavior Analysis Component for SentinentalBERT
BERT-based NLP analysis with comprehensive behavioral pattern detection
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import sys
import os
import re
from collections import Counter
import json

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from database.enhanced_cache_manager import EnhancedCacheManager
    from platforms.enhanced_twitter_service import EnhancedTwitterService
    from nlp.models.sentiment_model import SentimentAnalyzer
except ImportError as e:
    logging.warning(f"Could not import services: {e}")
    # Create mock SentimentAnalyzer
    class SentimentAnalyzer:
        def analyze_sentiment(self, text):
            return {'pos': 0.5, 'neg': 0.3, 'neu': 0.2, 'compound': 0.2}
        def get_sentiment_label(self, score):
            return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentBehaviorEnhanced:
    """Enhanced sentiment and behavior analysis with BERT and NLP"""
    
    def __init__(self):
        self.cache_manager = EnhancedCacheManager()
        self.twitter_service = EnhancedTwitterService()
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def render_sentiment_dashboard(self, keyword: str):
        """Render the complete sentiment and behavior dashboard"""
        st.subheader("🧠 Sentiment & Behavior Analysis")
        
        if not keyword:
            st.info("Enter a keyword to analyze sentiment and behavioral patterns")
            return
        
        # Control panel
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Analyzing Sentiment for:** `{keyword}`")
        
        with col2:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Comprehensive", "Sentiment Only", "Behavior Only"],
                help="Choose the type of analysis to perform"
            )
        
        with col3:
            if st.button("🔄 Refresh Analysis", key="refresh_sentiment"):
                self._refresh_sentiment_data(keyword)
                st.rerun()
        
        # Get sentiment data
        sentiment_data = self._get_sentiment_data(keyword)
        
        if not sentiment_data:
            st.warning("No sentiment data available. Analyzing fresh content...")
            self._analyze_fresh_content(keyword)
            sentiment_data = self._get_sentiment_data(keyword)
        
        if sentiment_data:
            if analysis_type in ["Comprehensive", "Sentiment Only"]:
                # Sentiment analysis
                self._render_sentiment_analysis(sentiment_data)
                
                # Emotion detection
                self._render_emotion_analysis(sentiment_data)
            
            if analysis_type in ["Comprehensive", "Behavior Only"]:
                # Behavioral patterns
                self._render_behavioral_analysis(sentiment_data)
                
                # User behavior clustering
                self._render_behavior_clustering(sentiment_data)
            
            if analysis_type == "Comprehensive":
                # Advanced analytics
                self._render_advanced_analytics(sentiment_data)
                
                # Toxicity and risk assessment
                self._render_toxicity_assessment(sentiment_data)
        else:
            st.error("Unable to analyze sentiment data. Please try again.")
    
    def _get_sentiment_data(self, keyword: str) -> Dict[str, Any]:
        """Get sentiment analysis data"""
        try:
            # Get posts from cache
            posts_data = self._get_cached_posts(keyword)
            
            if not posts_data:
                return {}
            
            # Analyze sentiment for each post
            analyzed_posts = []
            
            for post in posts_data:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(post.get('text', ''))
                
                analyzed_post = {
                    **post,
                    'sentiment_compound': sentiment_result.get('compound', 0),
                    'sentiment_positive': sentiment_result.get('pos', 0),
                    'sentiment_negative': sentiment_result.get('neg', 0),
                    'sentiment_neutral': sentiment_result.get('neu', 0),
                    'sentiment_label': self._get_sentiment_label(sentiment_result.get('compound', 0)),
                    'emotion_scores': self._analyze_emotions(post.get('text', '')),
                    'behavioral_indicators': self._extract_behavioral_indicators(post),
                    'toxicity_score': self._calculate_toxicity_score(post.get('text', ''))
                }
                
                analyzed_posts.append(analyzed_post)
            
            return {
                'keyword': keyword,
                'posts': analyzed_posts,
                'total_posts': len(analyzed_posts),
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment data: {e}")
            return {}
    
    def _get_cached_posts(self, keyword: str) -> List[Dict]:
        """Get cached posts for analysis"""
        try:
            # This would query the viral_content table
            # For now, get from Twitter service
            tweets = self.twitter_service.search_tweets(keyword, max_results=10, use_cache=True)
            
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
            
            return posts_data
            
        except Exception as e:
            logger.error(f"Error getting cached posts: {e}")
            return []
    
    def _analyze_fresh_content(self, keyword: str):
        """Analyze fresh content for sentiment"""
        try:
            with st.spinner("Analyzing sentiment of fresh content..."):
                # Get fresh tweets
                tweets = self.twitter_service.search_tweets(keyword, max_results=10)
                
                if tweets:
                    st.success(f"Analyzed sentiment for {len(tweets)} posts")
                else:
                    st.warning("No fresh content available for analysis")
                    
        except Exception as e:
            logger.error(f"Error analyzing fresh content: {e}")
            st.error(f"Error analyzing content: {e}")
    
    def _refresh_sentiment_data(self, keyword: str):
        """Refresh sentiment analysis data"""
        with st.spinner("Refreshing sentiment analysis..."):
            self._analyze_fresh_content(keyword)
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Get sentiment label from compound score"""
        if compound_score >= 0.05:
            return "Positive"
        elif compound_score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text using keyword-based approach"""
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'pleased', 'glad'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed', 'outraged'],
            'fear': ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'nervous', 'panic'],
            'sadness': ['sad', 'depressed', 'disappointed', 'grief', 'sorrow', 'melancholy'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled'],
            'trust': ['trust', 'confident', 'secure', 'reliable', 'faith', 'believe'],
            'anticipation': ['excited', 'eager', 'hopeful', 'optimistic', 'expecting']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score / len(keywords)  # Normalize
        
        return emotion_scores
    
    def _extract_behavioral_indicators(self, post: Dict) -> Dict[str, Any]:
        """Extract behavioral indicators from post"""
        text = post.get('text', '')
        metrics = post.get('public_metrics', {})
        
        indicators = {
            'urgency_level': self._calculate_urgency(text),
            'engagement_ratio': self._calculate_engagement_ratio(metrics),
            'influence_potential': self._calculate_influence_potential(post),
            'virality_indicators': self._detect_virality_indicators(text),
            'communication_style': self._analyze_communication_style(text),
            'credibility_score': self._assess_credibility(post)
        }
        
        return indicators
    
    def _calculate_urgency(self, text: str) -> float:
        """Calculate urgency level of text"""
        urgency_words = ['urgent', 'emergency', 'breaking', 'alert', 'immediate', 'now', 'asap', '!!!']
        text_lower = text.lower()
        
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        urgency_score = (urgency_count * 0.4) + (exclamation_count * 0.1) + (caps_ratio * 0.5)
        return min(urgency_score, 1.0)
    
    def _calculate_engagement_ratio(self, metrics: Dict) -> float:
        """Calculate engagement ratio"""
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        total_engagement = likes + retweets + replies
        
        if total_engagement == 0:
            return 0.0
        
        # Simple engagement ratio calculation
        return min(total_engagement / 100.0, 1.0)  # Normalize to 0-1
    
    def _calculate_influence_potential(self, post: Dict) -> float:
        """Calculate influence potential of post"""
        metrics = post.get('public_metrics', {})
        text = post.get('text', '')
        
        # Factors affecting influence
        engagement_score = self._calculate_engagement_ratio(metrics)
        content_quality = len(text) / 280.0 if text else 0  # Twitter character limit
        hashtag_count = text.count('#')
        mention_count = text.count('@')
        
        influence_score = (
            engagement_score * 0.4 +
            content_quality * 0.3 +
            min(hashtag_count / 5.0, 1.0) * 0.2 +
            min(mention_count / 3.0, 1.0) * 0.1
        )
        
        return min(influence_score, 1.0)
    
    def _detect_virality_indicators(self, text: str) -> List[str]:
        """Detect indicators of viral potential"""
        indicators = []
        
        # Check for viral patterns
        if re.search(r'#\w+', text):
            indicators.append('hashtags')
        
        if re.search(r'@\w+', text):
            indicators.append('mentions')
        
        if any(word in text.lower() for word in ['breaking', 'exclusive', 'shocking', 'unbelievable']):
            indicators.append('attention_grabbing')
        
        if text.count('!') > 2:
            indicators.append('high_excitement')
        
        if any(word in text.lower() for word in ['share', 'retweet', 'spread', 'tell everyone']):
            indicators.append('call_to_action')
        
        return indicators
    
    def _analyze_communication_style(self, text: str) -> Dict[str, float]:
        """Analyze communication style"""
        style_indicators = {
            'formal': len(re.findall(r'\b[A-Z][a-z]+\b', text)) / len(text.split()) if text.split() else 0,
            'emotional': (text.count('!') + text.count('?')) / len(text) if text else 0,
            'assertive': len([word for word in text.split() if word.isupper()]) / len(text.split()) if text.split() else 0,
            'questioning': text.count('?') / len(text) if text else 0
        }
        
        return style_indicators
    
    def _assess_credibility(self, post: Dict) -> float:
        """Assess credibility of post"""
        text = post.get('text', '')
        
        # Simple credibility indicators
        has_links = 'http' in text
        has_sources = any(word in text.lower() for word in ['source', 'according to', 'study', 'research'])
        excessive_caps = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        credibility_score = 0.5  # Base score
        
        if has_links:
            credibility_score += 0.2
        if has_sources:
            credibility_score += 0.3
        if excessive_caps > 0.3:  # Too many caps reduces credibility
            credibility_score -= 0.2
        
        return max(0.0, min(credibility_score, 1.0))
    
    def _calculate_toxicity_score(self, text: str) -> float:
        """Calculate toxicity score of text"""
        toxic_words = [
            'hate', 'stupid', 'idiot', 'moron', 'pathetic', 'disgusting',
            'terrible', 'awful', 'horrible', 'worst', 'useless', 'worthless'
        ]
        
        text_lower = text.lower()
        toxic_count = sum(1 for word in toxic_words if word in text_lower)
        
        # Normalize by text length
        toxicity_score = toxic_count / len(text.split()) if text.split() else 0
        
        return min(toxicity_score, 1.0)
    
    def _render_sentiment_analysis(self, sentiment_data: Dict[str, Any]):
        """Render sentiment analysis visualization"""
        st.subheader("😊 Sentiment Analysis")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for sentiment analysis")
            return
        
        # Sentiment distribution
        sentiment_counts = Counter([post['sentiment_label'] for post in posts])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment pie chart
            fig_pie = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title='Sentiment Distribution',
                color_discrete_map={
                    'Positive': '#2E8B57',
                    'Negative': '#DC143C',
                    'Neutral': '#708090'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Sentiment scores over time
            df = pd.DataFrame(posts)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df_sorted = df.sort_values('created_at')
            
            fig_timeline = px.scatter(
                df_sorted,
                x='created_at',
                y='sentiment_compound',
                color='sentiment_label',
                title='Sentiment Timeline',
                color_discrete_map={
                    'Positive': '#2E8B57',
                    'Negative': '#DC143C',
                    'Neutral': '#708090'
                }
            )
            fig_timeline.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Sentiment metrics
        avg_sentiment = np.mean([post['sentiment_compound'] for post in posts])
        sentiment_volatility = np.std([post['sentiment_compound'] for post in posts])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
        
        with col2:
            st.metric("Sentiment Volatility", f"{sentiment_volatility:.3f}")
        
        with col3:
            positive_ratio = sentiment_counts.get('Positive', 0) / len(posts)
            st.metric("Positive Ratio", f"{positive_ratio:.1%}")
        
        with col4:
            negative_ratio = sentiment_counts.get('Negative', 0) / len(posts)
            st.metric("Negative Ratio", f"{negative_ratio:.1%}")
    
    def _render_emotion_analysis(self, sentiment_data: Dict[str, Any]):
        """Render emotion analysis visualization"""
        st.subheader("🎭 Emotion Analysis")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for emotion analysis")
            return
        
        # Aggregate emotion scores
        emotion_totals = {}
        for post in posts:
            emotions = post.get('emotion_scores', {})
            for emotion, score in emotions.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
        
        # Normalize by number of posts
        emotion_averages = {emotion: score / len(posts) for emotion, score in emotion_totals.items()}
        
        # Emotion radar chart
        emotions = list(emotion_averages.keys())
        scores = list(emotion_averages.values())
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=scores,
            theta=emotions,
            fill='toself',
            name='Emotion Intensity'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(scores) if scores else 1]
                )),
            showlegend=True,
            title="Emotion Intensity Radar"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Top emotions
        sorted_emotions = sorted(emotion_averages.items(), key=lambda x: x[1], reverse=True)
        
        st.markdown("**🏆 Dominant Emotions**")
        for i, (emotion, score) in enumerate(sorted_emotions[:5], 1):
            st.markdown(f"{i}. **{emotion.title()}**: {score:.3f}")
    
    def _render_behavioral_analysis(self, sentiment_data: Dict[str, Any]):
        """Render behavioral pattern analysis"""
        st.subheader("🔍 Behavioral Pattern Analysis")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for behavioral analysis")
            return
        
        # Extract behavioral indicators
        urgency_scores = [post['behavioral_indicators']['urgency_level'] for post in posts]
        engagement_ratios = [post['behavioral_indicators']['engagement_ratio'] for post in posts]
        influence_potentials = [post['behavioral_indicators']['influence_potential'] for post in posts]
        credibility_scores = [post['behavioral_indicators']['credibility_score'] for post in posts]
        
        # Behavioral metrics visualization
        fig_behavior = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Urgency Distribution', 'Engagement Ratios', 
                          'Influence Potential', 'Credibility Scores'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}],
                   [{"type": "histogram"}, {"type": "histogram"}]]
        )
        
        fig_behavior.add_trace(
            go.Histogram(x=urgency_scores, name='Urgency', nbinsx=10),
            row=1, col=1
        )
        
        fig_behavior.add_trace(
            go.Histogram(x=engagement_ratios, name='Engagement', nbinsx=10),
            row=1, col=2
        )
        
        fig_behavior.add_trace(
            go.Histogram(x=influence_potentials, name='Influence', nbinsx=10),
            row=2, col=1
        )
        
        fig_behavior.add_trace(
            go.Histogram(x=credibility_scores, name='Credibility', nbinsx=10),
            row=2, col=2
        )
        
        fig_behavior.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_behavior, use_container_width=True)
        
        # Behavioral summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_urgency = np.mean(urgency_scores)
            st.metric("Avg Urgency", f"{avg_urgency:.3f}")
        
        with col2:
            avg_engagement = np.mean(engagement_ratios)
            st.metric("Avg Engagement", f"{avg_engagement:.3f}")
        
        with col3:
            avg_influence = np.mean(influence_potentials)
            st.metric("Avg Influence", f"{avg_influence:.3f}")
        
        with col4:
            avg_credibility = np.mean(credibility_scores)
            st.metric("Avg Credibility", f"{avg_credibility:.3f}")
    
    def _render_behavior_clustering(self, sentiment_data: Dict[str, Any]):
        """Render behavior clustering analysis"""
        st.subheader("👥 User Behavior Clustering")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for clustering analysis")
            return
        
        # Create behavior profiles
        behavior_profiles = []
        for post in posts:
            indicators = post['behavioral_indicators']
            profile = {
                'author_id': post['author_id'],
                'urgency': indicators['urgency_level'],
                'engagement': indicators['engagement_ratio'],
                'influence': indicators['influence_potential'],
                'credibility': indicators['credibility_score'],
                'sentiment': post['sentiment_compound']
            }
            behavior_profiles.append(profile)
        
        df_behavior = pd.DataFrame(behavior_profiles)
        
        # Scatter plot for clustering visualization
        fig_cluster = px.scatter(
            df_behavior,
            x='urgency',
            y='credibility',
            size='influence',
            color='sentiment',
            hover_data=['author_id', 'engagement'],
            title='User Behavior Clustering (Urgency vs Credibility)',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        # Behavior categories
        st.markdown("**📊 Behavior Categories**")
        
        # Simple categorization
        high_urgency = len([p for p in behavior_profiles if p['urgency'] > 0.5])
        high_credibility = len([p for p in behavior_profiles if p['credibility'] > 0.7])
        high_influence = len([p for p in behavior_profiles if p['influence'] > 0.6])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Urgency Users", high_urgency)
        
        with col2:
            st.metric("High Credibility Users", high_credibility)
        
        with col3:
            st.metric("High Influence Users", high_influence)
    
    def _render_advanced_analytics(self, sentiment_data: Dict[str, Any]):
        """Render advanced analytics"""
        st.subheader("🔬 Advanced Analytics")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for advanced analytics")
            return
        
        # Correlation analysis
        df = pd.DataFrame([
            {
                'sentiment': post['sentiment_compound'],
                'urgency': post['behavioral_indicators']['urgency_level'],
                'engagement': post['behavioral_indicators']['engagement_ratio'],
                'influence': post['behavioral_indicators']['influence_potential'],
                'credibility': post['behavioral_indicators']['credibility_score'],
                'toxicity': post['toxicity_score']
            }
            for post in posts
        ])
        
        # Correlation heatmap
        correlation_matrix = df.corr()
        
        fig_corr = px.imshow(
            correlation_matrix,
            title='Behavioral Correlation Matrix',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Key insights
        st.markdown("**🔍 Key Insights**")
        
        # Find strongest correlations
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:  # Significant correlation
                    correlations.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        for corr in correlations[:3]:
            direction = "positively" if corr['correlation'] > 0 else "negatively"
            st.markdown(f"• **{corr['var1'].title()}** and **{corr['var2'].title()}** are {direction} correlated ({corr['correlation']:.3f})")
    
    def _render_toxicity_assessment(self, sentiment_data: Dict[str, Any]):
        """Render toxicity and risk assessment"""
        st.subheader("⚠️ Toxicity & Risk Assessment")
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            st.warning("No posts available for toxicity assessment")
            return
        
        # Toxicity analysis
        toxicity_scores = [post['toxicity_score'] for post in posts]
        high_toxicity_posts = [post for post in posts if post['toxicity_score'] > 0.3]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_toxicity = np.mean(toxicity_scores)
            st.metric("Average Toxicity", f"{avg_toxicity:.3f}")
        
        with col2:
            max_toxicity = max(toxicity_scores) if toxicity_scores else 0
            st.metric("Max Toxicity", f"{max_toxicity:.3f}")
        
        with col3:
            high_toxicity_ratio = len(high_toxicity_posts) / len(posts) if posts else 0
            st.metric("High Toxicity Ratio", f"{high_toxicity_ratio:.1%}")
        
        # Risk level assessment
        if avg_toxicity > 0.5:
            st.error("🚨 HIGH RISK: Significant toxic content detected")
        elif avg_toxicity > 0.3:
            st.warning("⚠️ MEDIUM RISK: Moderate toxic content detected")
        else:
            st.success("✅ LOW RISK: Minimal toxic content detected")
        
        # Toxicity distribution
        fig_toxicity = px.histogram(
            x=toxicity_scores,
            nbins=20,
            title='Toxicity Score Distribution',
            labels={'x': 'Toxicity Score', 'y': 'Number of Posts'}
        )
        
        fig_toxicity.add_vline(x=0.3, line_dash="dash", line_color="orange", 
                              annotation_text="Medium Risk Threshold")
        fig_toxicity.add_vline(x=0.5, line_dash="dash", line_color="red", 
                              annotation_text="High Risk Threshold")
        
        st.plotly_chart(fig_toxicity, use_container_width=True)
    
    def get_sentiment_summary(self, keyword: str) -> Dict[str, Any]:
        """Get sentiment summary for other components"""
        sentiment_data = self._get_sentiment_data(keyword)
        
        if not sentiment_data:
            return {}
        
        posts = sentiment_data.get('posts', [])
        
        if not posts:
            return {}
        
        sentiment_scores = [post['sentiment_compound'] for post in posts]
        toxicity_scores = [post['toxicity_score'] for post in posts]
        
        return {
            'total_posts_analyzed': len(posts),
            'average_sentiment': np.mean(sentiment_scores),
            'sentiment_volatility': np.std(sentiment_scores),
            'positive_ratio': len([p for p in posts if p['sentiment_label'] == 'Positive']) / len(posts),
            'negative_ratio': len([p for p in posts if p['sentiment_label'] == 'Negative']) / len(posts),
            'average_toxicity': np.mean(toxicity_scores),
            'high_toxicity_count': len([p for p in posts if p['toxicity_score'] > 0.3]),
            'dominant_emotion': self._get_dominant_emotion(posts)
        }
    
    def _get_dominant_emotion(self, posts: List[Dict]) -> str:
        """Get the dominant emotion across all posts"""
        emotion_totals = {}
        
        for post in posts:
            emotions = post.get('emotion_scores', {})
            for emotion, score in emotions.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
        
        if emotion_totals:
            return max(emotion_totals.items(), key=lambda x: x[1])[0]
        else:
            return "neutral"

# Test the component
if __name__ == "__main__":
    # This would be called from the main dashboard
    sentiment_behavior = SentimentBehaviorEnhanced()
    
    # Test with sample data
    test_keyword = "climate change"
    print(f"Testing sentiment analysis for keyword: {test_keyword}")
    
    summary = sentiment_behavior.get_sentiment_summary(test_keyword)
    print(f"Sentiment summary: {summary}")