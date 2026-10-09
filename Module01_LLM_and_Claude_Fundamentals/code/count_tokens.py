import anthropic
client = anthropic.Anthropic()

text = "Tokenization isn't magic!"

for model in ["claude-haiku-4-5-20251001",
              "claude-sonnet-5-5",
              "claude-opus-5-5"]:
    count = client.messages.count_tokens(
        model=model,
        messages=[{"role": "user", "content": text}],
    )
    print(model, count.input_tokens)