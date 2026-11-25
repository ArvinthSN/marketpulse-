import asyncio
import random


async def reconnect_with_backoff(operation, max_attempts: int = 5, base_delay: float = 1.0):
    last_error = None
    for attempt in range(max_attempts):
        try:
            return await operation()
        except Exception as exc:
            last_error = exc
            if attempt + 1 >= max_attempts:
                break
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay * random.uniform(0.75, 1.25))
    raise RuntimeError('Provider reconnect failed') from last_error
