// Fixed source asset mapping. Do not change default order without a snapshot revision.
use crate::Table;
pub const EVERYDAY_TSV: &str = include_str!("../data/pinyin/everyday_phrases.tsv");
/// Optional project-authored usage classification; not corpus frequency or required ranking.
pub const COMMON_USAGE_PAIRS: &str = include_str!("../data/pinyin/common_usage_pairs.txt");
pub const DEFAULT_TSV: &str = concat!(
    include_str!("../data/pinyin/base_lexicon.tsv"),
    "\n",
    include_str!("../data/pinyin/phrases/phrase_lexicon.tsv"),
    "\n",
    include_str!("../data/pinyin/everyday_phrases.tsv"),
    "\n",
    include_str!("../data/pinyin/categories/IT.tsv"),
    include_str!("../data/pinyin/categories/animal.tsv"),
    include_str!("../data/pinyin/categories/caijing.tsv"),
    include_str!("../data/pinyin/categories/car.tsv"),
    include_str!("../data/pinyin/categories/chengyu.tsv"),
    include_str!("../data/pinyin/categories/diming.tsv"),
    include_str!("../data/pinyin/categories/food.tsv"),
    include_str!("../data/pinyin/categories/law.tsv"),
    include_str!("../data/pinyin/categories/lishimingren.tsv"),
    include_str!("../data/pinyin/categories/medical.tsv"),
    include_str!("../data/pinyin/categories/poem.tsv"),
    include_str!("../data/pinyin/categories/cedict_supplement.tsv"),
    include_str!("../data/pinyin/categories/erhua.tsv"),
);
pub static TABLES: &[Table] = &[
    Table {
        id: "characters",
        path: "data/pinyin/base_lexicon.tsv",
        tsv: include_str!("../data/pinyin/base_lexicon.tsv"),
        default_enabled: true,
        license: "Unicode-3.0 AND MIT",
    },
    Table {
        id: "core",
        path: "data/pinyin/phrases/phrase_lexicon.tsv",
        tsv: include_str!("../data/pinyin/phrases/phrase_lexicon.tsv"),
        default_enabled: true,
        license: "CC-BY-SA-4.0 AND MIT",
    },
    Table {
        id: "everyday",
        path: "data/pinyin/everyday_phrases.tsv",
        tsv: include_str!("../data/pinyin/everyday_phrases.tsv"),
        default_enabled: true,
        license: "MIT",
    },
    Table {
        id: "IT",
        path: "data/pinyin/categories/IT.tsv",
        tsv: include_str!("../data/pinyin/categories/IT.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "animal",
        path: "data/pinyin/categories/animal.tsv",
        tsv: include_str!("../data/pinyin/categories/animal.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "caijing",
        path: "data/pinyin/categories/caijing.tsv",
        tsv: include_str!("../data/pinyin/categories/caijing.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "car",
        path: "data/pinyin/categories/car.tsv",
        tsv: include_str!("../data/pinyin/categories/car.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "chengyu",
        path: "data/pinyin/categories/chengyu.tsv",
        tsv: include_str!("../data/pinyin/categories/chengyu.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "diming",
        path: "data/pinyin/categories/diming.tsv",
        tsv: include_str!("../data/pinyin/categories/diming.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "food",
        path: "data/pinyin/categories/food.tsv",
        tsv: include_str!("../data/pinyin/categories/food.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "law",
        path: "data/pinyin/categories/law.tsv",
        tsv: include_str!("../data/pinyin/categories/law.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "lishimingren",
        path: "data/pinyin/categories/lishimingren.tsv",
        tsv: include_str!("../data/pinyin/categories/lishimingren.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "medical",
        path: "data/pinyin/categories/medical.tsv",
        tsv: include_str!("../data/pinyin/categories/medical.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "poem",
        path: "data/pinyin/categories/poem.tsv",
        tsv: include_str!("../data/pinyin/categories/poem.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "cedict_supplement",
        path: "data/pinyin/categories/cedict_supplement.tsv",
        tsv: include_str!("../data/pinyin/categories/cedict_supplement.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "erhua",
        path: "data/pinyin/categories/erhua.tsv",
        tsv: include_str!("../data/pinyin/categories/erhua.tsv"),
        default_enabled: true,
        license: "MIT AND CC-BY-SA-4.0 AND Unicode-3.0",
    },
    Table {
        id: "proper",
        path: "data/pinyin/phrases/proper_lexicon.tsv",
        tsv: include_str!("../data/pinyin/phrases/proper_lexicon.tsv"),
        default_enabled: false,
        license: "CC-BY-SA-4.0 AND MIT",
    },
    Table {
        id: "legacy-mvp",
        path: "data/pinyin/mvp_lexicon.tsv",
        tsv: include_str!("../data/pinyin/mvp_lexicon.tsv"),
        default_enabled: false,
        license: "MIT",
    },
];
/// Packaged public asset bytes by exact repository-relative path; unknown paths return None.
pub fn asset(path: &str) -> Option<&'static [u8]> {
    match path {
        "data/pinyin/base_lexicon.tsv" => Some(include_bytes!("../data/pinyin/base_lexicon.tsv")),
        "data/pinyin/categories/animal.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/animal.tsv"))
        }
        "data/pinyin/categories/caijing.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/caijing.tsv"))
        }
        "data/pinyin/categories/car.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/car.tsv"))
        }
        "data/pinyin/categories/cedict_supplement.tsv" => Some(include_bytes!(
            "../data/pinyin/categories/cedict_supplement.tsv"
        )),
        "data/pinyin/categories/chengyu.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/chengyu.tsv"))
        }
        "data/pinyin/categories/coverage.json" => {
            Some(include_bytes!("../data/pinyin/categories/coverage.json"))
        }
        "data/pinyin/categories/diming.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/diming.tsv"))
        }
        "data/pinyin/categories/erhua.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/erhua.tsv"))
        }
        "data/pinyin/categories/food.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/food.tsv"))
        }
        "data/pinyin/categories/IT.tsv" => Some(include_bytes!("../data/pinyin/categories/IT.tsv")),
        "data/pinyin/categories/law.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/law.tsv"))
        }
        "data/pinyin/categories/lishimingren.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/lishimingren.tsv"))
        }
        "data/pinyin/categories/manifest.json" => {
            Some(include_bytes!("../data/pinyin/categories/manifest.json"))
        }
        "data/pinyin/categories/medical.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/medical.tsv"))
        }
        "data/pinyin/categories/NOTICE.md" => {
            Some(include_bytes!("../data/pinyin/categories/NOTICE.md"))
        }
        "data/pinyin/categories/poem.tsv" => {
            Some(include_bytes!("../data/pinyin/categories/poem.tsv"))
        }
        "data/pinyin/common_usage_pairs.txt" => {
            Some(include_bytes!("../data/pinyin/common_usage_pairs.txt"))
        }
        "data/pinyin/coverage.json" => Some(include_bytes!("../data/pinyin/coverage.json")),
        "data/pinyin/everyday_phrases.md" => {
            Some(include_bytes!("../data/pinyin/everyday_phrases.md"))
        }
        "data/pinyin/everyday_phrases.tsv" => {
            Some(include_bytes!("../data/pinyin/everyday_phrases.tsv"))
        }
        "data/pinyin/mvp_lexicon.tsv" => Some(include_bytes!("../data/pinyin/mvp_lexicon.tsv")),
        "data/pinyin/phrases/coverage.json" => {
            Some(include_bytes!("../data/pinyin/phrases/coverage.json"))
        }
        "data/pinyin/phrases/manifest.json" => {
            Some(include_bytes!("../data/pinyin/phrases/manifest.json"))
        }
        "data/pinyin/phrases/NOTICE.md" => Some(include_bytes!("../data/pinyin/phrases/NOTICE.md")),
        "data/pinyin/phrases/phrase_lexicon.tsv" => {
            Some(include_bytes!("../data/pinyin/phrases/phrase_lexicon.tsv"))
        }
        "data/pinyin/phrases/proper_lexicon.tsv" => {
            Some(include_bytes!("../data/pinyin/phrases/proper_lexicon.tsv"))
        }
        "data/pinyin/phrases/quality-cases.json" => {
            Some(include_bytes!("../data/pinyin/phrases/quality-cases.json"))
        }
        "data/pinyin/phrases/sources/CC-BY-SA-4.0.txt" => Some(include_bytes!(
            "../data/pinyin/phrases/sources/CC-BY-SA-4.0.txt"
        )),
        "data/pinyin/phrases/sources/dict.txt" => {
            Some(include_bytes!("../data/pinyin/phrases/sources/dict.txt"))
        }
        "data/pinyin/phrases/sources/LICENSE-jieba.txt" => Some(include_bytes!(
            "../data/pinyin/phrases/sources/LICENSE-jieba.txt"
        )),
        "data/pinyin/sources/kMandarin_8105.txt" => {
            Some(include_bytes!("../data/pinyin/sources/kMandarin_8105.txt"))
        }
        "data/pinyin/sources/LICENSE-pinyin-data.txt" => Some(include_bytes!(
            "../data/pinyin/sources/LICENSE-pinyin-data.txt"
        )),
        "data/pinyin/sources/manifest.json" => {
            Some(include_bytes!("../data/pinyin/sources/manifest.json"))
        }
        "data/pinyin/sources/NOTICE.md" => Some(include_bytes!("../data/pinyin/sources/NOTICE.md")),
        "data/pinyin/sources/thuocl/LICENSE" => {
            Some(include_bytes!("../data/pinyin/sources/thuocl/LICENSE"))
        }
        "data/pinyin/sources/thuocl/manifest.json" => Some(include_bytes!(
            "../data/pinyin/sources/thuocl/manifest.json"
        )),
        "data/pinyin/sources/thuocl/README.md" => {
            Some(include_bytes!("../data/pinyin/sources/thuocl/README.md"))
        }
        "data/pinyin/sources/UNICODE-LICENSE.txt" => {
            Some(include_bytes!("../data/pinyin/sources/UNICODE-LICENSE.txt"))
        }
        _ => None,
    }
}
