"""
Caching utilities for production API
"""
import redis
import json
import hashlib
import logging
from typing import Optional, Any
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager for predictions."""
    
    def __init__(self):
        """Initialize Redis connection if enabled."""
        self.enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.redis_client = None
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "redis"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    db=int(os.getenv("REDIS_DB", 0)),
                    password=os.getenv("REDIS_PASSWORD"),
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.enabled = False
                self.redis_client = None
    
    def _generate_key(self, data: dict) -> str:
        """Generate cache key from prediction input."""
        # Sort dict for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return f"pred:{hashlib.sha256(sorted_data.encode()).hexdigest()}"
    
    def get(self, data: dict) -> Optional[dict]:
        """
        Get cached prediction result.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cached prediction result or None
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._generate_key(data)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.info(f"Cache hit for key: {key[:16]}...")
                return json.loads(cached)
            
            logger.debug(f"Cache miss for key: {key[:16]}...")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, data: dict, result: dict, ttl: int = 3600):
        """
        Cache prediction result.
        
        Args:
            data: Input data dictionary
            result: Prediction result to cache
            ttl: Time to live in seconds (default 1 hour)
        """
        if not self.enabled or not self.redis_client:
            return
        
        try:
            key = self._generate_key(data)
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(result)
            )
            logger.debug(f"Cached result for key: {key[:16]}...")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self):
        """Clear all cached predictions."""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            # Find all prediction keys
            keys = self.redis_client.keys("pred:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached predictions")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
                )
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache instance
cache_manager = CacheManager()
