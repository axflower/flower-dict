# flower-dictionary

可复用、完全离线的中文拼音词库。它是数据包，不是输入法引擎：不依赖Flower、Windows、TSF、网络、用户配置或AI运行时，可供其他输入法、检索和文本工具使用。

当前源码版本为 **0.2.0本地候选**，尚未发布到crates.io。全量词目与可拼音读取的数据分别提供：

| 项目 | 数量 |
|---|---:|
| 完整、去重词目 | 2,168,043 |
| 默认拼音/文字对 | 2,088,650 |
| 保留的0.1.0默认词对 | 201,109 |
| 新增自动注音词对 | 1,887,541 |
| 英文、混输、符号和表情等非拼音词目 | 42,662 |
| 待补读音的生僻字及其他中文文本 | 45,313 |

完整词目包含已有可靠读音的192,527项、自动注音的1,887,541项及上述两类非拼音/待补项。词目收录不等于每项均有可靠读音；自动注音没有逐词人工核对。待补项完整保留于`data/pinyin/vocabulary/unresolved.txt`。

```toml
[dependencies]
# 0.2.0发布后使用；当前可在本地checkout通过path依赖验证
flower-dictionary = "=0.2.0"
```

```rust
use flower_dictionary::{default_tables, entries};

for table in default_tables() {
    for result in table.entries() {
        let entry = result?;
        // entry.pinyin: 规范拼音，音节用英文单引号分隔，ü写作v
        // entry.text: UTF-8文字；entry.weight: 来源权重或明确标注的人工权重
        let _ = (entry.pinyin, entry.text, entry.weight);
    }
}
# Ok::<(), flower_dictionary::ParseError>(())
```

## 数据接口

- `TABLES` / `all_tables()`：19张公开拼音词表，包含可选专名和旧MVP审计表。
- `default_tables()`：17张默认表，新增`expanded`，不自动启用专名和MVP。
- `table(id)`：按稳定标识选择特定表，如`characters`、`core`、`everyday`、`IT`、`medical`、`proper`。
- `DEFAULT_TSV`：保留原默认顺序并在末尾追加扩充表的静态UTF-8 TSV；`EVERYDAY_TSV`：803条人工日常表达。
- `entries(tsv)` / `Table::entries()`：借用源文本、逐行解析；跳过空行及`#`注释，坏记录返回一基行号，继续迭代不会吞掉后续记录。权重为正`u32`。
- `asset(path)`：按精确相对路径读取随crate携带的公开元数据或数据字节；不访问文件系统，不识别任意绝对路径。
- `COMMON_USAGE_PAIRS`：可选项目人工日常分类，空白分隔的`拼音=文字`；不是统计词频，也不要求其他消费者采用相同排名。
- `VOCABULARY_TSV` / `vocabulary()`：完整词目及读音状态，按文字排序且去重，包含无法装入拼音表的词目；不访问文件系统。
- `VocabularyEntry { text, reading_kind }` / `ReadingKind::{Existing, Automatic, Literal, Unresolved}`：分别表示既有词表读音、自动注音、非拼音文字和待补读音。拼音本身仍由各拼音表提供。

不同表可能重合，默认迭代保留记录而不暗中去重。当前默认表并集为2,088,650个拼音/文字对；消费者可按词对合并并取最大权重。新增扩充表统一使用项目权重1，旧词对及权重保留原值。字表、词组和人工表权重的语料来源不同，不应当成统一统计概率。全拼、简拼、混拼索引、分词、候选排序、学习和用户文件由消费者自己实现。无Rust消费者也可读取公开TSV进行转换。完整静态数据会增加编译产物和消费者索引的体积，消费者应自行评估加载时间与内存。

```rust
use flower_dictionary::{vocabulary, ReadingKind};
for result in vocabulary() {
    let word = result?;
    if word.reading_kind == ReadingKind::Unresolved {
        // 完整保留文字，但不要假定它已有可查询拼音。
        let _ = word.text;
    }
}
# Ok::<(), flower_dictionary::ParseError>(())
```

## 格式与来源

拼音TSV三列为`拼音<TAB>文字<TAB>权重`，每行LF，UTF-8。既有单字和规范词保留原读音；儿化表保留明确的末尾r，不机械替换为er。旧MVP仅为历史fixture，不作为规范词音来源。新增词目优先复用已有精确整词读音，否则使用pypinyin 0.55.0自动推导；未知字保持待补状态，不生成多音字笛卡尔积。

完整词目TSV为`文字<TAB>状态`，状态`E/A/L/U`分别对应上述四个`ReadingKind`。文字不做繁简转换、大小写折叠或符号拆分；例如`X光`、`♔`和`⌝⌞⌟`均按原文字整体保留。约定词典及辅助运行候选的覆盖基准为2,154,359项，集合差集为0；工具检查片段、错词负例、内部控制标记和程序动态生成的无限输出不属于词目范围。契约见`design/vocabulary-0.2.0.md`。

包含Unihan单字、CC-CEDICT/jieba词组、THUOCL分类及项目独立人工短语。完整来源固定版本、URL、摘要、覆盖与修改说明见`data/pinyin/`中的manifest、coverage和NOTICE。运行数据中没有私人用户词、聊天文本、学习历史或AI模型。

## 许可

Rust接口代码：MIT，见`LICENSE-MIT`。既有数据包含Unicode-3.0、MIT和CC BY-SA 4.0，分别见`NOTICE.md`、`licenses/`及来源目录的完整许可；CC-CEDICT派生词表仍受归属、共享相同方式和修改告知等义务约束。新增数据公开再分发条件尚未完成核定，以`NOASSERTION`标识；本地候选不声称全部数据均可按MIT使用。Cargo通过`license-file = "NOTICE.md"`说明实际分层状态。公开发布前须完成新增数据的权利核定。

## 离线重建与验证

源码仓库保存重建输入和覆盖报告；crate归档只发布消费/验包所需文件。原始Unihan、压缩CEDICT、THUOCL语料、source-groups、provenance/rejected及新增词目输入`words.txt`等不进入crate。jieba快照和标准库生成器随crate供参考消费者验证排序来源，完整重建仍需源码仓库。扩充数据的`--check`仅需Python标准库，不联网、不重写文件；刷新注音另需维护依赖`pypinyin==0.55.0`，它不属于Rust运行依赖。

在完整仓库执行（Python3.11+，无第三方Python依赖，无网络）：

```text
python -m unittest scripts.test_lexicon scripts.test_phrases scripts.test_categories scripts.test_vocabulary
python scripts/build_lexicon.py --check
python scripts/build_phrases.py --check
python scripts/build_categories.py --check
python scripts/build_vocabulary.py --check
# 只有需要重新生成注音时运行：
# python scripts/build_vocabulary.py --refresh
cargo test
cargo package --allow-dirty
cargo publish --dry-run --allow-dirty
```

任何数据更新须同步来源摘要、派生覆盖、消费者可信清单和版本；不要只更新散列来掩盖不一致。发布到crates.io前核对最终归档与账号权限；`--dry-run`不是已经发布。
