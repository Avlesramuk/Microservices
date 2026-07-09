import time
import redis


# Token bucket configuration
MAX_TOKENS = 10
REFILL_RATE = 10 / 60   # tokens per second


redis_client = redis.Redis(
    host="redis-cache",
    port=6379,
    decode_responses=True
)


def is_allowed(client_id: str):

    key = f"rate_limit:{client_id}"

    now = time.time()

    try:

        bucket = redis_client.hgetall(key)

        # First request
        if not bucket:

            redis_client.hset(
                key,
                mapping={
                    "tokens": MAX_TOKENS - 1,
                    "timestamp": now
                }
            )

            redis_client.expire(
                key,
                120
            )

            return True


        tokens = float(bucket["tokens"])
        last_time = float(bucket["timestamp"])


        # Calculate refill
        elapsed = now - last_time

        refill = elapsed * REFILL_RATE

        tokens = min(
            MAX_TOKENS,
            tokens + refill
        )


        # No tokens available
        if tokens < 1:

            return False


        # Consume token

        tokens -= 1


        redis_client.hset(
            key,
            mapping={
                "tokens": tokens,
                "timestamp": now
            }
        )

        return True


    except Exception as e:

        print(
            "Redis unavailable:",
            e
        )

        # Fail open strategy
        return True