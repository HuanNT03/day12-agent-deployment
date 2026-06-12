import time
import json
import logging
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Redis Connection setup
USE_REDIS = False
_redis = None
_daily_cost = 0.0
_cost_reset_day = time.strftime("%Y-%m-%d")

if settings.redis_url:
    try:
        import redis
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
        USE_REDIS = True
        logger.info(json.dumps({"event": "redis_connected_cost_guard", "msg": "Successfully connected to Redis for Cost Guard"}))
    except Exception as e:
        logger.warning(json.dumps({"event": "redis_failed_cost_guard", "msg": f"Failed to connect to Redis for Cost Guard: {str(e)}"}))


def check_and_record_cost(key: str, input_tokens: int, output_tokens: int):
    global _daily_cost, _cost_reset_day
    today = time.strftime("%Y-%m-%d")
    cost = (input_tokens / 1000) * 0.0003 + (output_tokens / 1000) * 0.0006
    
    if USE_REDIS:
        cost_key = f"cost:{key}:{today}"
        try:
            current_cost_str = _redis.get(cost_key)
            current_cost = float(current_cost_str) if current_cost_str else 0.0
            
            if current_cost >= settings.daily_budget_usd:
                raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
                
            pipe = _redis.pipeline()
            pipe.incrbyfloat(cost_key, cost)
            pipe.expire(cost_key, 24 * 3600 * 2) # lưu trong 2 ngày
            pipe.execute()
        except HTTPException:
            raise
        except Exception as e:
            # Fallback to memory if redis fails during check
            logger.warning(json.dumps({"event": "redis_check_failed_cost_guard", "msg": f"Redis cost check failed, falling back to memory: {str(e)}"}))
            _check_and_record_cost_memory(today, cost)
    else:
        _check_and_record_cost_memory(today, cost)


def _check_and_record_cost_memory(today: str, cost: float):
    global _daily_cost, _cost_reset_day
    if today != _cost_reset_day:
        _daily_cost = 0.0
        _cost_reset_day = today
    if _daily_cost >= settings.daily_budget_usd:
        raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
    _daily_cost += cost


def get_daily_cost(key: str) -> float:
    if USE_REDIS:
        today = time.strftime("%Y-%m-%d")
        cost_key = f"cost:{key}:{today}"
        try:
            cost_val = _redis.get(cost_key)
            return float(cost_val) if cost_val else 0.0
        except Exception:
            return _daily_cost
    else:
        return _daily_cost
