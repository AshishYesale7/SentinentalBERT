#!/usr/bin/env python3
"""
Tracking Cache Database System for SentinelBERT
Implements local caching to minimize API calls and store tracking data
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CachedTrackingData:
    """Cached tracking data structure"""
    cache_key: str
    platform: str
    query_type: str  # 'hashtag', 'url', 'trend', 'keyword'
    query_value: str
    data: Dict[str, Any]
    timestamp: datetime
    expires_at: datetime
    api_calls_used: int

class TrackingCacheDB:
    """Database for caching tracking data and minimizing API calls"""
    
    def __init__(self, db_path: str = "data/tracking_cache.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracking_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_value TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    api_calls_used INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_collection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_value TEXT NOT NULL,
                    evidence_data TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    case_reference TEXT,
                    officer_id TEXT,
                    status TEXT DEFAULT 'collected'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mock_trending_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    trend_data TEXT NOT NULL,
                    sentiment_score REAL,
                    engagement_count INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _generate_cache_key(self, platform: str, query_type: str, query_value: str) -> str:
        """Generate unique cache key"""
        key_string = f"{platform}:{query_type}:{query_value.lower()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_data(self, platform: str, query_type: str, query_value: str) -> Optional[CachedTrackingData]:
        """Retrieve cached data if available and not expired"""
        cache_key = self._generate_cache_key(platform, query_type, query_value)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT cache_key, platform, query_type, query_value, data, 
                       timestamp, expires_at, api_calls_used
                FROM tracking_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            if row:
                return CachedTrackingData(
                    cache_key=row[0],
                    platform=row[1],
                    query_type=row[2],
                    query_value=row[3],
                    data=json.loads(row[4]),
                    timestamp=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]),
                    api_calls_used=row[7]
                )
        return None
    
    def cache_data(self, platform: str, query_type: str, query_value: str, 
                   data: Dict[str, Any], cache_duration_hours: int = 24, 
                   api_calls_used: int = 1) -> str:
        """Cache tracking data"""
        cache_key = self._generate_cache_key(platform, query_type, query_value)
        timestamp = datetime.now()
        expires_at = timestamp + timedelta(hours=cache_duration_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tracking_cache 
                (cache_key, platform, query_type, query_value, data, timestamp, expires_at, api_calls_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cache_key, platform, query_type, query_value, json.dumps(data), 
                  timestamp.isoformat(), expires_at.isoformat(), api_calls_used))
            conn.commit()
            
        logger.info(f"Cached data for {platform}:{query_type}:{query_value}")
        return cache_key
    
    def get_api_usage_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get API usage statistics"""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT platform, SUM(api_calls_used) as total_calls, COUNT(*) as requests
                FROM tracking_cache 
                WHERE timestamp > ?
                GROUP BY platform
            """, (since.isoformat(),))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = {
                    'total_api_calls': row[1],
                    'total_requests': row[2]
                }
            
            # Get overall stats
            cursor = conn.execute("""
                SELECT SUM(api_calls_used) as total_calls, COUNT(*) as requests
                FROM tracking_cache 
                WHERE timestamp > ?
            """, (since.isoformat(),))
            
            overall = cursor.fetchone()
            stats['overall'] = {
                'total_api_calls': overall[0] or 0,
                'total_requests': overall[1] or 0,
                'cache_hit_rate': self._calculate_cache_hit_rate(hours)
            }
            
        return stats
    
    def _calculate_cache_hit_rate(self, hours: int = 24) -> float:
        """Calculate cache hit rate"""
        # This would be implemented with request tracking
        # For now, return estimated rate
        return 0.75  # 75% cache hit rate estimate
    
    def store_evidence(self, platform: str, query_type: str, query_value: str, 
                      evidence_data: Dict[str, Any], case_reference: str = None, 
                      officer_id: str = None) -> str:
        """Store evidence data"""
        evidence_id = f"EV_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(f'{platform}:{query_value}'.encode()).hexdigest()[:8]}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO evidence_collection 
                (evidence_id, platform, query_type, query_value, evidence_data, 
                 collected_at, case_reference, officer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (evidence_id, platform, query_type, query_value, 
                  json.dumps(evidence_data), datetime.now().isoformat(), 
                  case_reference, officer_id))
            conn.commit()
            
        logger.info(f"Evidence stored with ID: {evidence_id}")
        return evidence_id
    
    def get_evidence_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get evidence collection history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT evidence_id, platform, query_type, query_value, 
                       collected_at, case_reference, officer_id, status
                FROM evidence_collection 
                ORDER BY collected_at DESC 
                LIMIT ?
            """, (limit,))
            
            evidence_list = []
            for row in cursor.fetchall():
                evidence_list.append({
                    'evidence_id': row[0],
                    'platform': row[1],
                    'query_type': row[2],
                    'query_value': row[3],
                    'collected_at': row[4],
                    'case_reference': row[5],
                    'officer_id': row[6],
                    'status': row[7]
                })
            
        return evidence_list
    
    def initialize_mock_trending_data(self):
        """Initialize mock trending data for demo purposes"""
        mock_trends = [
            {
                'keyword': 'climate change',
                'platform': 'twitter',
                'trend_data': {
                    'posts': [
                        {
                            'id': 'mock_001',
                            'content': 'Climate change is affecting our monsoons severely this year. #ClimateChange #India',
                            'author': 'environmental_activist',
                            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                            'engagement': {'likes': 245, 'retweets': 89, 'replies': 34},
                            'location': 'Mumbai, India'
                        },
                        {
                            'id': 'mock_002',
                            'content': 'New research shows alarming trends in global warming patterns',
                            'author': 'climate_researcher',
                            'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
                            'engagement': {'likes': 567, 'retweets': 234, 'replies': 78},
                            'location': 'Delhi, India'
                        }
                    ],
                    'sentiment_distribution': {'positive': 0.2, 'neutral': 0.3, 'negative': 0.5},
                    'geographic_spread': ['India', 'USA', 'UK', 'Australia'],
                    'viral_metrics': {'growth_rate': 0.15, 'reach': 15000, 'influence_score': 0.78}
                },
                'sentiment_score': -0.3,
                'engagement_count': 1247
            },
            {
                'keyword': 'digital india',
                'platform': 'twitter',
                'trend_data': {
                    'posts': [
                        {
                            'id': 'mock_003',
                            'content': 'Digital India initiative transforming rural connectivity! #DigitalIndia #Technology',
                            'author': 'tech_enthusiast',
                            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                            'engagement': {'likes': 892, 'retweets': 445, 'replies': 123},
                            'location': 'Bangalore, India'
                        }
                    ],
                    'sentiment_distribution': {'positive': 0.7, 'neutral': 0.2, 'negative': 0.1},
                    'geographic_spread': ['India', 'Singapore', 'UAE'],
                    'viral_metrics': {'growth_rate': 0.25, 'reach': 25000, 'influence_score': 0.85}
                },
                'sentiment_score': 0.6,
                'engagement_count': 1460
            },
            {
                'keyword': 'cybersecurity',
                'platform': 'twitter',
                'trend_data': {
                    'posts': [
                        {
                            'id': 'mock_004',
                            'content': 'New cybersecurity threats targeting Indian financial institutions. Stay alert! #CyberSecurity #India',
                            'author': 'security_expert',
                            'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                            'engagement': {'likes': 334, 'retweets': 156, 'replies': 67},
                            'location': 'Chennai, India'
                        }
                    ],
                    'sentiment_distribution': {'positive': 0.1, 'neutral': 0.4, 'negative': 0.5},
                    'geographic_spread': ['India', 'USA', 'UK'],
                    'viral_metrics': {'growth_rate': 0.12, 'reach': 8500, 'influence_score': 0.72}
                },
                'sentiment_score': -0.2,
                'engagement_count': 557
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing mock data
            conn.execute("DELETE FROM mock_trending_data")
            
            # Insert new mock data
            for trend in mock_trends:
                conn.execute("""
                    INSERT INTO mock_trending_data 
                    (keyword, platform, trend_data, sentiment_score, engagement_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (trend['keyword'], trend['platform'], 
                      json.dumps(trend['trend_data']), 
                      trend['sentiment_score'], trend['engagement_count']))
            
            conn.commit()
            logger.info("Mock trending data initialized")
    
    def get_mock_trending_data(self, keyword: str = None) -> List[Dict[str, Any]]:
        """Get mock trending data for demo purposes"""
        with sqlite3.connect(self.db_path) as conn:
            if keyword:
                cursor = conn.execute("""
                    SELECT keyword, platform, trend_data, sentiment_score, engagement_count
                    FROM mock_trending_data 
                    WHERE keyword LIKE ? AND is_active = 1
                """, (f"%{keyword}%",))
            else:
                cursor = conn.execute("""
                    SELECT keyword, platform, trend_data, sentiment_score, engagement_count
                    FROM mock_trending_data 
                    WHERE is_active = 1
                    ORDER BY engagement_count DESC
                """)
            
            trends = []
            for row in cursor.fetchall():
                trends.append({
                    'keyword': row[0],
                    'platform': row[1],
                    'trend_data': json.loads(row[2]),
                    'sentiment_score': row[3],
                    'engagement_count': row[4]
                })
            
        return trends
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM tracking_cache 
                WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
        logger.info(f"Cleaned up {deleted_count} expired cache entries")
        return deleted_count

# Global cache instance
cache_db = TrackingCacheDB()

# Initialize mock data on first import
try:
    cache_db.initialize_mock_trending_data()
except Exception as e:
    logger.warning(f"Could not initialize mock data: {e}")