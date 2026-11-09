//! Complete word inventory, including entries outside the Pinyin TSV format.
use crate::ParseError;

/// How a word is represented by this dictionary.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ReadingKind {
    /// At least one reading is supported by an existing dictionary table.
    Existing,
    /// A reading was generated automatically; it has not been manually verified.
    Automatic,
    /// An English, mixed-script, symbol or emoji word, without a Pinyin promise.
    Literal,
    /// A Chinese word is retained but its reading could not be generated.
    Unresolved,
}

/// One distinct word. Readings are exposed by the Pinyin tables separately.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct VocabularyEntry<'a> {
    pub text: &'a str,
    pub reading_kind: ReadingKind,
}

/// Sorted, distinct words with their reading status.
pub const VOCABULARY_TSV: &str = include_str!("../data/pinyin/vocabulary/catalog.tsv");

/// Iterate the complete vocabulary without loading an index or touching disk.
///
/// Literal and unresolved words are retained here even when they cannot be
/// represented by [`crate::Entry`]. Automatic readings are not verified readings.
pub fn vocabulary() -> impl Iterator<Item = Result<VocabularyEntry<'static>, ParseError>> {
    VOCABULARY_TSV.lines().enumerate().map(|(number, line)| {
        let error = ParseError { line: number + 1 };
        let (text, kind) = line.split_once('\t').ok_or(error)?;
        if text.is_empty() || text.chars().any(char::is_control) {
            return Err(error);
        }
        let reading_kind = match kind {
            "E" => ReadingKind::Existing,
            "A" => ReadingKind::Automatic,
            "L" => ReadingKind::Literal,
            "U" => ReadingKind::Unresolved,
            _ => return Err(error),
        };
        Ok(VocabularyEntry { text, reading_kind })
    })
}
