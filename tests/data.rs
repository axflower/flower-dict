use flower_dictionary::{all_tables, default_tables, entries, table, DEFAULT_TSV};
use std::collections::HashSet;

#[test]
fn all_tables_parse_and_default_snapshot_preserves_pairs() {
    assert_eq!(all_tables().count(), 18);
    assert_eq!(default_tables().count(), 16);
    assert!(!table("proper").unwrap().default_enabled);
    assert!(!table("legacy-mvp").unwrap().default_enabled);
    let mut all_ids = HashSet::new();
    let mut default_pairs = HashSet::new();
    for source in all_tables() {
        assert!(all_ids.insert(source.id));
        assert!(!source.license.is_empty());
        assert_eq!(
            flower_dictionary::asset(source.path).unwrap(),
            source.tsv.as_bytes()
        );
        let mut count = 0;
        for entry in source.entries() {
            let entry = entry.unwrap();
            assert!(entry.weight > 0);
            count += 1;
            if source.default_enabled {
                default_pairs.insert((entry.pinyin, entry.text));
            }
        }
        assert!(count > 0);
        if source.id == "everyday" {
            assert_eq!(count, 803);
        }
    }
    assert_eq!(default_pairs.len(), 201109);
    let combined: HashSet<_> = entries(DEFAULT_TSV)
        .map(|r| {
            let e = r.unwrap();
            (e.pinyin, e.text)
        })
        .collect();
    assert_eq!(default_pairs, combined);
    assert!(combined.contains(&("qing'xu'jia'zhi", "情绪价值")));
    assert!(combined.contains(&("beng'bu'zhu'le", "蚌埠住了")));
}

#[test]
fn parser_reports_one_based_lines_and_continues() {
    let mut iter = entries("# comment\n\nni\t你\t1\nnope\nhao\t好\t2\n");
    assert_eq!(iter.next().unwrap().unwrap().text, "你");
    assert_eq!(iter.next().unwrap().unwrap_err().line, 4);
    assert_eq!(iter.next().unwrap().unwrap().weight, 2);
    assert!(iter.next().is_none());
    for invalid in [
        "ni\t你\t0",
        "ni\t你\t4294967296",
        "ni\t你\t1\textra",
        "Ni\t你\t1",
        "ni''hao\t你好\t1",
        "ni\t\t1",
    ] {
        assert!(entries(invalid).next().unwrap().is_err(), "{invalid}");
    }
    assert!(table("unknown").is_none());
    assert!(flower_dictionary::asset("../Cargo.toml").is_none());
    assert!(flower_dictionary::asset("E:/private").is_none());
}

#[test]
fn baseline_and_licenses_are_packaged_assets() {
    let baseline = std::str::from_utf8(
        flower_dictionary::asset("data/pinyin/sources/kMandarin_8105.txt").unwrap(),
    )
    .unwrap();
    assert_eq!(
        baseline
            .lines()
            .filter(|l| !l.is_empty() && !l.starts_with('#'))
            .count(),
        8105
    );
    assert_eq!(
        flower_dictionary::COMMON_USAGE_PAIRS
            .split_whitespace()
            .count(),
        135
    );
    for name in [
        "data/pinyin/sources/UNICODE-LICENSE.txt",
        "data/pinyin/phrases/sources/CC-BY-SA-4.0.txt",
        "data/pinyin/sources/thuocl/LICENSE",
    ] {
        assert!(flower_dictionary::asset(name).unwrap().len() > 1000);
    }
}
