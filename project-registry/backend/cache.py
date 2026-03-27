import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("REDIS_URL")
# Handle different Redis URL formats if needed
if REDIS_URL and REDIS_URL.startswith("rediss://"):
    # Upstash often provides rediss:// links
    pass

redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except Exception as e:
        print(f"Warning: Failed to connect to Redis. Running without caching. Error: {e}")

def get_cache(key: str):
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"Redis get error: {e}")
    return None

def set_cache(key: str, value, expire_time: int = 3600):
    if not redis_client:
        return
    try:
        redis_client.setex(key, expire_time, json.dumps(value))
    except Exception as e:
        print(f"Redis set error: {e}")

def invalidate_cache(key: str):
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Redis delete error: {e}")
