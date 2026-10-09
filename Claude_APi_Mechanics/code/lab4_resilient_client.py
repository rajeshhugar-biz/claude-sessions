"""Lab 4: a resilient wrapper - retries, timeouts, logging, and a fallback model."""
import logging, time
import anthropic

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("claude")

client = anthropic.Anthropic(max_retries=3, timeout=60.0)
PRIMARY, FALLBACK = "claude-sonnet-5-5", "claude-haiku-4-5-20251001"

def ask(prompt, model=PRIMARY):
    t0 = time.perf_counter()
    try:
        r = client.messages.create(model=model, max_tokens=512,
                                   messages=[{"role": "user", "content": prompt}])
    except anthropic.BadRequestError as e:
        log.error("400 - not retrying: %s", e.message)
        raise
    except anthropic.APIStatusError as e:
        log.warning("status %s (request %s) after retries", e.status_code, e.request_id)
        if e.status_code == 529 and model != FALLBACK:
            log.info("overloaded - falling back to %s", FALLBACK)
            return ask(prompt, FALLBACK)
        raise
    log.info("ok model=%s request=%s %.2fs in=%d out=%d stop=%s", model,
             r._request_id, time.perf_counter() - t0,
             r.usage.input_tokens, r.usage.output_tokens, r.stop_reason)
    return "".join(b.text for b in r.content if b.type == "text")

if __name__ == "__main__":
    print(ask("Give me one tip for writing clean Python."))
