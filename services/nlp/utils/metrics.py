"""
Metrics collection utilities
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Simple metrics collector"""
    
    def __init__(self):
        self.stats = {
            'total_requests': 0,
            'total_texts_processed': 0,
            'total_processing_time_ms': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }
    
    async def record_batch_analysis(self, text_count: int, processing_time_ms: float, cache_hits: int, cache_misses: int):
        """Record batch analysis metrics"""
        self.stats['total_requests'] += 1
        self.stats['total_texts_processed'] += text_count
        self.stats['total_processing_time_ms'] += processing_time_ms
        self.stats['cache_hits'] += cache_hits
        self.stats['cache_misses'] += cache_misses
    
    async def record_error(self):
        """Record an error"""
        self.stats['errors'] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        avg_processing_time = 0
        if self.stats['total_texts_processed'] > 0:
            avg_processing_time = self.stats['total_processing_time_ms'] / self.stats['total_texts_processed']
        
        cache_hit_rate = 0
        total_cache_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = self.stats['cache_hits'] / total_cache_requests
        
        return {
            **self.stats,
            'average_processing_time_ms': avg_processing_time,
            'cache_hit_rate': cache_hit_rate
        }