"""Lint tool definitions against the docs' best practices. Runs offline."""
import re

from toolbox import TOOLS

VAGUE_PARAMS = {"id", "user", "data", "value", "input", "query"}


def lint_tool(tool):
    problems = []
    name, desc = tool.get("name", ""), tool.get("description", "")
    schema = tool.get("input_schema", {})
    props = schema.get("properties", {})
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", name):
        problems.append("name must match ^[a-zA-Z0-9_-]{1,128}$")
    if len(re.findall(r"[.!?](\s|$)", desc)) < 3:
        problems.append("description: aim for at least 3-4 sentences")
    if not re.search(r"\b(use|when)\b", desc, re.I):
        problems.append("description: say WHEN to use the tool")
    for p in schema.get("required", []):
        if p not in props:
            problems.append(f"required '{p}' is not in properties")
    for p, spec in props.items():
        if p in VAGUE_PARAMS:
            problems.append(f"param '{p}' is vague - say what it is, e.g. order_id")
        if "description" not in spec and "enum" not in spec:
            problems.append(f"param '{p}' has no description or enum")
    if tool.get("strict") and schema.get("additionalProperties") is not False:
        problems.append("strict tool: set additionalProperties to false")
    return problems


WEAK = {"name": "orders", "description": "Gets order data.",
        "input_schema": {"type": "object", "properties": {"id": {"type": "string"}},
                         "required": ["id", "email"]}}

if __name__ == "__main__":
    for tool in [WEAK, *TOOLS]:
        issues = lint_tool(tool)
        print(f"{tool['name']:<14}", "OK" if not issues else "")
        for msg in issues:
            print("   -", msg)
