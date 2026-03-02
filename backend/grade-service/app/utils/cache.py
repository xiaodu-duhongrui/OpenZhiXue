from app.redis_client import get_redis
from app.config import settings
from typing import Optional, Any
import json


class CacheService:
    def __init__(self):
        self.prefix = "grade_service:"
    
    def _get_key(self, key: str) -> str:
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        redis = get_redis()
        if not redis:
            return None
        
        value = await redis.get(self._get_key(key))
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        redis = get_redis()
        if not redis:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await redis.set(self._get_key(key), value, ex=expire)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        redis = get_redis()
        if not redis:
            return False
        
        try:
            await redis.delete(self._get_key(key))
            return True
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        redis = get_redis()
        if not redis:
            return 0
        
        try:
            keys = await redis.keys(self._get_key(pattern))
            if keys:
                return await redis.delete(*keys)
            return 0
        except Exception:
            return 0
    
    async def get_or_set(self, key: str, factory, expire: int = 3600) -> Any:
        value = await self.get(key)
        if value is not None:
            return value
        
        value = await factory()
        if value is not None:
            await self.set(key, value, expire)
        return value


cache = CacheService()
