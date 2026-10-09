import anthropic

client = anthropic.Anthropic()
BETA = ["compact-2026-09-04"]
MODEL = "claude-opus-5-5"

history = [
    {"role": "user", "content": "I'm building a recipe app. Name the main entities."},
    {"role": "assistant", "content": "Recipe, Ingredient, Step, RecipeIngredient."},
    {"role": "user", "content": "Good. Now suggest field names for Recipe."},
]

def compact_now(history):
    """Ask for a signed summary block, then use it IN PLACE of the history."""
    r = client.beta.messages.create(
        model=MODEL, max_tokens=4096, betas=BETA,
        messages=history,
        compaction={"type": "summarize"},          # no reply, just the summary
    )
    if r.stop_reason != "compaction":
        raise RuntimeError(f"no summary produced (stop_reason={r.stop_reason})")
    block = next(b for b in r.content if b.type == "compaction")
    print("summary:", block.content[:200])
    return [{"role": "assistant", "content": [block]}]   # one block, placed first

history = compact_now(history)
history.append({"role": "user", "content": "Now suggest field names for Step."})
r = client.beta.messages.create(model=MODEL, max_tokens=2048, betas=BETA,
                                messages=history)          # header still required
print("".join(b.text for b in r.content if b.type == "text"))
