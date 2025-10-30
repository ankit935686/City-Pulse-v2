import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache implementation
class SimpleCache:
    def __init__(self, default_ttl=3600):  # Default TTL: 1 hour
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key):
        """Get a value from the cache if it exists and hasn't expired"""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if item['expires_at'] < time.time():
            # Item has expired, remove it
            del self.cache[key]
            return None
        
        return item['value']
    
    def set(self, key, value, ttl=None):
        """Set a value in the cache with an expiration time"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
    
    def delete(self, key):
        """Delete a key from the cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all items from the cache"""
        self.cache = {}

# Create cache instances with different TTLs
maps_api_cache = SimpleCache(default_ttl=3600)  # 1 hour for general Maps API responses
working_api_key_cache = SimpleCache(default_ttl=1800)  # 30 minutes for working API keys

# Decorator for caching function results
def cached(cache_instance, key_prefix=''):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ':'.join(key_parts)
            
            # Try to get from cache first
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Cache miss, call the function
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache if result is not None
            if result is not None:
                cache_instance.set(cache_key, result)
            
            return result
        return wrapper
    return decorator