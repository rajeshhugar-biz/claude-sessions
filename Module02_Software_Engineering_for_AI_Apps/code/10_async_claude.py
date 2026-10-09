import asyncio
import random
from dotenv import load_dotenv

load_dotenv()

import anthropic

client = anthropic.AsyncAnthropic(max_retries=0)  # this file owns the retry policy
LIMIT = asyncio.Semaphore(5)                       # at most 5 requests in flight

def retryable(e: Exception) -> bool:
    if isinstance(e, anthropic.APIConnectionError):   # includes timeouts
        return True
    return isinstance(e, anthropic.APIStatusError) and (
        e.status_code in (408, 409, 429) or e.status_code >= 500)

async def summarise(text: str, max_attempts: int = 5) -> str:
    for attempt in range(max_attempts):
        try:
            async with LIMIT:                      # wait for a free slot
                msg = await client.messages.create(
                    model="claude-haiku-4-5-20251001", max_tokens=150,
                    messages=[{"role": "user", "content": f"Summarise: {text}"}])
            return "".join(b.text for b in msg.content if b.type == "text")
        except anthropic.APIError as e:
            if not retryable(e) or attempt == max_attempts - 1:
                raise
            resp = getattr(e, "response", None)
            wait = resp.headers.get("retry-after") if resp is not None else None
            await asyncio.sleep(float(wait) if wait else random.uniform(0, 2**attempt))

async def main() -> None:
    notes = [f"Release note {i}: fixed bug #{100 + i}." for i in range(20)]
    results = await asyncio.gather(*(summarise(n) for n in notes),
                                   return_exceptions=True)
    for note, r in zip(notes, results):
        print("FAILED" if isinstance(r, Exception) else "ok    ", note, "->", r)

asyncio.run(main())
