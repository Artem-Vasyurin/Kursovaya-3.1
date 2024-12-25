import aioredis

class RedisBroker:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)

    async def send_message(self, channel: str, message: str):
        if not self.redis:
            raise ConnectionError("Redis is not connected")
        await self.redis.publish(channel, message)

    async def close(self):
        if self.redis:
            await self.redis.close()
