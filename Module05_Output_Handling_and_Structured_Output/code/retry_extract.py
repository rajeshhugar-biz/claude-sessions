"""Ask for JSON, validate it with Pydantic + business rules, retry with feedback."""
from anthropic import transform_schema
from pydantic import ValidationError
from safe_json import extract_json


class ExtractionError(Exception):
    """No valid result: route this item to a human."""


def extract_with_retry(client, model_cls, content, *, rules=None, max_attempts=3,
                       model="claude-sonnet-5-5", max_tokens=2048):
    fmt = {"type": "json_schema", "schema": transform_schema(model_cls)}
    messages = [{"role": "user", "content": content}]
    for attempt in range(1, max_attempts + 1):
        r = client.messages.create(model=model, max_tokens=max_tokens,
                                   messages=messages, output_config={"format": fmt})
        if r.stop_reason == "refusal":
            raise ExtractionError("refused: change the request, don't retry it")
        if r.stop_reason == "max_tokens":
            max_tokens *= 2  # truncated JSON: retry with more room
            continue
        text = "".join(b.text for b in r.content if b.type == "text")
        try:
            obj = model_cls.model_validate(extract_json(text))
        except ValidationError as e:  # schema problems, one line per field
            problems = [f"{'.'.join(map(str, d['loc']))}: {d['msg']}"
                        for d in e.errors()]
        except ValueError as e:  # no parseable JSON at all
            problems = [str(e)]
        else:
            problems = rules(obj) if rules else []  # business rules
        if not problems:
            return obj, attempt
        messages += [{"role": "assistant", "content": text},
                     {"role": "user", "content": "Your JSON has problems:\n- "
                      + "\n- ".join(problems) + "\nReturn the corrected JSON."}]
    raise ExtractionError(f"no valid result after {max_attempts} attempts")
