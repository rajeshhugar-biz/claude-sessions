"""Test the concurrency pattern offline with a fake client. No API key needed."""
import asyncio
import random

class FakeRateLimit(Exception):
    pass

class FakeClient:
    """Slow, and rate-limited 20% of the time. Records peak concurrency."""
    def __init__(self, fail_rate: float = 0.2, seed: int = 7):
        self.rng, self.fail_rate = random.Random(seed), fail_rate
        self.calls = self.in_flight = self.peak = 0

    async def create(self, prompt: str) -> str:
        self.calls += 1
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        try:
            await asyncio.sleep(self.rng.uniform(0.01, 0.05))
            if self.rng.random() < self.fail_rate:
                raise FakeRateLimit("429")
            return prompt.upper()
        finally:
            self.in_flight -= 1

async def run_all(client, prompts, limit=5, max_attempts=8):
    sem = asyncio.Semaphore(limit)
    async def one(p):
        for attempt in range(max_attempts):
            try:
                async with sem:
                    return await client.create(p)
            except FakeRateLimit:
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(random.uniform(0, 0.01 * 2 ** attempt))
    return await asyncio.gather(*(one(p) for p in prompts))

if __name__ == "__main__":
    fake = FakeClient()
    out = asyncio.run(run_all(fake, [f"ticket {i}" for i in range(30)]))
    print(len(out), "results | calls:", fake.calls, "| peak in flight:", fake.peak)
    assert len(out) == 30 and fake.peak <= 5 and fake.calls > 30
