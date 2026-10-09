"""Server tools together: web fetch reads a page, code execution does the maths."""
import anthropic

client = anthropic.Anthropic()
URL = "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"
tools = [
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 2,
     "allowed_domains": ["platform.claude.com"],      # limit exfiltration risk
     "citations": {"enabled": True}, "max_content_tokens": 30000},
    {"type": "code_execution_20260120", "name": "code_execution"},  # sandbox
]
# web_fetch only opens URLs already in the conversation: put it in the user turn
question = (f"Fetch {URL}. From the tool-use system prompt token table, "
            "use code to find the mean tokens for tool_choice auto/none.")
r = client.messages.create(
    model="claude-sonnet-5-5", max_tokens=4096, tools=tools,
    messages=[{"role": "user", "content": question}])

print("stop_reason:", r.stop_reason)               # pause_turn? resend as-is
for block in r.content:
    print("-", block.type, getattr(block, "name", ""))
print("".join(b.text for b in r.content if b.type == "text"))
print("container:", r.container.id if r.container else None)  # reusable
