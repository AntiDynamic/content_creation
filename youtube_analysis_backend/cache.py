"""
Simple in-memory cache (no Redis required)
"""
from typing import Optional, Any
import time

class SimpleCacheManager:
    """Simple in-memory cache for development"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            # Check if expired
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL"""
        try:
            self._cache[key] = value
            self._expiry[key] = time.time() + ttl
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._cache
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL"""
        if key in self._expiry:
            remaining = int(self._expiry[key] - time.time())
            return max(0, remaining)
        return -1
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
    
    # Specialized methods
    def get_channel_analysis(self, channel_id: str) -> Optional[dict]:
        """Get cached channel analysis"""
        return self.get(f"channel_analysis:{channel_id}")
    
    def set_channel_analysis(self, channel_id: str, analysis: dict) -> bool:
        """Cache channel analysis"""
        return self.set(f"channel_analysis:{channel_id}", analysis, 604800)
    
    def get_channel_metadata(self, channel_id: str) -> Optional[dict]:
        """Get cached channel metadata"""
        return self.get(f"channel_meta:{channel_id}")
    
    def set_channel_metadata(self, channel_id: str, metadata: dict) -> bool:
        """Cache channel metadata"""
        return self.set(f"channel_meta:{channel_id}", metadata, 604800)
    
    def get_url_mapping(self, url_hash: str) -> Optional[str]:
        """Get channel ID from URL hash"""
        return self.get(f"channel_url:{url_hash}")
    
    def set_url_mapping(self, url_hash: str, channel_id: str) -> bool:
        """Cache URL mapping"""
        return self.set(f"channel_url:{url_hash}", channel_id, 86400)
    
    def invalidate_channel(self, channel_id: str):
        """Invalidate channel cache"""
        self.delete(f"channel_analysis:{channel_id}")
        self.delete(f"channel_meta:{channel_id}")

# Global cache instance
cache = SimpleCacheManager()
