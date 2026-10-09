"""Exponential backoff with full jitter, plus a small async retry helper."""
import asyncio
import random

BASE, CAP = 0.5, 8.0                       # seconds

def backoff_delay(attempt: int, rng=random.random) -> float:
    """Random wait between 0 and min(CAP, BASE * 2**attempt)."""
    return rng() * min(CAP, BASE * 2 ** attempt)

class TransientError(Exception):
    """Stands in for 429, 5xx and 529 responses."""

async def with_retries(make_call, max_attempts: int = 5):
    for attempt in range(max_attempts):
        try:
            return await make_call()
        except TransientError:
            if attempt == max_attempts - 1:
                raise                      # out of attempts: let the caller decide
            await asyncio.sleep(backoff_delay(attempt))

if __name__ == "__main__":
    for a in range(7):
        print(f"attempt {a}: ceiling {min(CAP, BASE * 2 ** a):4.1f}s, "
              f"this time {backoff_delay(a):.2f}s")
