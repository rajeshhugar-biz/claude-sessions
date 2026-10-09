"""Validate JSON from a model before your code trusts it."""
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

class Triage(BaseModel):
    category: Literal["billing", "login", "bug", "other"]
    priority: int = Field(ge=1, le=4)
    summary: str = Field(max_length=120)
    needs_human: bool = False

good = '{"category": "login", "priority": 2, "summary": "Reset link expired"}'
bad = '{"category": "Login", "priority": 7}'

t = Triage.model_validate_json(good)
print(t.category, t.priority, t.needs_human)    # typed, default filled in

try:
    Triage.model_validate_json(bad)
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], "->", err["msg"])

print(Triage.model_json_schema()["required"])
