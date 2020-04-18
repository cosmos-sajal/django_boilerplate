from django.core.cache import cache


class CacheAdapter:
    """
    A class which serves as an adapter for Cache
    """

    def get(self, key):
        """
        Returns the set value
        """
        return cache.get(key)

    def set(self, key, value, timeout=None):
        """
        Expiration time is in seconds, sets the value
        in cache
        """
        cache.set(key, value, timeout)

    def delete(self, key):
        """
        Deletes a specific key from cache
        """
        cache.delete(key)
