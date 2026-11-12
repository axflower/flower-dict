"""Boundary tests for fixed-source static vocabulary synchronization."""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scripts import sync_rime_ice as sync
from scripts import build_vocabulary as vocab
from scripts import test_vocabulary as vocabulary_fixtures


class StaticSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('FLOWER_TEST_SCRATCH'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / sync.SOURCE).mkdir(parents=True)

    def source(self, name, text):
        path = self.root / sync.SOURCE / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode('utf-8'))

    def test_canonical_umlaut_keeps_v_and_rejects_non_pinyin(self):
        for raw in ['lüè', 'lǜe', 'lve']:
            self.assertEqual(sync.canonical_pinyin(raw), 'lve')
        self.assertEqual(sync.canonical_pinyin('nǐ hǎo'), "ni'hao")
        for raw in ['X光', '123', '', 'ni/hao']:
            self.assertIsNone(sync.canonical_pinyin(raw))

    def test_dictionary_body_excludes_headers_and_commented_words(self):
        rows = list(sync.dictionary_rows('name: test\n...\n# 错词\n你好\tni hao\t10\n'))
        self.assertEqual(rows, [(4, ['你好', 'ni hao', '10'])])
        with self.assertRaisesRegex(ValueError, 'delimiter'):
            list(sync.dictionary_rows('你好\tni hao\t10\n'))

    def test_symbols_preserve_entire_values_not_keys_or_yaml_scalars(self):
        values = list(sync.symbol_values('symbols:\n  vkey: ["⌝⌞⌟", on, 123, "a b"]\n'))
        self.assertEqual(values, ['⌝⌞⌟', 'on', '123', 'a b'])
        self.source('symbols_v.yaml', 'symbols:\n  vkey: ["⌝⌞⌟", on]\n')
        words, _, _ = sync.extract_inventory(self.root, {'files': {'symbols_v.yaml': {}}})
        self.assertEqual(words, {'⌝⌞⌟', 'on'})
        self.assertNotIn('vkey', words)

    def test_symbols_reject_unexpected_nested_shapes(self):
        with self.assertRaisesRegex(ValueError, 'shape'):
            list(sync.symbol_values('symbols:\n  key: {arbitrary: object}\n'))

    def test_opencc_control_separator_and_literal_tab_are_not_words(self):
        self.source('opencc/others.txt', '----------说明\t----------\ntab\ttab ⇥ \t\n一月\tJan. January\n')
        words, _, excluded = sync.extract_inventory(self.root, {'files': {'opencc/others.txt': {}}})
        self.assertEqual(words, {'tab', '⇥', '一月', 'Jan.', 'January'})
        self.assertEqual(excluded['empty_or_control_candidates'], 1)

    def test_control_characters_are_rejected_but_emoji_zwj_is_preserved(self):
        self.assertFalse(sync.valid_text('bad\u0085text'))
        self.assertFalse(sync.valid_text(''))
        self.assertTrue(sync.valid_text('👨\u200d💻'))

    def test_source_order_weights_and_single_reading_protection(self):
        tables = {'8105': '你\tni\t999999\n妳\tni\t500000\n',
                  'base': '你好\tni hao\t500000\n',
                  'ext': '你好\tni hao\t900000\n',
                  'tencent': '新词\t100\n', 'others': '谢谢\txie xie\n'}
        for name, body in tables.items():
            self.source(f'cn_dicts/{name}.dict.yaml', '...\n' + body)
        raw, stats = sync.source_lexicon(self.root, {('ni', '你')})
        self.assertEqual(raw.decode(), "ni\t妳\t1\nni'hao\t你好\t7812\nxie'xie\t谢谢\t1\n")
        self.assertEqual(stats['existing_single_pairs_not_reweighted'], 1)
        self.assertEqual(stats['duplicate_pairs_first_source_wins'], 1)
        self.assertNotIn('新词', raw.decode())

    def test_invalid_weight_fails_instead_of_widening_policy(self):
        for name in sync.DEFAULT_CHINESE:
            self.source(f'cn_dicts/{name}.dict.yaml', '...\n')
        self.source('cn_dicts/base.dict.yaml', '...\n坏词\thuai ci\t-1\n')
        with self.assertRaisesRegex(ValueError, 'weight'):
            sync.source_lexicon(self.root, set())

    def test_source_weights_are_monotonic_bounded_and_distinct_from_raw_frequency(self):
        raw = [1, 100, 1000, 500000, 1000000, 0xffffffff]
        weights = [sync.source_weight(value) for value in raw]
        self.assertEqual(weights, [1, 1, 15, 7812, 8192, 8192])
        self.assertEqual(weights, sorted(weights))
        for invalid in [0, -1, 0x100000000]:
            with self.assertRaisesRegex(ValueError, 'source weight'):
                sync.source_weight(invalid)

    def test_source_manifest_and_file_tampering_are_rejected(self):
        raw = b'original\n'
        path = self.root / sync.SOURCE / 'LICENSE'
        path.write_bytes(raw)
        info = {'bytes': len(raw), 'sha256': sync.digest(raw),
                'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}
        manifest = {'commit': sync.COMMIT, 'declared_license': 'GPL-3.0-only', 'files': {'LICENSE': info}}
        snapshot = sync.json_bytes(manifest)
        (path.parent / 'manifest.json').write_bytes(snapshot)
        with patch.object(sync, 'MANIFEST_SHA256', sync.digest(snapshot)):
            sync.checked_sources(self.root)
            path.write_bytes(b'changed\n')
            with self.assertRaisesRegex(ValueError, 'source bytes'):
                sync.checked_sources(self.root)
        with self.assertRaisesRegex(ValueError, 'manifest'):
            sync.checked_sources(self.root)

    def test_incremental_words_keep_old_readings_and_refresh_is_idempotent(self):
        fixture = vocabulary_fixtures.VocabularyCheckTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        root = fixture.root
        folder = root / vocab.DATA
        before_lines = set((folder / 'expanded.tsv').read_bytes().splitlines())
        before_catalog = dict(line.split('\t') for line in
                              (folder / 'catalog.tsv').read_text(encoding='utf-8').splitlines())
        self.assertEqual(sync.extend_vocabulary(root, {'国国', 'ABC'}), 2)
        vocab.check(root)
        self.assertTrue(before_lines <= set((folder / 'expanded.tsv').read_bytes().splitlines()))
        after_catalog = dict(line.split('\t') for line in
                             (folder / 'catalog.tsv').read_text(encoding='utf-8').splitlines())
        self.assertTrue(before_catalog.items() <= after_catalog.items())
        before = {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in folder.iterdir()}
        self.assertEqual(sync.extend_vocabulary(root, {'国国', 'ABC'}), 0)
        self.assertEqual(before, {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in folder.iterdir()})


if __name__ == '__main__':
    unittest.main()
