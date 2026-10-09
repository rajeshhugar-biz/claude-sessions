"""Decide what to do with an HTTP status code from the Claude API."""

def action_for(status: int) -> str:
    if 200 <= status < 300:
        return "success"
    if status in (408, 409, 429) or status >= 500:
        return "retry with backoff"        # transient: may succeed later
    if status == 413:
        return "shrink the request"
    if status in (401, 403):
        return "fix the key or permissions"
    if status == 402:
        return "fix billing"
    if 400 <= status < 500:
        return "fix the request"           # same request = same error
    return "unexpected: log it"

if __name__ == "__main__":
    for code in (200, 400, 401, 404, 413, 429, 500, 529):
        print(code, "->", action_for(code))
    assert action_for(529) == "retry with backoff"
    assert action_for(400) == "fix the request"
