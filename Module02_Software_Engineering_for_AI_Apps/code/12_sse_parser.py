"""Parse a raw server-sent events (SSE) stream by hand, the way an SDK does."""
import json
from pathlib import Path

def parse_sse(lines):
    event, data = None, []
    for line in lines:
        line = line.rstrip("\r\n")
        if line == "":                         # blank line = end of one event
            if data:
                yield event, json.loads("\n".join(data))
            event, data = None, []
        elif line.startswith(":"):             # comment / keep-alive: ignore
            continue
        elif line.startswith("event:"):
            event = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data.append(line[len("data:"):].strip())

if __name__ == "__main__":
    raw = Path(__file__).with_name("sse_sample.txt").read_text().splitlines()
    known = {"message_start", "content_block_start", "content_block_delta",
             "content_block_stop", "message_delta", "message_stop", "ping"}
    text = []
    for event, payload in parse_sse(raw + [""]):
        if event not in known:
            print("unknown event ignored:", event)
        elif event == "content_block_delta":
            if payload["delta"]["type"] == "text_delta":
                text.append(payload["delta"]["text"])
        elif event == "message_delta":
            print("stop_reason:", payload["delta"]["stop_reason"])
    print("text:", "".join(text))
