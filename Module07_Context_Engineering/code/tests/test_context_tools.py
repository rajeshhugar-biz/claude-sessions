"""Unit tests for the local (no-API) pieces. Run from the code/ folder:
    python -m unittest discover -s tests -v
"""
import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE))
os.chdir(CODE)                                   # demos read data/ relative paths

sim = importlib.import_module("01_long_chat_simulator")
pruner = importlib.import_module("02_tool_output_pruner")
clearer = importlib.import_module("03_clear_old_results")
summ = importlib.import_module("04_summarise_helpers")
memory = importlib.import_module("08_window_memory")
rag = importlib.import_module("10_local_rag")
lab1 = importlib.import_module("lab1_degrading_chat")
try:
    memtool = importlib.import_module("09_memory_tool")
except ImportError:                              # anthropic not installed
    memtool = None


class TestSimulator(unittest.TestCase):
    def test_context_grows_every_turn(self):
        chat = sim.build_chat(turns=10)
        sizes = [sim.context_tokens(chat[:i]) for i in range(1, len(chat) + 1)]
        self.assertEqual(sizes, sorted(sizes))

    def test_tool_pairs_are_well_formed(self):
        chat = sim.build_chat(turns=6, tool_every=3)
        uses = [b["id"] for m in chat if isinstance(m["content"], list)
                for b in m["content"] if b["type"] == "tool_use"]
        results = [b["tool_use_id"] for m in chat if isinstance(m["content"], list)
                   for b in m["content"] if b["type"] == "tool_result"]
        self.assertEqual(uses, ["toolu_3", "toolu_6"])
        self.assertEqual(uses, results)


class TestPruner(unittest.TestCase):
    def test_whitelist_and_list_cap(self):
        rows = [{"id": i, "junk": i} for i in range(8)]
        data = {"id": 1, "secret": "x", "rows": rows}
        out = pruner.prune(data, fields={"id", "rows"}, max_items=2)
        self.assertNotIn("secret", out)
        self.assertEqual(out["rows"][:2], [{"id": 0}, {"id": 1}])
        self.assertEqual(out["rows"][-1], {"_omitted": 6})

    def test_long_strings_are_truncated(self):
        out = pruner.prune("a" * 500, max_chars=100)
        self.assertTrue(out.startswith("a" * 100))
        self.assertIn("[+400 chars]", out)

    def test_real_payload_shrinks_a_lot(self):
        raw = json.loads(Path("data/order_api_response.json").read_text())
        block = pruner.to_tool_result("t1", raw, fields={"order", "id", "status"})
        self.assertLess(len(block["content"]) * 10, len(json.dumps(raw)))
        self.assertEqual(json.loads(block["content"])["order"]["status"], "shipped")


class TestClearing(unittest.TestCase):
    def test_keeps_newest_results_and_does_not_mutate(self):
        chat = sim.build_chat(turns=12, tool_every=3)      # 4 tool results
        original = json.dumps(chat)
        out, cleared = clearer.clear_old_tool_results(chat, keep=1)
        self.assertEqual(cleared, 3)
        self.assertEqual(json.dumps(chat), original)
        results = [b for m in out if isinstance(m["content"], list)
                   for b in m["content"] if b["type"] == "tool_result"]
        self.assertEqual([r["content"] == clearer.PLACEHOLDER for r in results],
                         [True, True, True, False])

    def test_exclude_tools(self):
        chat = sim.build_chat(turns=9, tool_every=3)
        _, cleared = clearer.clear_old_tool_results(
            chat, keep=0, exclude_tools=("search_inventory",))
        self.assertEqual(cleared, 0)


class TestSummariseHelpers(unittest.TestCase):
    def test_split_never_starts_on_tool_result(self):
        chat = sim.build_chat(turns=9, tool_every=3)
        for keep in range(1, 10):
            i = summ.split_point(chat, keep_last=keep)
            if i:
                self.assertTrue(summ.is_plain_user(chat[i]))

    def test_compact_puts_summary_first_and_keeps_tail(self):
        chat = sim.build_chat(turns=9, tool_every=3)
        seen = []
        out = summ.compact(chat, lambda t: seen.append(t) or "<summary>S</summary>",
                           keep_last=4)
        self.assertEqual(out[0]["role"], "user")
        self.assertIn("<earlier_conversation_summary>\nS\n",
                      out[0]["content"][0]["text"])
        self.assertEqual(out[-1], chat[-1])
        self.assertTrue(seen and "USER:" in seen[0])

    def test_extract_summary(self):
        self.assertEqual(summ.extract_summary("x <summary> hi </summary> y"), "hi")
        self.assertEqual(summ.extract_summary("no tags"), "no tags")


