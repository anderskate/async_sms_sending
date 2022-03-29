import asyncio
import aioredis


async def main():
    redis = aioredis.from_url("redis://localhost", decode_responses=True)
    await redis.set("my-number", "79220353847")
    value = await redis.get("my-number")
    print(value)


asyncio.run(main())
