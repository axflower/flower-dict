# flower-dict

可复用、完全离线的中文拼音词库。它是数据包，不是输入法引擎：不依赖Flower、Windows、TSF、网络、用户配置或AI运行时，可供其他输入法、检索和文本工具使用。

当前源码版本为 **flower-dict 0.2.0**，本地包含尚未提交、推送的词目与来源权重更新。下面的Git依赖仍解析已发布提交，不会自动读取这些本地修改；本地验证使用显式隔离消费者，不修改正常依赖锁定。全量词目与可拼音读取的数据分别提供：

| 项目 | 数量 |
|---|---:|
| 完整、去重词目 | 2,168,318 |
| 默认拼音/文字对（全部来源去重） | 2,112,294 |
| 保留的0.1.0默认词对 | 201,109 |
| 基础扩充子系统的自动注音词对 | 1,887,815 |
| 基础扩充子系统的非拼音词目 | 42,663 |
| 待补读音的生僻字及其他中文文本 | 45,313 |

基础扩充子系统保留已有读音192,527项、自动注音1,887,815项及上述两类状态。历史状态描述该子系统的注音来源，新增显式来源表可独立提供其他读音；不以历史状态否认额外来源的读音。词目收录不等于每项均有可靠读音或对应输入功能；自动注音没有逐词人工核对。基础待补项保留于`data/pinyin/vocabulary/unresolved.txt`。

本轮保留全部旧词目/词对，完整目录新增275词；固定上游静态集合1,986,007词目，差集为0。新增独立来源表883,073词对，其中23,370词对原默认并集没有；另有274个新增自动音词对，默认总词对净增23,644。校准后使318,318个重合词对可获得更高默认权重，不修改个人排序或手工prior。词组使用项目尺度`max(1,min(8192,raw_weight//64))`，不是原始频率；原始权重留在来源快照。既有单字读音不导入全局文字频率，新增单字读音低权重收录。直接复制原权重的试验发生常用词退位，不作为最终排序通过证据，真实排名由消费者验证。

```toml
[dependencies]
flower-dict = { git = "https://github.com/axflower/flower-dict.git", branch = "main", version = "=0.2.0" }
```

```rust
use flower_dict::{default_tables, entries};

for table in default_tables() {
    for result in table.entries() {
        let entry = result?;
        // entry.pinyin: 规范拼音，音节用英文单引号分隔，ü写作v
        // entry.text: UTF-8文字；entry.weight: 来源权重或明确标注的人工权重
        let _ = (entry.pinyin, entry.text, entry.weight);
    }
}
# Ok::<(), flower_dict::ParseError>(())
```

## 数据接口

- `TABLES` / `all_tables()`：20张公开拼音词表，包含可选专名和旧MVP审计表。
- `default_tables()`：18张默认表，包含`expanded`与`source-phrases`，不自动启用专名和MVP。
- `table(id)`：按稳定标识选择特定表，如`characters`、`core`、`everyday`、`IT`、`medical`、`proper`。
- `DEFAULT_TSV`：保留原默认顺序，在扩充表后追加显式来源词表；`EVERYDAY_TSV`：803条人工日常表达。
- `entries(tsv)` / `Table::entries()`：借用源文本、逐行解析；跳过空行及`#`注释，坏记录返回一基行号，继续迭代不会吞掉后续记录。权重为正`u32`。
- `asset(path)`：按精确相对路径读取随crate携带的公开元数据或数据字节；不访问文件系统，不识别任意绝对路径。
- `COMMON_USAGE_PAIRS`：可选项目人工日常分类，空白分隔的`拼音=文字`；不是统计词频，也不要求其他消费者采用相同排名。
- `VOCABULARY_TSV` / `vocabulary()`：完整词目及读音状态，按文字排序且去重，包含无法装入拼音表的词目；不访问文件系统。
- `VocabularyEntry { text, reading_kind }` / `ReadingKind::{Existing, Automatic, Literal, Unresolved}`：分别表示既有词表读音、自动注音、非拼音文字和待补读音。拼音本身仍由各拼音表提供。

不同表可能重合，默认迭代保留记录而不暗中去重。当前默认表并集为2,112,294个拼音/文字对；消费者可按词对合并并取最大权重。自动扩充表使用项目权重1，独立显式来源表使用上述校准尺度，旧表及其权重保留原值。字表、词组、人工表与显式来源的尺度不同，不应当成统一统计概率。全拼、简拼、混拼索引、分词、候选排序、学习和用户文件由消费者自己实现。无Rust消费者也可读取公开TSV进行转换。完整静态数据会增加编译产物和消费者索引的体积，消费者应自行评估加载时间与内存。

