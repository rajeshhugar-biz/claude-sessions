"""Context isolation: each subagent reads raw material in its OWN context and
returns a short report. The lead agent only ever sees the reports."""
from concurrent.futures import ThreadPoolExecutor
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

def text(r):
    return "".join(b.text for b in r.content if b.type == "text")

def run_subagent(task, material):
    """Fresh message list: no parent history, only what this task needs."""
    r = client.messages.create(
        model=MODEL, max_tokens=1500,
        system="You are a research subagent. Return only findings relevant to "
               "the task, max 250 words, with source names. No raw excerpts.",
        messages=[{"role": "user", "content":
                   f"<task>{task}</task>\n<material>\n{material}\n</material>"}])
    return text(r)

def lead_agent(question, sources):
    with ThreadPoolExecutor(max_workers=4) as pool:        # subagents in parallel
        reports = list(pool.map(
            lambda kv: run_subagent(f"{question} Focus on: {kv[0]}", kv[1]),
            sources.items()))
    joined = "\n\n".join(f'<report from="{n}">\n{r}\n</report>'
                         for n, r in zip(sources, reports))
    r = client.messages.create(                            # small, clean context
        model=MODEL, max_tokens=2048,
        messages=[{"role": "user", "content":
                   f"{joined}\n\nUsing these reports, answer: {question}"}])
    return text(r)

def lead_context_tokens(sources, report_tokens=400):
    """Estimate the lead agent's input with and without isolation."""
    raw = sum(len(m) // 4 for m in sources.values())
    return {"no_isolation": raw, "with_subagents": report_tokens * len(sources)}

if __name__ == "__main__":
    sources = {"tickets": "ticket text " * 20_000, "reviews": "review " * 30_000,
               "returns_log": "return row " * 15_000}
    print(lead_context_tokens(sources))
    print(lead_agent("Why are washing machine returns rising?", sources))
