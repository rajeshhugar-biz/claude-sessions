"""tool_choice: auto, none, any, tool - and which models reject forcing."""
import anthropic

from toolbox import pick

NO_FORCED_TOOL = {"claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1"}


def checked_choice(model, choice):
    """Fail fast in your code instead of getting a 400 from the API."""
    if choice["type"] in ("any", "tool") and model in NO_FORCED_TOOL:
        raise ValueError(f"{model} supports tool_choice auto/none only; "
                         "use auto + strict tools or structured outputs")
    return choice


def ask(client, model, choice, question):
    r = client.messages.create(
        model=model, max_tokens=1024, tools=pick("get_weather", "calculate"),
        tool_choice=checked_choice(model, choice),
        messages=[{"role": "user", "content": question}])
    calls = [f"{b.name}({b.input})" for b in r.content if b.type == "tool_use"]
    print(f"{model} {choice} -> {r.stop_reason} {calls}")


if __name__ == "__main__":
    client = anthropic.Anthropic()
    q = "Is it raining in Mumbai, and what is 18% of 2340?"
    ask(client, "claude-sonnet-5-5", {"type": "auto"}, q)   # Claude decides
    ask(client, "claude-sonnet-5-5", {"type": "none"}, q)   # text only
    ask(client, "claude-sonnet-5-5",                        # one call per turn
        {"type": "auto", "disable_parallel_tool_use": True}, q)
    ask(client, "claude-haiku-4-5-20251001",                # forced, older model
        {"type": "tool", "name": "get_weather"}, q)
    try:
        ask(client, "claude-opus-5-5", {"type": "any"}, q)
    except ValueError as e:
        print("Blocked:", e)