```rust
use flower_dict::{vocabulary, ReadingKind};
for result in vocabulary() {
    let word = result?;
    if word.reading_kind == ReadingKind::Unresolved {
        // 完整保留文字，但不要假定它已有可查询拼音。
        let _ = word.text;
    }
}
# Ok::<(), flower_dict::ParseError>(())
```

## 格式与来源

拼音TSV三列为`拼音<TAB>文字<TAB>权重`，每行LF，UTF-8。既有单字和规范词保留原读音；儿化表保留明确的末尾r，不机械替换为er。旧MVP仅为历史fixture，不作为规范词音来源。新增词目优先复用已有精确整词读音，否则使用pypinyin 0.55.0自动推导；未知字保持待补状态，不生成多音字笛卡尔积。

完整词目TSV为`文字<TAB>状态`，状态`E/A/L/U`分别对应上述四个`ReadingKind`。文字不做繁简转换、大小写折叠或符号拆分；例如`X光`、`♔`和`⌝⌞⌟`均按原文字整体保留。旧词目目标与本轮来源并集现为2,154,640项，缺词差集为0；工具检查片段、错词负例、内部控制标记和程序动态生成的无限输出不属于词目范围。`data/pinyin/vocabulary/coverage.json`报告基础扩充子系统，`data/pinyin/rime_ice/coverage.json`独立报告固定来源全量差集、完整默认并集和权重策略；不得将重合行数相加冒称新增词。

包含Unihan单字、CC-CEDICT/jieba词组、THUOCL分类及项目独立人工短语。完整来源固定版本、URL、摘要、覆盖与修改说明见`data/pinyin/`中的manifest、coverage和NOTICE。运行数据中没有私人用户词、聊天文本、学习历史或AI模型。

## 许可

Rust接口代码：MIT，见`LICENSE-MIT`。既有数据包含Unicode-3.0、MIT和CC BY-SA 4.0；本轮独立来源表为GPL-3.0-only，完整条款、固定身份与必要归属见`NOTICE.md`及各来源目录。既有自动扩充数据的公开再分发条件仍为`NOASSERTION`，不能被新来源许可覆盖。Cargo通过`license-file = "NOTICE.md"`说明分层状态，公开发布前仍须核定未决数据权利，不声称全部数据均可按MIT使用。

## 离线重建与验证

源码仓库保存重建输入和覆盖报告；crate归档只发布消费/验包所需文件。原始Unihan、压缩CEDICT、THUOCL语料、source-groups、provenance/rejected及新增词目输入`words.txt`等不进入crate。jieba快照和标准库生成器随crate供参考消费者验证排序来源，完整重建仍需源码仓库。扩充数据的`--check`仅需Python标准库，不联网、不重写文件；刷新注音另需维护依赖`pypinyin==0.55.0`，它不属于Rust运行依赖。

原有离线检查使用Python标准库；新增来源同步另需固定维护工具PyYAML 6.0.3，刷新还需pypinyin 0.55.0，不属于Rust运行依赖。完整仓库中使用 `python -m scripts.sync_rime_ice --refresh` 刷新，使用 `--check` 只读校验，不联网、不执行上游代码。来源原始快照仅留源码仓库；crate携带运行表、覆盖、必要通知/许可及manifest。

原有完整仓库检查（Python3.11+，无第三方Python依赖，无网络）：

```text
python -m unittest scripts.test_lexicon scripts.test_phrases scripts.test_categories scripts.test_vocabulary
python scripts/build_lexicon.py --check
python scripts/build_phrases.py --check
python scripts/build_categories.py --check
python scripts/build_vocabulary.py --check
# 只有需要重新生成注音时运行：
# python scripts/build_vocabulary.py --refresh
cargo test
cargo clippy --all-targets -- -D warnings
```

任何数据更新须同步来源摘要、派生覆盖、消费者可信清单和版本；不要只更新散列来掩盖不一致。通过GitHub同步后，消费者先用`cargo metadata`核对Git源和实际提交，再提交更新后的Cargo.lock；`--locked --offline`需要已经获取该提交。完整词库不拆成多个crate，Git依赖不受crates.io的单包上传体积限制。
