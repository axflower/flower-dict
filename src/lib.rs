//! Reusable, offline Pinyin dictionary data; no IME or platform policy.
//!
//! Tables retain their original positive integer weights and may overlap.
//! Consumers decide normalization, deduplication, ranking and input behavior.
//! Program code is MIT; see NOTICE.md for the separate data licenses.
#![forbid(unsafe_code)]
#![doc = include_str!("../README.md")]

mod generated;
pub use generated::{asset, COMMON_USAGE_PAIRS, DEFAULT_TSV, EVERYDAY_TSV, TABLES};

/// One original dictionary record, borrowing its source table.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Entry<'a> {
    pub pinyin: &'a str,
    pub text: &'a str,
    pub weight: u32,
}

/// A source table, not a pre-ranked candidate list.
#[derive(Clone, Copy, Debug)]
pub struct Table {
    pub id: &'static str,
    pub path: &'static str,
    pub tsv: &'static str,
    pub default_enabled: bool,
    /// Data license(s), independent of the MIT Rust API code.
    pub license: &'static str,
}

impl Table {
    pub fn entries(&self) -> Entries<'static> {
        entries(self.tsv)
    }
}

/// Malformed TSV. Line numbers are one-based within the original table.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct ParseError {
    pub line: usize,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "invalid dictionary record at line {}", self.line)
    }
}
impl std::error::Error for ParseError {}

/// Lazy zero-copy TSV parsing, skipping blank and comment lines.
pub struct Entries<'a> {
    lines: std::iter::Enumerate<std::str::Lines<'a>>,
}

pub fn entries(tsv: &str) -> Entries<'_> {
    Entries {
        lines: tsv.lines().enumerate(),
    }
}

impl<'a> Iterator for Entries<'a> {
    type Item = Result<Entry<'a>, ParseError>;

    fn next(&mut self) -> Option<Self::Item> {
        for (number, line) in self.lines.by_ref() {
            if line.trim().is_empty() || line.trim_start().starts_with('#') {
                continue;
            }
            let mut fields = line.split('\t');
            let parsed = (|| {
                let pinyin = fields.next()?;
                let text = fields.next()?;
                let weight = fields.next()?.parse::<u32>().ok()?;
                if fields.next().is_some()
                    || weight == 0
                    || text.is_empty()
                    || text.chars().any(char::is_control)
                    || pinyin.is_empty()
                    || pinyin.starts_with('\'')
                    || pinyin.ends_with('\'')
                    || pinyin.contains("''")
                    || !pinyin.bytes().all(|b| b.is_ascii_lowercase() || b == b'\'')
                {
                    return None;
                }
                Some(Entry {
                    pinyin,
                    text,
                    weight,
                })
            })();
            return Some(parsed.ok_or(ParseError { line: number + 1 }));
        }
        None
    }
}

/// All public tables, including optional proper names and the legacy fixture.
pub fn all_tables() -> impl Iterator<Item = &'static Table> {
    TABLES.iter()
}

/// The 16 tables used by the reference default snapshot; no optional names.
pub fn default_tables() -> impl Iterator<Item = &'static Table> {
    TABLES.iter().filter(|table| table.default_enabled)
}

pub fn table(id: &str) -> Option<&'static Table> {
    TABLES.iter().find(|table| table.id == id)
}
