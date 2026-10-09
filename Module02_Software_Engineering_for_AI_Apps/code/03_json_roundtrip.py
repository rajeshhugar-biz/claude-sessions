"""Serialise Python -> JSON text and back. Watch the types that change."""
import json
from datetime import datetime, timezone
from decimal import Decimal

record = {
    "ticket_id": 1042,
    "subject": "Can't log in from the café",
    "tags": ("login", "wifi"),             # tuple
    "score": Decimal("0.875"),             # Decimal is not a JSON type
    "created": datetime(2026, 10, 8, 9, 30, tzinfo=timezone.utc),
}

def to_jsonable(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)                  # keep the exact digits as text
    raise TypeError(f"not JSON serialisable: {type(value).__name__}")

text = json.dumps(record, default=to_jsonable, ensure_ascii=False)
print(text)

back = json.loads(text)
print(type(back["tags"]).__name__, type(back["created"]).__name__)
# list str: JSON has no tuple or datetime, so you must convert them back
