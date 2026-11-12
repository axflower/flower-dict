"""Sync a fixed static word snapshot and independent source Pinyin weights offline.

Maintenance dependencies: PyYAML==6.0.3; refresh also needs pypinyin==0.55.0.
Never downloads or executes upstream code. --check never writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))
from scripts import build_vocabulary as vocab

SOURCE = Path('data/pinyin/sources/rime_ice')
OUTPUT = Path('data/pinyin/rime_ice')
COMMIT = '927e1cf1d3eeb9bf4be85e3f684dba4dd485b6f6'
MANIFEST_SHA256 = 'fb1e907de05498c3205803b91ba12264caf4ceb373889043f43e6b45c8d6f42a'
BASELINE_CATALOG_WORDS = 2168043
DEFAULT_CHINESE = ('8105', 'base', 'ext', 'tencent', 'others')
PINYIN = re.compile(r'[a-z]+(?:\x27[a-z]+)*\Z')
SOURCE_WEIGHT_DIVISOR = 64
SOURCE_WEIGHT_CAP = 8192


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def checked_sources(root):
    folder = root / SOURCE
    raw = (folder / 'manifest.json').read_bytes()
    if digest(raw) != MANIFEST_SHA256:
        raise ValueError('source manifest differs from fixed snapshot')
    manifest = json.loads(raw)
    if manifest['commit'] != COMMIT or manifest['declared_license'] != 'GPL-3.0-only':
        raise ValueError('source identity mismatch')
    for name, info in manifest['files'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('invalid source path')
        data = (folder / path).read_bytes()
        if len(data) != info['bytes'] or digest(data) != info['sha256']:
            raise ValueError(f'source bytes mismatch: {name}')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != info['git_blob']:
            raise ValueError(f'source Git blob mismatch: {name}')
    return manifest


def dictionary_rows(text):
    started = False
    for number, line in enumerate(text.splitlines(), 1):
        if not started:
            if line.strip() == '...':
                started = True
            continue
        if line.strip() and not line.lstrip().startswith('#'):
            yield number, line.split('\t')
    if not started:
        raise ValueError('missing dictionary body delimiter')


def canonical_pinyin(code):
    tokens = []
    for token in code.strip().split():
        token = unicodedata.normalize('NFD', token.lower()).replace('u\u0308', 'v')
        token = ''.join(c for c in token if unicodedata.category(c) != 'Mn')
        if not re.fullmatch('[a-z]+', token):
            return None
        tokens.append(token)
    key = "'".join(tokens)
    return key if PINYIN.fullmatch(key) else None


def valid_text(text):
    return bool(text) and not any(unicodedata.category(c) == 'Cc' for c in text)


def source_weight(raw_weight):
    """Project scale, not a claim that unrelated source frequencies are equal."""
    if not 1 <= raw_weight <= 0xffffffff:
        raise ValueError('out-of-range source weight')
    return max(1, min(SOURCE_WEIGHT_CAP, raw_weight // SOURCE_WEIGHT_DIVISOR))


def symbol_values(text):
    import yaml
    if yaml.__version__ != '6.0.3':
        raise ValueError('static YAML parsing requires PyYAML==6.0.3')
    # BaseLoader does not coerce bare on/off/numbers into non-string values.
    parsed = yaml.load(text, Loader=yaml.BaseLoader)
    if not isinstance(parsed, dict) or not isinstance(parsed.get('symbols'), dict):
        raise ValueError('invalid symbols mapping')
    for values in parsed['symbols'].values():
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ValueError('unexpected symbols candidate shape')
        yield from values


def extract_inventory(root, manifest):
    words, file_counts = set(), {}
    excluded = Counter()
    for name in manifest['files']:
        if name in ('LICENSE', 'README.md', 'rime_ice.schema.yaml', 'opencc/emoji.json'):
            continue
        text = (root / SOURCE / name).read_text(encoding='utf-8-sig')
        values = []
        if name.endswith('.dict.yaml'):
            values = (parts[0] for _, parts in dictionary_rows(text))
        elif name in ('symbols_v.yaml', 'symbols_caps_v.yaml'):
            values = symbol_values(text)
        elif name.startswith('opencc/'):
            values = []
            for line in text.splitlines():
                if not line or line.startswith('#') or line.startswith('----------'):
                    continue
                fields = line.split('\t', 1)
                if len(fields) != 2:
                    raise ValueError(f'invalid OpenCC record: {name}')
                values.append(fields[0])
                values.extend(fields[1].split(' '))
        elif name == 'custom_phrase.txt' or name.startswith('en_dicts/'):
            values = (line.split('\t')[0] for line in text.splitlines()
                      if line.strip() and not line.lstrip().startswith('#'))
        else:
            raise ValueError(f'unclassified source file: {name}')
        selected = set()
        for word in values:
            if not valid_text(word):
                excluded['empty_or_control_candidates'] += 1
                continue
            selected.add(word)
        words.update(selected)
        file_counts[name] = len(selected)
    return words, file_counts, dict(excluded)


def source_lexicon(root, existing_single_pairs):
    records = {}
    counts = Counter()
    for name in DEFAULT_CHINESE:
        path = root / SOURCE / f'cn_dicts/{name}.dict.yaml'
        for _, fields in dictionary_rows(path.read_text(encoding='utf-8-sig')):
            if name == 'tencent' or len(fields) < 2:
                counts['without_explicit_pinyin'] += 1
                continue
            word = fields[0]
            key = canonical_pinyin(fields[1])
            if not key or not valid_text(word):
                counts['unsupported_explicit_records'] += 1
                continue
            pair = (key, word)
            if pair in records:
                counts['duplicate_pairs_first_source_wins'] += 1
                continue
            if len(word) == 1:
                if pair in existing_single_pairs:
                    counts['existing_single_pairs_not_reweighted'] += 1
                    continue
                weight = 1
            elif len(fields) > 2 and fields[2].strip():
                raw = fields[2].strip()
                if not raw.isascii() or not raw.isdigit():
                    raise ValueError(f'invalid source weight: {name} {word}')
                weight = source_weight(int(raw))
            else:
                weight = 1  # Explicitly a project fallback, not measured frequency.
                counts['missing_weight_project_fallback_1'] += 1
            records[pair] = weight
    raw = ''.join(f'{key}\t{word}\t{weight}\n'
                  for (key, word), weight in sorted(records.items())).encode('utf-8')
    return raw, dict(counts)


def existing_single_pairs(root):
    result = set()
    for relative in vocab.baseline_paths(root):
        for line in (root / relative).read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            if len(fields) == 3 and len(fields[1]) == 1:
                result.add((fields[0], fields[1]))
    return result


def extend_vocabulary(root, imported):
    """Only annotate new words; previously validated readings/weights are retained."""
    import pypinyin
    if pypinyin.__version__ != vocab.ENGINE_VERSION:
        raise ValueError('refresh requires pypinyin==0.55.0')
    vocab.check(root)
    known, default, hashes = vocab.load_baseline(root)
    _, target = vocab.word_snapshot(root)
    folder = root / vocab.DATA
    report = json.loads((folder / 'coverage.json').read_text(encoding='utf-8'))
    catalog = dict(line.split('\t') for line in
                   (folder / 'catalog.tsv').read_text(encoding='utf-8').splitlines())
    added = sorted(imported - catalog.keys())
    extra_lines = []
    for word in added:
        if word in known:
            kind = 'E'
        elif vocab.han_word(word):
            key = vocab.auto_reading(word, known, pypinyin.lazy_pinyin, pypinyin.Style.NORMAL)
            if key:
                kind = 'A'
                extra_lines.append(f'{key}\t{word}\t1\n')
            else:
                kind = 'U'
        else:
            kind = 'L'
        catalog[word] = kind
    target.update(imported)
    # Existing lines retain their exact contents; a deterministic sort adds new lines.
    expanded = (folder / 'expanded.tsv').read_text(encoding='utf-8').splitlines(keepends=True)
    expanded.extend(extra_lines)
    counts = Counter(catalog.values())
    outputs = {
        'words.txt': ''.join(w + '\n' for w in sorted(target)).encode('utf-8'),
        'catalog.tsv': ''.join(f'{w}\t{catalog[w]}\n' for w in sorted(catalog)).encode('utf-8'),
        'expanded.tsv': ''.join(sorted(expanded)).encode('utf-8'),
        'unresolved.txt': ''.join(w + '\n' for w in sorted(catalog)
                                  if catalog[w] == 'U').encode('utf-8'),
    }
    report.update(target_words=len(target), target_sha256=digest(outputs['words.txt']),
                  words=len(catalog), reading_kind=dict(sorted(counts.items())),
                  expanded_pairs=len(expanded), default_pairs_before=len(default),
                  default_pairs_after=len(default) + len(expanded), missing_target_words=0,
                  baseline_sha256=hashes)
    report['outputs'] = {name: {'bytes': len(raw), 'sha256': digest(raw)}
                         for name, raw in outputs.items() if name != 'words.txt'}
    outputs['coverage.json'] = json_bytes(report)
    for name, raw in outputs.items():
        path = folder / name
        if path.read_bytes() != raw:
            path.write_bytes(raw)
    return len(added)


def combined_statistics(root, lexicon):
    pairs, upgraded = {}, 0
    for relative in vocab.baseline_paths(root) + [vocab.DATA / 'expanded.tsv']:
        for line in (root / relative).read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'):
                continue
            key, word, weight = line.split('\t')
            pair = (key, word)
            pairs[pair] = max(pairs.get(pair, 0), int(weight))
    before = len(pairs)
    for line in lexicon.decode('utf-8').splitlines():
        key, word, weight = line.split('\t')
        pair, weight = (key, word), int(weight)
        if pair in pairs and weight > pairs[pair]:
            upgraded += 1
        pairs[pair] = max(pairs.get(pair, 0), weight)
    return {'default_pairs_without_source_table': before,
            'default_pairs_with_source_table': len(pairs),
            'additional_pinyin_pairs': len(pairs) - before,
            'existing_pairs_with_higher_source_weight': upgraded}


def run(root, refresh=False):
    manifest = checked_sources(root)
    imported, file_counts, excluded = extract_inventory(root, manifest)
    singles = existing_single_pairs(root)
    lexicon, lexicon_counts = source_lexicon(root, singles)
    # Source-only new single pairs become existing after first generation: ignore our
    # own table when deriving exclusions so repeated refresh remains byte-identical.
    if refresh:
        extend_vocabulary(root, imported)
    vocab.check(root)
    catalog = {line.split('\t')[0] for line in
               (root / vocab.DATA / 'catalog.tsv').read_text(encoding='utf-8').splitlines()}
    missing = imported - catalog
    if missing:
        raise ValueError(f'{len(missing)} source words missing from catalog')
    report = {'schema_version': 1, 'source_commit': COMMIT,
              'source_manifest_sha256': MANIFEST_SHA256,
              'license': 'GPL-3.0-only', 'source_unique_words': len(imported),
              'source_file_word_counts': file_counts,
              'excluded': excluded, 'missing_source_words': 0,
              'baseline_catalog_words': BASELINE_CATALOG_WORDS,
              'added_catalog_words': len(catalog) - BASELINE_CATALOG_WORDS,
              'catalog_words': len(catalog),
              'lexicon_pairs': lexicon.count(b'\n'), 'lexicon_policy_counts': lexicon_counts,
              'lexicon_sha256': digest(lexicon), 'lexicon_bytes': len(lexicon),
              'phrase_weight_policy': {'kind': 'project-scaled source weight',
                                       'divisor': SOURCE_WEIGHT_DIVISOR,
                                       'cap': SOURCE_WEIGHT_CAP, 'minimum': 1},
              'vocabulary_scope': 'baseline/automatic reading statuses are retained; source table adds independent explicit readings',
              **combined_statistics(root, lexicon)}
    outputs = {'lexicon.tsv': lexicon, 'coverage.json': json_bytes(report)}
    if refresh:
        (root / OUTPUT).mkdir(exist_ok=True)
        for name, data in outputs.items():
            path = root / OUTPUT / name
            if not path.exists() or path.read_bytes() != data:
                path.write_bytes(data)
    else:
        for name, data in outputs.items():
            if (root / OUTPUT / name).read_bytes() != data:
                raise ValueError(f'generated output mismatch: {name}')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(ROOT, refresh=args.refresh), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
