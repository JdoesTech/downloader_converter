from collections import defaultdict
import time

from fastapi import HTTPException, Request

_AUTH_RATE_BUCKETS: dict[str, list[float]] = defaultdict(list)
_AUTH_RATE_WINDOW_SECONDS = 60
_AUTH_RATE_MAX_REQUESTS = 10


async def auth_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _AUTH_RATE_BUCKETS[client_host]
    _AUTH_RATE_BUCKETS[client_host] = [
        timestamp for timestamp in bucket if now - timestamp < _AUTH_RATE_WINDOW_SECONDS
    ]

    if len(_AUTH_RATE_BUCKETS[client_host]) >= _AUTH_RATE_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

    _AUTH_RATE_BUCKETS[client_host].append(now)
