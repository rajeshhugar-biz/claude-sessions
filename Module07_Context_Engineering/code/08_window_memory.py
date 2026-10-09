"""Short-term memory: a running summary plus the last N messages. No API key."""
import re

def plain_user(m):
    """A real user turn, not a tool_result carrier (never split a tool pair)."""
    return m["role"] == "user" and (isinstance(m["content"], str) or not any(
        b.get("type") == "tool_result" for b in m["content"]))

class WindowMemory:
    def __init__(self, summarise, window=8):
        self.summarise = summarise      # (old_summary, folded_messages) -> new summary
        self.window = window
        self.summary = ""
        self.recent = []

    def add(self, role, content):
        self.recent.append({"role": role, "content": content})
        if len(self.recent) > self.window:
            self._fold()

    def _fold(self):
        """Fold the older half into the summary in one go (fewer cache misses)."""
        target = len(self.recent) - self.window // 2
        starts = [i for i, m in enumerate(self.recent) if i > 0 and plain_user(m)]
        if not starts:
            return                      # no safe place to cut yet
        # kept part must start with a real user turn: first one at/after target
        cut = next((i for i in starts if i >= target), starts[-1])
        folded, self.recent = self.recent[:cut], self.recent[cut:]
        self.summary = self.summarise(self.summary, folded)

    def system(self, base):
        """The summary rides in the system prompt; recent turns stay verbatim."""
        if not self.summary:
            return base
        return (f"{base}\n\n<conversation_summary>\n{self.summary}\n"
                "</conversation_summary>")

    def messages(self):
        return list(self.recent)

FACT = re.compile(r"\b(ORD-\d+|my name is \w+|I live in \w+|deadline is [\w ]+)",
                  re.I)

def fact_keeper(old_summary, folded):
    """Offline stand-in for an LLM summariser: keeps lines that look like facts."""
    facts = [ln for ln in old_summary.splitlines() if ln]
    for m in folded:
        if isinstance(m["content"], str):
            facts += [f"- {f}" for f in FACT.findall(m["content"])]
    return "\n".join(dict.fromkeys(facts))          # de-duplicate, keep order

if __name__ == "__main__":
    mem = WindowMemory(fact_keeper, window=6)
    mem.add("user", "Hi, my name is Ravi and my order is ORD-48213.")
    mem.add("assistant", "Thanks Ravi, I can see ORD-48213.")
    for t in range(2, 12):
        mem.add("user", f"Question {t} about delivery options.")
        mem.add("assistant", f"Answer {t}.")
    print(mem.system("You are Acme's support agent."))
    print(len(mem.messages()), "recent messages kept verbatim")
