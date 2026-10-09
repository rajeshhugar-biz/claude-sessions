"""Ask Claude for JSON that matches a Pydantic model (structured outputs)."""
from typing import Literal
from dotenv import load_dotenv

load_dotenv()  # load ANTHROPIC_API_KEY from .env file if present



import anthropic
from pydantic import BaseModel

class Triage(BaseModel):
    category: Literal["billing", "login", "bug", "other"]
    priority: int
    summary: str

client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    system="Triage support tickets for Nimbus Learning. Priority 1 is most urgent.",
    messages=[{"role": "user", "content": "Ticket: I was charged twice this month!"}],
    output_format=Triage,                 # SDK sends output_config.format for you
)

if response.stop_reason != "end_turn":
    raise RuntimeError(f"incomplete output: {response.stop_reason}")
triage = response.parsed_output           # a Triage instance, already validated
print(triage.model_dump_json(indent=2))
