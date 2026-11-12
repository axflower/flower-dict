# 新增来源词目与词组权重

来源：iDvel/rime-ice contributors，https://github.com/iDvel/rime-ice ，固定提交 `927e1cf1d3eeb9bf4be85e3f684dba4dd485b6f6`。上游声明 GPL-3.0-only；完整许可见 `../sources/rime_ice/LICENSE`。本次新增派生词目与词表保留该许可，既有其他来源条款及 NOASSERTION 状态不变。

`../sources/rime_ice/manifest.json` 固定27个来源文件的大小、SHA-256与Git blob身份。源码仓库保留原字节；crate只带运行表、覆盖、此通知、来源manifest和完整许可，不带全部重建原料。同步时不联网、不执行上游脚本。

静态词目提取中文字/词表（含可选大字表）、根词表、拆字字表、英文表、中英混输、自定义短语、OpenCC键和完整候选、symbols完整候选字符串。保留原文，不拆符号串、不导入YAML结构键；排除注释、控制分隔行、空或控制字符候选、维护负例与动态无限输出。英文、混输、表情和符号进入完整词目API，不声称增加对应触发命令。

`lexicon.tsv` 只从五张默认中文表取显式规范拼音（声调去除、ü写v、音节用单引号分隔）及词组权重，同词对按上游导入顺序首条优先。腾讯表无显式读音，不伪造；未提供权重时使用项目低权重1。词组采用项目校准尺度`max(1,min(8192,raw_weight//64))`，不是统一统计频率；原始权重保留于来源快照。直接复制原权重的试验导致既有常用词退位，因此不能混用几十万来源权重与既有日常prior。既有基线单字读音不加权，新增单字读音以1收录，避免文字总频率跨读音档使用。原基础表/自动音表不重写，消费者按同词对max合并，旧词对保留。

完整词目和自动音只增量增加新词，历史A/E/L/U标记描述原基础/自动注音子系统，不代表新增显式来源表没有其他读音。`coverage.json` 分别报告完整词目差集、独立词表及默认总词对；原vocabulary/coverage.json仍报告基础表与自动音子系统，不把重叠行重复计作新词。

维护入口：固定 PyYAML 6.0.3；刷新另需 pypinyin 0.55.0。

```text
python -m scripts.sync_rime_ice --refresh
python -m scripts.sync_rime_ice --check
python scripts/build_vocabulary.py --check
```

前两个命令需要完整源码仓库内的固定原料；原vocabulary只读检查仍使用Python标准库。所有数量、排除计数及输出摘要以同目录coverage为准。此为未发布本地更新，不代表消费者已锁定远端新提交。
