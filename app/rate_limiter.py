from fastapi import Request, HTTPException
from .cache import redis_client

RATE_LIMIT = 10
WINDOW = 60

def rate_limit(request: Request):

    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    try:
        current = redis_client.get(key)

        if current is None:
            redis_client.set(
                key,
                RATE_LIMIT - 1,
                ex=WINDOW
            )
            return

        current = int(current)

        if current <= 0:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )

        redis_client.decr(key)

    except Exception:
        # Redis failure → fail open
        return