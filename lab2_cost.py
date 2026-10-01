PRICES = {  # USD per 1M tokens (input, output), Sep 2026 list prices
    "Haiku 4.5":  (1, 5),
    "Sonnet 5.5": (2, 10),
    "Opus 5.5":   (4, 20),
    "Fable 5.1":  (10, 50),
}

def daily_cost(conversations, in_tok, out_tok, price):
    p_in, p_out = price
    inp = conversations * in_tok * p_in / 1_000_000
    out = conversations * out_tok * p_out / 1_000_000
    return inp, out

print(f"{'model':<12}{'input $':>9}{'output $':>10}{'day $':>9}{'month $':>10}{'out %':>7}")
for model, price in PRICES.items():
    inp, out = daily_cost(5_000, 1_500, 400, price)
    day = inp + out
    print(f"{model:<12}{inp:>9.2f}{out:>10.2f}{day:>9.2f}{day*30:>10.2f}{out/day:>7.0%}")