class TestWindowMemory(unittest.TestCase):
    def test_window_bound_and_facts_survive(self):
        mem = memory.WindowMemory(memory.fact_keeper, window=6)
        mem.add("user", "my name is Asha, order ORD-1001")
        mem.add("assistant", "ok")
        for t in range(20):
            mem.add("user", f"q{t}")
            mem.add("assistant", f"a{t}")
            self.assertLessEqual(len(mem.messages()), 6)
        self.assertIn("ORD-1001", mem.system("base"))
        self.assertIn("my name is Asha", mem.system("base"))
        self.assertTrue(memory.plain_user(mem.messages()[0]))

    def test_no_summary_means_base_system(self):
        mem = memory.WindowMemory(memory.fact_keeper)
        self.assertEqual(mem.system("base"), "base")


class TestRag(unittest.TestCase):
    def setUp(self):
        text = Path("data/acme_handbook.md").read_text()
        self.chunks = rag.chunk_markdown(text, "acme_handbook.md", 60, 15)

    def test_chunks_have_metadata_and_overlap(self):
        self.assertTrue(all(c["source"] and c["heading"] for c in self.chunks))
        refunds = [c for c in self.chunks if c["heading"] == "Returns and refunds"]
        tail = refunds[0]["text"].split()[-15:]
        self.assertEqual(refunds[1]["text"].split()[:15], tail)

    def test_top_k_finds_the_right_section(self):
        r = rag.Retriever(self.chunks, use_sklearn=False)
        _, best = r.top_k("compressor warranty", k=1)[0]
        self.assertEqual(best["heading"], "Warranty")

    def test_numpy_and_sklearn_agree(self):
        if rag.TfidfVectorizer is None:
            self.skipTest("scikit-learn not installed")
        a = rag.Retriever(self.chunks, use_sklearn=False)
        b = rag.Retriever(self.chunks, use_sklearn=True)
        q = "express delivery cost"
        self.assertEqual([c["id"] for _, c in a.top_k(q)],
                         [c["id"] for _, c in b.top_k(q)])


@unittest.skipIf(memtool is None, "anthropic SDK not installed")
class TestMemoryToolHandler(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        memtool.ROOT = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_rejects_traversal(self):
        for bad in ["/memories/../../etc/passwd", "/etc/passwd", "/memoriesX/a",
                    "/memories/%2e%2e/secret", "/memories/..\\x"]:
            with self.assertRaises(ValueError):
                memtool.safe_path(bad)

    def test_create_view_replace_rename_delete(self):
        run = memtool.run_memory
        run({"command": "create", "path": "/memories/notes.md",
             "file_text": "pref: email\n"})
        self.assertIn("pref: email", run({"command": "view",
                                          "path": "/memories/notes.md"}))
        run({"command": "str_replace", "path": "/memories/notes.md",
             "old_str": "email", "new_str": "phone"})
        run({"command": "insert", "path": "/memories/notes.md", "insert_line": 0,
             "insert_text": "# Customer CUS-7781"})
        text = run({"command": "view", "path": "/memories/notes.md"})
        self.assertIn("1\t# Customer CUS-7781", text)
        self.assertIn("pref: phone", text)
        run({"command": "rename", "old_path": "/memories/notes.md",
             "new_path": "/memories/cus-7781.md"})
        self.assertIn("cus-7781.md", run({"command": "view", "path": "/memories"}))
        run({"command": "delete", "path": "/memories/cus-7781.md"})
        with self.assertRaises(ValueError):
            run({"command": "delete", "path": "/memories"})


class TestLab1(unittest.TestCase):
    def test_managed_beats_truncation(self):
        trunc, managed = lab1.run("truncate"), lab1.run("managed")
        self.assertEqual(managed["over_budget_turns"], 0)
        self.assertEqual(len(managed["recalled"]), 4)
        self.assertLess(len(trunc["recalled"]), 4)
        self.assertLess(managed["sent"], trunc["sent"])

    def test_keep_all_breaks_the_budget(self):
        self.assertGreater(lab1.run("keep_all")["over_budget_turns"], 0)


if __name__ == "__main__":
    unittest.main()
