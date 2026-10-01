import anthropic
from dotenv import load_dotenv
load_dotenv()  # loads ANTHROPIC_API_KEY from .env

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain an LLM in one sentence."}
    ],
)

for block in response.content:      # read blocks by type
    if block.type == "text":
        print(block.text)

print(response.stop_reason)  # end_turn
print(response.usage)        # input_tokens, output_tokens ...