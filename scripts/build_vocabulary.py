"""Build the expanded word inventory; --check is offline and never writes.

Refreshing readings requires pypinyin==0.55.0. The Rust consumer and --check
only need the committed snapshots, not Python packages or network access.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = Path("data/pinyin/vocabulary")
ENGINE_VERSION = "0.55.0"
READING = re.compile(r"[a-z]+(?:'[a-z]+)*\Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def baseline_paths(root: Path):
    paths = [
        Path("data/pinyin/base_lexicon.tsv"),
        Path("data/pinyin/phrases/phrase_lexicon.tsv"),
        Path("data/pinyin/everyday_phrases.tsv"),
    ]
    paths += [
        p.relative_to(root)
        for p in sorted((root / "data/pinyin/categories").glob("*.tsv"))
        if p.name not in {"provenance.tsv", "rejected.tsv"}
    ]
    return paths


def load_baseline(root: Path):
    known = defaultdict(dict)
    default = set()
    paths = baseline_paths(root)
    proper = Path("data/pinyin/phrases/proper_lexicon.tsv")
    for path in paths + [proper]:
        for line in (root / path).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            key, word, raw_weight = line.split("\t")
            weight = int(raw_weight)
            if not READING.fullmatch(key) or weight <= 0:
                raise ValueError(f"invalid baseline entry: {path}")
            known[word][key] = max(known[word].get(key, 0), weight)
            if path != proper:
                default.add((key, word))
    hashes = {p.as_posix(): sha((root / p).read_bytes()) for p in paths + [proper]}
    return known, default, hashes


def han_word(word: str) -> bool:
    return bool(word) and all(
        c == "〇" or any(a <= ord(c) <= b for a, b in (
            (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
            (0x20000, 0x323AF),
        )) for c in word
    )


def word_snapshot(root: Path):
    raw = (root / DATA / "words.txt").read_bytes()
    words = raw.decode("utf-8").splitlines()
    if raw != "".join(w + "\n" for w in sorted(set(words))).encode("utf-8"):
        raise ValueError("word snapshot must be sorted, distinct UTF-8 with LF")
    if any(not w or any(unicodedata.category(c) == "Cc" for c in w) for w in words):
        raise ValueError("empty or control word")
    return raw, set(words)


def auto_reading(word, known, lazy_pinyin, style):
    tokens = lazy_pinyin(word, style=style, strict=False,
                         errors=lambda chars: list(chars))
    if len(tokens) != len(word):
        return None
    for i, token in enumerate(tokens):
        if not re.fullmatch("[a-z]+", token) and word[i] in known:
            tokens[i] = max(known[word[i]], key=known[word[i]].get)
    if not all(re.fullmatch("[a-z]+", t) for t in tokens):
        return None
    return "'".join(tokens)


def refresh(root: Path):
    import pypinyin
    if pypinyin.__version__ != ENGINE_VERSION:
        raise ValueError(f"refresh requires pypinyin=={ENGINE_VERSION}")
    known, default, baseline_hashes = load_baseline(root)
    word_raw, target = word_snapshot(root)
    words = sorted(target | set(known))
    extra, catalog, unresolved = set(), [], []
    counts = Counter()
    for index, word in enumerate(words):
        keys = list(known.get(word, ()))
        if keys:
            method = "E"
        elif han_word(word):
            key = auto_reading(word, known, pypinyin.lazy_pinyin, pypinyin.Style.NORMAL)
            if key:
                keys, method = [key], "A"
            else:
                method = "U"
                unresolved.append(word)
        else:
            method = "L"
        # Keep proper-only readings optional; only newly inferred readings
        # belong to the default expansion.
        if method == "A":
            extra.update((key, word) for key in keys if (key, word) not in default)
        catalog.append(f"{word}\t{method}\n")
        counts[method] += 1
        if index and index % 400_000 == 0:
            print(f"processed {index}/{len(words)} words", flush=True)
    outputs = {
        "expanded.tsv": "".join(f"{key}\t{word}\t1\n" for key, word in sorted(extra)).encode(),
        "catalog.tsv": "".join(catalog).encode(),
        "unresolved.txt": "".join(w + "\n" for w in unresolved).encode(),
    }
    coverage = {
        "schema_version": 1, "version": "0.2.0",
        "target_words": len(target), "target_sha256": sha(word_raw),
        "words": len(words), "reading_kind": dict(sorted(counts.items())),
        "expanded_pairs": len(extra), "default_pairs_before": len(default),
        "default_pairs_after": len(default) + len(extra),
        "missing_target_words": 0,
        "automatic_readings_manually_verified": False,
        "reading_engine": f"pypinyin {ENGINE_VERSION}; existing exact words first",
        "new_weights": "uniform project weight 1; not corpus frequency",
        "baseline_sha256": baseline_hashes,
        "outputs": {name: {"bytes": len(raw), "sha256": sha(raw)}
                    for name, raw in outputs.items()},
    }
    outputs["coverage.json"] = (json.dumps(coverage, ensure_ascii=False, indent=2) + "\n").encode()
    for name, raw in outputs.items():
        (root / DATA / name).write_bytes(raw)
    return coverage


def check(root: Path):
    folder = root / DATA
    report = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
    if report["schema_version"] != 1 or report["version"] != "0.2.0":
        raise ValueError("unsupported coverage version")
    known, default, hashes = load_baseline(root)
    word_raw, target = word_snapshot(root)
    if hashes != report["baseline_sha256"] or sha(word_raw) != report["target_sha256"]:
        raise ValueError("baseline or word snapshot changed")
    for name in ("expanded.tsv", "catalog.tsv", "unresolved.txt"):
        raw = (folder / name).read_bytes()
        if report["outputs"][name] != {"bytes": len(raw), "sha256": sha(raw)}:
            raise ValueError(f"snapshot mismatch: {name}")
    catalog, counts, previous = {}, Counter(), None
    for line in (folder / "catalog.tsv").read_text(encoding="utf-8").splitlines():
        word, kind = line.split("\t")
        if not word or kind not in {"E", "A", "L", "U"}:
            raise ValueError("invalid word catalog")
        if previous is not None and previous >= word:
            raise ValueError("catalog is not sorted and distinct")
        previous, catalog[word] = word, kind
        counts[kind] += 1
        if (kind == "E") != (word in known):
            raise ValueError("incorrect existing-reading status")
        if kind in {"A", "U"} and not han_word(word):
            raise ValueError("non-Chinese word assigned a generated reading")
        if kind == "L" and han_word(word):
            raise ValueError("Chinese word incorrectly marked literal")
    if set(catalog) != target | set(known):
        raise ValueError("word coverage mismatch")
    valid_syllables = {
        syllable for key in known.values() for reading in key
        for syllable in reading.split("'")
    }
    extras, extra_words, previous = set(), set(), None
    for line in (folder / "expanded.tsv").read_text(encoding="utf-8").splitlines():
        key, word, weight = line.split("\t")
        pair = key, word
        if (not READING.fullmatch(key) or weight != "1" or pair in default
                or (previous is not None and previous >= pair)):
            raise ValueError("invalid, duplicate or overlapping expanded pair")
        if catalog.get(word) in {"L", "U"}:
            raise ValueError("reading for a literal or unresolved word")
        if catalog.get(word) != "A":
            raise ValueError("non-automatic reading promoted into default expansion")
        if catalog[word] == "A" and len(key.split("'")) != len(word):
            raise ValueError("automatic syllable count mismatch")
        if any(s not in valid_syllables for s in key.split("'")):
            raise ValueError("unknown expanded syllable")
        previous = pair
        extras.add(pair)
        extra_words.add(word)
    if any(word not in extra_words for word, kind in catalog.items() if kind == "A"):
        raise ValueError("automatic word missing from Pinyin tables")
    unresolved = (folder / "unresolved.txt").read_text(encoding="utf-8").splitlines()
    if unresolved != [w for w, kind in catalog.items() if kind == "U"]:
        raise ValueError("unresolved inventory mismatch")
    actual = {
        "target_words": len(target), "words": len(catalog),
        "reading_kind": dict(sorted(counts.items())),
        "expanded_pairs": len(extras), "default_pairs_before": len(default),
        "default_pairs_after": len(default) + len(extras),
        "missing_target_words": len(target - catalog.keys()),
    }
    for key, value in actual.items():
        if report[key] != value:
            raise ValueError(f"coverage mismatch: {key}")
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    report = refresh(ROOT) if args.refresh else check(ROOT)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
