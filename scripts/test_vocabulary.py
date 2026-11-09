"""Failure boundaries for the offline word inventory validator."""
from pathlib import Path
import json
import os
import tempfile
import unittest

from scripts import build_vocabulary as vocab


class VocabularyCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            dir=os.environ.get("FLOWER_TEST_SCRATCH"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("data/pinyin/phrases", "data/pinyin/categories",
                       str(vocab.DATA)):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        fixtures = {
            "data/pinyin/base_lexicon.tsv":
                "guo\t国\t2\nhao\t好\t2\nni\t你\t2\nzhong\t中\t2\n",
            "data/pinyin/phrases/phrase_lexicon.tsv": "ni'hao\t你好\t3\n",
            "data/pinyin/everyday_phrases.tsv": "",
            "data/pinyin/phrases/proper_lexicon.tsv": "",
        }
        for path, text in fixtures.items():
            (self.root / path).write_bytes(text.encode())
        self.folder = self.root / vocab.DATA
        target = sorted(["X光", "中国", "你好", "𲎮"])
        (self.folder / "words.txt").write_bytes(
            "".join(w + "\n" for w in target).encode())
        known, default, hashes = vocab.load_baseline(self.root)
        kinds = {word: "E" for word in known}
        kinds.update({"X光": "L", "中国": "A", "𲎮": "U"})
        data = {
            "catalog.tsv": "".join(f"{w}\t{kinds[w]}\n" for w in sorted(kinds)),
            "expanded.tsv": "zhong'guo\t中国\t1\n",
            "unresolved.txt": "𲎮\n",
        }
        for path, text in data.items():
            (self.folder / path).write_bytes(text.encode())
        self.report = {
            "schema_version": 1, "version": "0.2.0",
            "baseline_sha256": hashes,
            "target_sha256": vocab.sha((self.folder / "words.txt").read_bytes()),
            "target_words": 4, "words": 8,
            "reading_kind": {"E": 5, "A": 1, "L": 1, "U": 1},
            "expanded_pairs": 1, "default_pairs_before": len(default),
            "default_pairs_after": len(default) + 1, "missing_target_words": 0,
        }
        self.rehash()

    def rehash(self):
        self.report["outputs"] = {
            name: {"bytes": len((raw := (self.folder / name).read_bytes())),
                   "sha256": vocab.sha(raw)}
            for name in ("catalog.tsv", "expanded.tsv", "unresolved.txt")
        }
        (self.folder / "coverage.json").write_text(
            json.dumps(self.report), encoding="utf-8")

    def test_check_is_read_only_and_needs_no_annotation_package(self):
        before = {p: (p.stat().st_mtime_ns, p.read_bytes())
                  for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(vocab.check(self.root)["missing_target_words"], 0)
        self.assertEqual(before, {p: (p.stat().st_mtime_ns, p.read_bytes())
                                  for p in before})

    def test_baseline_edit_is_rejected(self):
        path = self.root / "data/pinyin/base_lexicon.tsv"
        path.write_bytes(path.read_bytes().replace(b"\t2\n", b"\t3\n", 1))
        with self.assertRaisesRegex(ValueError, "baseline"):
            vocab.check(self.root)

    def test_truncated_snapshot_is_rejected(self):
        (self.folder / "expanded.tsv").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            vocab.check(self.root)

    def test_missing_word_is_rejected_even_with_updated_file_hash(self):
        path = self.folder / "catalog.tsv"
        path.write_bytes(path.read_bytes().replace("X光\tL\n".encode(), b""))
        self.rehash()
        with self.assertRaisesRegex(ValueError, "coverage"):
            vocab.check(self.root)

    def test_fake_pinyin_for_unresolved_text_is_rejected(self):
        path = self.folder / "expanded.tsv"
        path.write_bytes("ni\t𲎮\t1\nzhong'guo\t中国\t1\n".encode())
        self.rehash()
        with self.assertRaisesRegex(ValueError, "unresolved"):
            vocab.check(self.root)

    def test_unknown_syllable_is_rejected_even_with_updated_file_hash(self):
        (self.folder / "expanded.tsv").write_bytes("zhong'xyz\t中国\t1\n".encode())
        self.rehash()
        with self.assertRaisesRegex(ValueError, "syllable"):
            vocab.check(self.root)

    def test_automatic_status_cannot_masquerade_as_existing(self):
        path = self.folder / "catalog.tsv"
        path.write_bytes(path.read_bytes().replace("中国\tA".encode(), "中国\tE".encode()))
        self.rehash()
        with self.assertRaisesRegex(ValueError, "existing-reading"):
            vocab.check(self.root)

    def test_optional_proper_reading_is_not_promoted_into_default_expansion(self):
        proper = self.root / "data/pinyin/phrases/proper_lexicon.tsv"
        proper.write_bytes("ni\t倪\t1\n".encode())
        self.report["baseline_sha256"] = vocab.load_baseline(self.root)[2]
        path = self.folder / "catalog.tsv"
        lines = path.read_text(encoding="utf-8").splitlines() + ["倪\tE"]
        path.write_bytes("".join(line + "\n" for line in sorted(lines)).encode())
        self.report["words"] += 1
        self.report["reading_kind"]["E"] += 1
        self.rehash()
        vocab.check(self.root)
        (self.folder / "expanded.tsv").write_bytes("ni\t倪\t1\nzhong'guo\t中国\t1\n".encode())
        self.rehash()
        with self.assertRaisesRegex(ValueError, "non-automatic"):
            vocab.check(self.root)

    def test_c1_control_character_is_rejected_like_rust_parser(self):
        path = self.folder / "words.txt"
        words = path.read_text(encoding="utf-8").splitlines() + ["X\u0080"]
        path.write_bytes("".join(w + "\n" for w in sorted(words)).encode())
        with self.assertRaisesRegex(ValueError, "control"):
            vocab.check(self.root)


if __name__ == "__main__":
    unittest.main()
