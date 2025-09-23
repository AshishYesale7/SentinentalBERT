#!/usr/bin/env python3
"""
Enhanced Cache Manager for SentinentalBERT
Optimized database operations with intelligent caching
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import os
from dataclasses import dataclass, asdict
import threading
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None

class EnhancedCacheManager:
    """Enhanced cache manager with intelligent data management"""
    
    def __init__(self, db_path: str = "data/enhanced_cache.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        
    def _init_database(self):
        """Initialize enhanced database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    data_type TEXT DEFAULT 'json',
                    size_bytes INTEGER DEFAULT 0
                )
            ''')
            
            # Viral content tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS viral_content (
                    id TEXT PRIMARY KEY,
                    keyword TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id TEXT,
                    author_name TEXT,
                    created_at TIMESTAMP,
                    engagement_metrics TEXT,
                    sentiment_score REAL,
                    influence_score REAL,
                    geographic_data TEXT,
                    viral_potential REAL DEFAULT 0.0,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Timeline analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeline_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    time_period TEXT NOT NULL,
                    date_bucket TEXT NOT NULL,
                    post_count INTEGER DEFAULT 0,
                    engagement_total INTEGER DEFAULT 0,
                    sentiment_avg REAL DEFAULT 0.0,
                    viral_score REAL DEFAULT 0.0,
                    top_influencers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Influence network tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS influence_network (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    source_user_id TEXT NOT NULL,
                    target_user_id TEXT,
                    interaction_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    influence_weight REAL DEFAULT 1.0,
                    content_id TEXT,
                    geographic_location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Evidence collection
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence_collection (
                    id TEXT PRIMARY KEY,
                    keyword TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    source_url TEXT,
                    collected_by TEXT,
                    legal_status TEXT DEFAULT 'pending',
                    chain_of_custody TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash_signature TEXT
                )
            ''')
            
            # Geographic spread data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geographic_spread (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    country_code TEXT,
                    region TEXT,
                    city TEXT,
                    latitude REAL,
                    longitude REAL,
                    post_count INTEGER DEFAULT 1,
                    engagement_total INTEGER DEFAULT 0,
                    sentiment_avg REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Search trends
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    search_volume INTEGER DEFAULT 1,
                    trend_score REAL DEFAULT 0.0,
                    related_keywords TEXT,
                    controversy_score REAL DEFAULT 0.0,
                    top_spreaders TEXT,
                    date_bucket TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_viral_keyword ON viral_content(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_viral_created ON viral_content(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timeline_keyword ON timeline_analytics(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_influence_keyword ON influence_network(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_evidence_keyword ON evidence_collection(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_keyword ON geographic_spread(keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_keyword ON search_trends(keyword)')
            
            conn.commit()
            logger.info("Enhanced database schema initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper handling"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def cache_viral_content(self, keyword: str, posts: List[Dict]) -> bool:
        """Cache viral content with enhanced metadata"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for post in posts:
                        # Calculate viral potential
                        viral_potential = self._calculate_viral_potential(post)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO viral_content 
                            (id, keyword, platform, content, author_id, author_name, 
                             created_at, engagement_metrics, viral_potential)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            post.get('id', ''),
                            keyword,
                            post.get('platform', 'twitter'),
                            post.get('text', ''),
                            post.get('author_id', ''),
                            post.get('author_name', ''),
                            post.get('created_at', datetime.now()),
                            json.dumps(post.get('public_metrics', {})),
                            viral_potential
                        ))
                    
                    conn.commit()
                    logger.info(f"Cached {len(posts)} viral content entries for keyword: {keyword}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error caching viral content: {e}")
            return False
    
    def get_timeline_analytics(self, keyword: str, time_period: str = "24h") -> Dict[str, Any]:
        """Get timeline analytics for specified period"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Calculate time range
                if time_period == "24h":
                    start_time = datetime.now() - timedelta(hours=24)
                    bucket_format = "%Y-%m-%d %H:00"
                elif time_period == "1w":
                    start_time = datetime.now() - timedelta(weeks=1)
                    bucket_format = "%Y-%m-%d"
                elif time_period == "1m":
                    start_time = datetime.now() - timedelta(days=30)
                    bucket_format = "%Y-%m-%d"
                else:
                    start_time = datetime.now() - timedelta(hours=24)
                    bucket_format = "%Y-%m-%d %H:00"
                
                # Get viral content for the period
                cursor.execute('''
                    SELECT 
                        strftime(?, created_at) as time_bucket,
                        COUNT(*) as post_count,
                        AVG(viral_potential) as avg_viral_score,
                        SUM(CAST(json_extract(engagement_metrics, '$.like_count') AS INTEGER)) as total_likes,
                        SUM(CAST(json_extract(engagement_metrics, '$.retweet_count') AS INTEGER)) as total_retweets
                    FROM viral_content 
                    WHERE keyword = ? AND created_at >= ?
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                ''', (bucket_format, keyword, start_time))
                
                timeline_data = []
                for row in cursor.fetchall():
                    timeline_data.append({
                        'time': row['time_bucket'],
                        'posts': row['post_count'],
                        'viral_score': round(row['avg_viral_score'] or 0, 2),
                        'engagement': (row['total_likes'] or 0) + (row['total_retweets'] or 0)
                    })
                
                return {
                    'keyword': keyword,
                    'period': time_period,
                    'timeline': timeline_data,
                    'total_posts': sum(item['posts'] for item in timeline_data),
                    'peak_time': max(timeline_data, key=lambda x: x['posts'])['time'] if timeline_data else None
                }
                
        except Exception as e:
            logger.error(f"Error getting timeline analytics: {e}")
            return {'keyword': keyword, 'period': time_period, 'timeline': [], 'total_posts': 0}
    
    def track_influence_network(self, keyword: str, interactions: List[Dict]) -> bool:
        """Track influence network interactions"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for interaction in interactions:
                        cursor.execute('''
                            INSERT INTO influence_network 
                            (keyword, source_user_id, target_user_id, interaction_type, 
                             timestamp, influence_weight, content_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            keyword,
                            interaction.get('source_user_id', ''),
                            interaction.get('target_user_id', ''),
                            interaction.get('type', 'mention'),
                            interaction.get('timestamp', datetime.now()),
                            interaction.get('weight', 1.0),
                            interaction.get('content_id', '')
                        ))
                    
                    conn.commit()
                    logger.info(f"Tracked {len(interactions)} influence interactions for keyword: {keyword}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error tracking influence network: {e}")
            return False
    
    def get_influence_network(self, keyword: str) -> Dict[str, Any]:
        """Get influence network data for visualization"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get nodes (users)
                cursor.execute('''
                    SELECT DISTINCT source_user_id as user_id, 
                           COUNT(*) as interaction_count,
                           SUM(influence_weight) as total_influence
                    FROM influence_network 
                    WHERE keyword = ?
                    GROUP BY source_user_id
                    ORDER BY total_influence DESC
                    LIMIT 50
                ''', (keyword,))
                
                nodes = []
                for row in cursor.fetchall():
                    nodes.append({
                        'id': row['user_id'],
                        'interactions': row['interaction_count'],
                        'influence': round(row['total_influence'], 2)
                    })
                
                # Get edges (connections)
                cursor.execute('''
                    SELECT source_user_id, target_user_id, 
                           COUNT(*) as connection_strength,
                           interaction_type
                    FROM influence_network 
                    WHERE keyword = ? AND target_user_id IS NOT NULL
                    GROUP BY source_user_id, target_user_id, interaction_type
                    ORDER BY connection_strength DESC
                    LIMIT 100
                ''', (keyword,))
                
                edges = []
                for row in cursor.fetchall():
                    edges.append({
                        'source': row['source_user_id'],
                        'target': row['target_user_id'],
                        'weight': row['connection_strength'],
                        'type': row['interaction_type']
                    })
                
                return {
                    'keyword': keyword,
                    'nodes': nodes,
                    'edges': edges,
                    'network_stats': {
                        'total_nodes': len(nodes),
                        'total_edges': len(edges),
                        'top_influencer': nodes[0]['id'] if nodes else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting influence network: {e}")
            return {'keyword': keyword, 'nodes': [], 'edges': [], 'network_stats': {}}
    
    def store_evidence(self, keyword: str, evidence_data: Dict) -> str:
        """Store evidence with chain of custody"""
        try:
            evidence_id = hashlib.md5(f"{keyword}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Create hash signature for integrity
            content_hash = hashlib.sha256(
                json.dumps(evidence_data, sort_keys=True).encode()
            ).hexdigest()
            
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO evidence_collection 
                        (id, keyword, evidence_type, content, metadata, source_url, 
                         collected_by, chain_of_custody, hash_signature)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        evidence_id,
                        keyword,
                        evidence_data.get('type', 'social_media_post'),
                        json.dumps(evidence_data.get('content', {})),
                        json.dumps(evidence_data.get('metadata', {})),
                        evidence_data.get('source_url', ''),
                        evidence_data.get('collected_by', 'system'),
                        json.dumps({
                            'collection_time': datetime.now().isoformat(),
                            'collection_method': 'automated_api',
                            'integrity_verified': True
                        }),
                        content_hash
                    ))
                    
                    conn.commit()
                    logger.info(f"Stored evidence with ID: {evidence_id}")
                    return evidence_id
                    
        except Exception as e:
            logger.error(f"Error storing evidence: {e}")
            return ""
    
    def get_evidence_collection(self, keyword: str) -> List[Dict]:
        """Get all evidence for a keyword"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM evidence_collection 
                    WHERE keyword = ?
                    ORDER BY created_at DESC
                ''', (keyword,))
                
                evidence_list = []
                for row in cursor.fetchall():
                    evidence_list.append({
                        'id': row['id'],
                        'type': row['evidence_type'],
                        'content': json.loads(row['content']),
                        'metadata': json.loads(row['metadata']),
                        'source_url': row['source_url'],
                        'collected_by': row['collected_by'],
                        'legal_status': row['legal_status'],
                        'created_at': row['created_at'],
                        'hash_signature': row['hash_signature']
                    })
                
                return evidence_list
                
        except Exception as e:
            logger.error(f"Error getting evidence collection: {e}")
            return []
    
    def update_geographic_spread(self, keyword: str, location_data: List[Dict]) -> bool:
        """Update geographic spread data"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for location in location_data:
                        cursor.execute('''
                            INSERT OR REPLACE INTO geographic_spread 
                            (keyword, country_code, region, city, latitude, longitude, 
                             post_count, engagement_total, sentiment_avg)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            keyword,
                            location.get('country_code', ''),
                            location.get('region', ''),
                            location.get('city', ''),
                            location.get('latitude', 0.0),
                            location.get('longitude', 0.0),
                            location.get('post_count', 1),
                            location.get('engagement', 0),
                            location.get('sentiment', 0.0)
                        ))
                    
                    conn.commit()
                    logger.info(f"Updated geographic spread for {len(location_data)} locations")
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating geographic spread: {e}")
            return False
    
    def get_geographic_spread(self, keyword: str) -> List[Dict]:
        """Get geographic spread data for mapping"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM geographic_spread 
                    WHERE keyword = ?
                    ORDER BY post_count DESC
                ''', (keyword,))
                
                locations = []
                for row in cursor.fetchall():
                    locations.append({
                        'country': row['country_code'],
                        'region': row['region'],
                        'city': row['city'],
                        'lat': row['latitude'],
                        'lng': row['longitude'],
                        'posts': row['post_count'],
                        'engagement': row['engagement_total'],
                        'sentiment': row['sentiment_avg']
                    })
                
                return locations
                
        except Exception as e:
            logger.error(f"Error getting geographic spread: {e}")
            return []
    
    def _calculate_viral_potential(self, post: Dict) -> float:
        """Calculate viral potential score for a post"""
        try:
            metrics = post.get('public_metrics', {})
            
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            quotes = metrics.get('quote_count', 0)
            
            # Simple viral potential calculation
            engagement_score = (likes * 1) + (retweets * 3) + (replies * 2) + (quotes * 2)
            
            # Normalize to 0-1 scale
            viral_potential = min(engagement_score / 1000.0, 1.0)
            
            return viral_potential
            
        except Exception as e:
            logger.error(f"Error calculating viral potential: {e}")
            return 0.0
    
    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        DELETE FROM cache_entries 
                        WHERE expires_at < ?
                    ''', (datetime.now(),))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} expired cache entries")
                    
                    return deleted_count
                    
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Cache entries stats
                cursor.execute('SELECT COUNT(*) FROM cache_entries')
                stats['total_cache_entries'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM cache_entries WHERE expires_at > ?', (datetime.now(),))
                stats['active_cache_entries'] = cursor.fetchone()[0]
                
                # Viral content stats
                cursor.execute('SELECT COUNT(*) FROM viral_content')
                stats['total_viral_content'] = cursor.fetchone()[0]
                
                # Evidence stats
                cursor.execute('SELECT COUNT(*) FROM evidence_collection')
                stats['total_evidence'] = cursor.fetchone()[0]
                
                # Geographic data stats
                cursor.execute('SELECT COUNT(DISTINCT keyword) FROM geographic_spread')
                stats['keywords_with_geo_data'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

# Test the cache manager
if __name__ == "__main__":
    cache_manager = EnhancedCacheManager()
    
    # Test caching
    test_posts = [
        {
            'id': 'test_1',
            'text': 'Test post about climate change',
            'author_id': 'user_1',
            'author_name': 'Test User',
            'created_at': datetime.now(),
            'public_metrics': {'like_count': 100, 'retweet_count': 50}
        }
    ]
    
    cache_manager.cache_viral_content("climate change", test_posts)
    
    # Test timeline analytics
    analytics = cache_manager.get_timeline_analytics("climate change", "24h")
    print(f"Timeline analytics: {analytics}")
    
    # Show cache stats
    stats = cache_manager.get_cache_stats()
    print(f"Cache stats: {stats}")