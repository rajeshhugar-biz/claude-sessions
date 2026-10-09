"""Demo 07: replacing prefill. Opus 5.5 rejects a prefilled last assistant turn."""
import json
import anthropic

client = anthropic.Anthropic()
ticket = "<ticket>Charged twice for Pro this month, please refund one.</ticket>"

# OLD - returns 400 on Claude 4.6+ models, including Opus 5.5:
# messages=[{"role": "user", "content": ...}, {"role": "assistant", "content": "{"}]

# NEW 1: structured outputs force the reply to match a JSON schema.
schema = {"type": "object", "additionalProperties": False, "required": ["label"],
          "properties": {"label": {"type": "string", "enum": [
              "billing", "technical", "account", "content", "other"]}}}
r = client.messages.create(
    model="claude-opus-5-5", max_tokens=2048,
    output_config={"format": {"type": "json_schema", "schema": schema}},
    messages=[{"role": "user", "content": f"Classify this ticket.\n{ticket}"}])
text = "".join(b.text for b in r.content if b.type == "text")
print("label:", json.loads(text)["label"])

# NEW 2: no preamble -> ask for it directly, then strip any leftover.
r = client.messages.create(
    model="claude-opus-5-5", max_tokens=2048,
    system="Respond directly without preamble. Do not start with 'Here is'.",
    messages=[{"role": "user", "content": f"Summarise in one line.\n{ticket}"}])
text = "".join(b.text for b in r.content if b.type == "text").strip()
print("summary:", text.removeprefix("Here is the summary:").strip())
