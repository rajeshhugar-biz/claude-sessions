import anthropic

client = anthropic.Anthropic()

with open("policy_handbook.txt") as f:        # a long, stable document
    handbook = f.read()

def ask(question):
    r = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=512,
        system=[
            {"type": "text", "text": "You answer HR questions using the handbook."},
            {"type": "text", "text": handbook,
             "cache_control": {"type": "ephemeral"}},     # breakpoint: cache up to here
        ],
        messages=[{"role": "user", "content": question}],
    )
    u = r.usage
    print(f"write={u.cache_creation_input_tokens} "
          f"read={u.cache_read_input_tokens} uncached={u.input_tokens}")
    return r

ask("How many casual leaves do I get?")      # 1st call: cache WRITE
ask("What is the notice period?")            # within 5 min: cache READ
