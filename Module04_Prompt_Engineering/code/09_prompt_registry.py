"""Demo 09: versioned prompts - what gets logged with every request (no API key)."""
import json
from harness.registry import build_request, load_prompt

ticket = "Mera account login nahi ho raha, OTP nahi aa raha."

for version in ["v1", "v2", "v3", "v4"]:
    prompt = load_prompt(version)
    request = build_request(prompt, ticket)
    size = len(request.get("system", "")) + len(request["messages"][0]["content"])
    print(f"{prompt['id']:24} model={request['model']}  prompt chars={size}")

# Log the prompt id next to every output so any result can be traced back
# to the exact prompt text and model that produced it.
v4 = load_prompt("v4")
print(json.dumps(build_request(v4, ticket)["messages"], ensure_ascii=False))
