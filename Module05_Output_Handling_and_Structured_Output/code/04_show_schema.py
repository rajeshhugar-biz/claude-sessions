"""Offline: see the JSON schema the SDK will send for the Invoice model."""
import json
from anthropic import transform_schema
from invoice_models import Invoice

original = Invoice.model_json_schema()
sent = transform_schema(Invoice)  # what messages.parse() sends as the format

print("required:", sent["required"])
print("optional:", sorted(set(sent["properties"]) - set(sent["required"])))
print("quantity before:", original["$defs"]["LineItem"]["properties"]["quantity"])
print("quantity after: ", sent["$defs"]["LineItem"]["properties"]["quantity"])
print("due_date:", sent["properties"]["due_date"])
print(json.dumps(sent, indent=2)[:600], "...")
