"""Offline: run the defensive parser over the kinds of text models really return."""
from safe_json import extract_json

SAMPLES = {
    "clean": '{"total": 135582.0}',
    "code fence": '```json\n{"total": 135582.0}\n```',
    "prose around": 'Here is the data:\n{"total": 135582.0}\nLet me know!',
    "brace in string": '{"note": "use } with care", "total": 1}',
    "two objects": '{"total": 1} and also {"total": 2}',
    "truncated": '{"total": 135582.0, "line_items": [{"desc',
    "NaN": '{"total": NaN}',
    "no JSON": "I could not find a total on this invoice.",
}

for name, text in SAMPLES.items():
    try:
        print(f"{name:16} OK    {extract_json(text)}")
    except ValueError as e:
        print(f"{name:16} FAIL  {e}")
