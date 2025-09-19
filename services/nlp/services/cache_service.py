"""
Simplified cache service (in-memory for now)
"""
import logging
import hashlib
import json
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

class CacheService:
    """Simple in-memory cache service"""
    
    def __init__(self):
        self.cache = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize cache service"""
        self.initialized = True
        logger.info("Cache service initialized (in-memory)")
    
    async def close(self):
        """Close cache service"""
        self.cache.clear()
        logger.info("Cache service closed")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def get_batch_results(self, texts: List[str]) -> List[Optional[Any]]:
        """Get cached results for batch of texts"""
        results = []
        for text in texts:
            key = self._get_cache_key(text)
            result = self.cache.get(key)
            results.append(result)
        return results
    
    async def cache_batch_results(self, texts: List[str], results: List[Any]):
        """Cache results for batch of texts"""
        for text, result in zip(texts, results):
            key = self._get_cache_key(text)
            self.cache[key] = result
        
        # Simple cache size management
        if len(self.cache) > 1000:
            # Remove oldest 100 entries (simple FIFO)
            keys_to_remove = list(self.cache.keys())[:100]
            for key in keys_to_remove:
                del self.cache[key]