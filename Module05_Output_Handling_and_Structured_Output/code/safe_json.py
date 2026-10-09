"""Defensive JSON extraction for model text that may not be clean JSON."""
import json
import re

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _reject(name):
    raise ValueError(f"{name} is not valid JSON")


_decoder = json.JSONDecoder(parse_constant=_reject)  # refuse NaN / Infinity


def extract_json(text, want=dict):
    """Return the first JSON object (or list) in text: fences and prose are OK.

    Fails loudly (ValueError) rather than guessing, e.g. on truncated output.
    """
    text = (text or "").lstrip("\ufeff").strip()  # BOM, whitespace
    if not text:
        raise ValueError("empty response")
    fenced = FENCE.search(text)
    if fenced:
        text = fenced.group(1)
    start = text.find("{" if want is dict else "[")
    if start == -1:
        raise ValueError(f"no JSON {want.__name__} in: {text[:60]!r}")
    try:
        value, _ = _decoder.raw_decode(text, start)  # ignores trailing prose
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid or truncated JSON: {e}") from e
    return value
