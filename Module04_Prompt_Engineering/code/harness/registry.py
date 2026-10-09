"""Load versioned prompt files and build Messages API requests from them."""
import hashlib
import re
from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
MODEL = "claude-sonnet-5-5"          # pin the model together with the prompt


def load_prompt(version: str) -> dict:
    raw = (PROMPTS / f"classifier_{version}.txt").read_text(encoding="utf-8")
    parts = re.split(r"^=== (system|user) ===$", raw, flags=re.M)
    sections = dict(zip(parts[1::2], (p.strip() for p in parts[2::2])))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
    return {"version": version, "id": f"classifier@{version}+{digest}",
            "system": sections.get("system", ""), "user": sections["user"]}


def clean_ticket(ticket: str) -> str:
    ticket = "".join(ch for ch in ticket if ch in "\n\t" or ch.isprintable())
    return re.sub(r"</?\s*ticket\s*>", "", ticket, flags=re.I)[:4000]


def build_request(prompt: dict, ticket: str) -> dict:
    user = prompt["user"].replace("{{TICKET}}", clean_ticket(ticket))
    request = {"model": MODEL, "max_tokens": 1024, "output_config": {"effort": "low"},
               "messages": [{"role": "user", "content": user}]}
    if prompt["system"]:
        request["system"] = prompt["system"]
    return request
