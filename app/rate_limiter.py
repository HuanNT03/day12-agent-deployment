import time
import json
import logging
from collections import defaultdict, deque
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Redis Connection setup
USE_REDIS = False
_redis = None
_rate_windows: dict[str, deque] = defaultdict(deque)

if settings.redis_url:
    try:
        import redis
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
        USE_REDIS = True
        logger.info(json.dumps({"event": "redis_connected_rate_limiter", "msg": "Successfully connected to Redis for Rate Limiting"}))
    except Exception as e:
        logger.warning(json.dumps({"event": "redis_failed_rate_limiter", "msg": f"Failed to connect to Redis for Rate Limiting: {str(e)}"}))


def check_rate_limit(key: str):
    now = time.time()
    limit = settings.rate_limit_per_minute
    window = 60
    
    if USE_REDIS:
        redis_key = f"rate_limit:{key}"
        try:
            pipe = _redis.pipeline()
            pipe.zremrangebyscore(redis_key, 0, now - window)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(now): now})
            pipe.expire(redis_key, window)
            _, current_count, _, _ = pipe.execute()
            
            if current_count >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} req/min",
                    headers={"Retry-After": "60"},
                )
        except Exception as e:
            # Fallback to memory if redis fails during check
            logger.warning(json.dumps({"event": "redis_check_failed_rate_limiter", "msg": f"Redis rate limit check failed, falling back to memory: {str(e)}"}))
            _check_rate_limit_memory(key, now, limit, window)
    else:
        _check_rate_limit_memory(key, now, limit, window)


def _check_rate_limit_memory(key: str, now: float, limit: int, window: int):
    window_deque = _rate_windows[key]
    while window_deque and window_deque[0] < now - window:
        window_deque.popleft()
    if len(window_deque) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} req/min",
            headers={"Retry-After": "60"},
        )
    window_deque.append(now)
