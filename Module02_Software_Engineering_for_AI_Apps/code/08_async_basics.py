"""Sequential vs concurrent: ten fake API calls that each wait one second."""
import asyncio
import time

async def fake_call(i: int) -> str:
    await asyncio.sleep(1.0)               # waiting on the network; CPU is free
    return f"answer {i}"

async def sequential() -> list[str]:
    return [await fake_call(i) for i in range(10)]

async def concurrent() -> list[str]:
    return await asyncio.gather(*(fake_call(i) for i in range(10)))

for runner in (sequential, concurrent):
    t0 = time.perf_counter()
    results = asyncio.run(runner())
    print(f"{runner.__name__:<10} {len(results)} results "
          f"in {time.perf_counter() - t0:.1f}s")
