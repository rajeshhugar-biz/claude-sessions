import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-5-5", "claude-opus-5-5"]

TEXTS = {
    "english": "Our support team replies within one business day. "
               "Please include your order number so we can help you faster.",
    "hindi":   "हमारी सहायता टीम एक कार्यदिवस के भीतर जवाब देती है। "
               "कृपया अपना ऑर्डर नंबर शामिल करें ताकि हम आपकी जल्दी मदद कर सकें।",
    "python":  "def average(nums):\n"
               "    if not nums:\n"
               "        return 0.0\n"
               "    return sum(nums) / len(nums)\n",
    "json":    '{"order_id": "A-10293", "status": "shipped", '
               '"items": [{"sku": "TSH-01", "qty": 2}]}',
}

print(f"{'text':<10}" + "".join(f"{m.split('-')[1]:>10}" for m in MODELS))
for name, text in TEXTS.items():
    counts = [
        client.messages.count_tokens(
            model=m, messages=[{"role": "user", "content": text}]
        ).input_tokens
        for m in MODELS
    ]
    print(f"{name:<10}" + "".join(f"{c:>10}" for c in counts))