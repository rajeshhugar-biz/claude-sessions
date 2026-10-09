"""Server tool: web search. Anthropic runs it; you handle pause_turn."""
import anthropic

client = anthropic.Anthropic()
WEB_SEARCH = {
    "type": "web_search_20260209",        # dynamic filtering (Claude 4.6+)
    "name": "web_search",
    "max_uses": 3,                         # cap searches ($10 per 1,000)
    "allowed_domains": ["imd.gov.in", "mausam.imd.gov.in"],  # or blocked_domains
    "user_location": {"type": "approximate", "city": "Pune",
                      "country": "IN", "timezone": "Asia/Kolkata"},
}
messages = [{"role": "user", "content":
             "What is the latest monsoon update for Maharashtra? Cite sources."}]

searches = 0
for _ in range(5):                         # cap continuations
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=4096,
                               tools=[WEB_SEARCH], messages=messages)
    searches += getattr(r.usage.server_tool_use, "web_search_requests", 0)
    if r.stop_reason != "pause_turn":
        break
    messages.append({"role": "assistant", "content": r.content})  # resend as-is

for block in r.content:
    if block.type == "server_tool_use":
        print(f"{block.name}:", block.input)    # e.g. the search query
    elif block.type == "text":
        print(block.text, end="")
        for c in block.citations or []:
            print(f" [{c.title} - {c.url}]", end="")
print("\nsearches billed:", searches)
