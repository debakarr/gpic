import random
import time
from dataclasses import dataclass


@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0


def calculate_backoff(attempt: int, config: RetryConfig) -> float:
    delay = config.initial_delay * (config.backoff_factor ** attempt)
    delay = min(delay, config.max_delay)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter


def should_retry(status_code: int) -> bool:
    return status_code >= 500 or status_code == 429
