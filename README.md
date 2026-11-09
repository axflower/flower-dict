# flower-dictionary

可复用、完全离线的中文拼音词库。它是数据包，不是输入法引擎：不依赖Flower、Windows、TSF、网络、用户配置或AI运行时，可供其他输入法、检索和文本工具使用。

```toml
[dependencies]
flower-dictionary = "0.1.0"
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

- `TABLES` / `all_tables()`：18张公开词表，包含可选专名和旧MVP审计表。
- `default_tables()`：16张默认表，不自动启用专名和MVP。
- `table(id)`：按稳定标识选择特定表，如`characters`、`core`、`everyday`、`IT`、`medical`、`proper`。
- `DEFAULT_TSV`：原默认顺序拼接的静态UTF-8 TSV；`EVERYDAY_TSV`：803条人工日常表达。
- `entries(tsv)` / `Table::entries()`：借用源文本、逐行解析；跳过空行及`#`注释，坏记录返回一基行号，继续迭代不会吞掉后续记录。权重为正`u32`。
- `asset(path)`：按精确相对路径读取随crate携带的公开元数据或数据字节；不访问文件系统，不识别任意绝对路径。
- `COMMON_USAGE_PAIRS`：可选项目人工日常分类，空白分隔的`拼音=文字`；不是统计词频，也不要求其他消费者采用相同排名。

不同表可能重合，默认迭代保留来源记录而不暗中去重。当前默认表并集为201109个拼音/文字对；消费者可按词对合并并取最大权重。字表、词组和人工表权重的语料来源不同，不应当成统一统计概率。全拼、简拼、混拼索引、分词、候选排序、学习和用户文件由消费者自己实现。所谓可复用不表示所有输入法都能直接导入TSV，无Rust消费者也可读取公开TSV进行转换。

## 格式与来源

TSV三列为`拼音<TAB>文字<TAB>权重`，每行LF，UTF-8。单字和规范词保留来源支持的读音；儿化表保留明确的末尾r，不机械替换为er。旧MVP仅为历史fixture，不作为规范词音来源。

包含Unihan单字、CC-CEDICT/jieba词组、THUOCL分类及项目独立人工短语。完整来源固定版本、URL、摘要、覆盖与修改说明见`data/pinyin/`中的manifest、coverage和NOTICE。运行数据中没有私人用户词、聊天文本、学习历史或AI模型。

## 许可

Rust接口代码：MIT，见`LICENSE-MIT`。数据包含Unicode-3.0、MIT和CC BY-SA 4.0，分别见`NOTICE.md`、`licenses/`及来源目录的完整许可。Cargo并存许可表达式不将所有数据重新许可为MIT；CC-CEDICT派生词表仍受归属、共享相同方式和修改告知等义务约束。使用者须按实际分发数据保留适用归属和许可。

## 离线重建与验证

源码仓库保存全部公开原始快照和审计报告；crate归档只发布消费/验包所需文件。原始Unihan、压缩CEDICT、THUOCL语料、source-groups、provenance/rejected等不进入crate。jieba快照和标准库生成器随crate供参考消费者验证排序来源，完整重建仍需源码仓库。

在完整仓库执行（Python3.11+，无第三方Python依赖，无网络）：

```text
python -m unittest scripts.test_lexicon scripts.test_phrases scripts.test_categories
python scripts/build_lexicon.py --check
python scripts/build_phrases.py --check
python scripts/build_categories.py --check
cargo test
cargo package --allow-dirty
cargo publish --dry-run --allow-dirty
```

任何数据更新须同步来源摘要、派生覆盖、消费者可信清单和版本；不要只更新散列来掩盖不一致。发布到crates.io前核对最终归档与账号权限；`--dry-run`不是已经发布。
