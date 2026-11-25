import random
import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar('T')


def retry_with_backoff(operation: Callable[[], T], max_attempts: int = 3, base_delay: float = 0.5,
                       jitter_ratio: float = 0.25, retryable_exceptions: tuple[type[BaseException], ...] = (Exception,),
                       sleep: Callable[[float], None] = time.sleep) -> T:
    if max_attempts < 1:
        raise ValueError('max_attempts must be at least 1')
    last_error: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return operation()
        except retryable_exceptions as exc:
            last_error = exc
            if attempt + 1 >= max_attempts:
                break
            exponential = base_delay * (2 ** attempt)
            jitter = random.uniform(-jitter_ratio * exponential, jitter_ratio * exponential)
            sleep(max(0.0, exponential + jitter))
    assert last_error is not None
    raise last_error
