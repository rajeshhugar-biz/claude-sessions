def handle(response):
    reason = response.stop_reason
    if reason == "end_turn":
        return "done"                       # normal finish
    if reason == "max_tokens":
        return "truncated: raise max_tokens or ask for less"
    if reason == "stop_sequence":
        return f"hit stop sequence {response.stop_sequence!r}"
    if reason == "tool_use":
        return "run the requested tool, send tool_result back"
    if reason == "pause_turn":
        return "long server-tool turn paused: resend to continue"
    if reason == "refusal":
        return "declined for safety: don't retry the same request"
    if reason == "model_context_window_exceeded":
        return "context full: trim or compact history"
    return f"unknown stop_reason {reason}: log it"   # future-proof
