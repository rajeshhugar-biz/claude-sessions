from typing import Literal, Optional
import anthropic
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    category: Literal["billing", "bug", "how_to", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(description="One sentence, under 20 words")
    order_id: Optional[str]  # required key, but the value may be null


client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Triage: the export button crashes "
               "the app every time since Monday's update."}],
    output_format=Ticket,  # SDK builds output_config.format from the model
)
ticket = response.parsed_output  # a Ticket instance, or None
print(response.stop_reason, type(ticket).__name__)
print(ticket.model_dump_json(indent=2))
