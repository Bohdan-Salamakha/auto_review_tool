import json
import logging
from typing import Optional

import redis.asyncio as redis

from auto_review_tool.core.config import settings


class RedisClient:
    def __init__(self) -> None:
        self.redis_url = settings.REDIS_URL
        self.redis = None
        self.is_connected = False

    async def connect(self) -> None:
        """Connecting to Redis."""
        try:
            self.redis = await redis.from_url(self.redis_url)
            self.is_connected = True
            logging.info("Redis is connected")
        except Exception as e:
            self.is_connected = False
            logging.warning(f"Failed to connect to Redis: {e}")

    async def close(self) -> None:
        """Close the connection to Redis."""
        if self.redis:
            await self.redis.aclose()
            logging.info("Redis connection closed")

    async def get(self, key: str) -> Optional[dict]:
        """Get data from cache."""
        if not self.is_connected:
            return None
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logging.error(f"Error getting data from Redis: {e}")
            return None

    async def set(self, key: str, value: dict, expire: int = 3600) -> None:
        """Save data to cache."""
        if not self.is_connected:
            return None
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logging.error(f"Error saving data to Redis: {e}")


redis_client = RedisClient()
