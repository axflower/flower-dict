# 分层许可与归属

本包由独立Rust读取接口和多来源公开数据组成。它不是单一MIT词库。

- Rust接口及项目人工词表：Copyright (c) 2026 Flower contributors，MIT，完整条款见`LICENSE-MIT`。
- 单字读音：Unicode Unihan 17.0.0，Unicode-3.0；8105独立转录基线来自pinyin-data，MIT。完整条款见`licenses/UNICODE-3.0.txt`、`data/pinyin/sources/LICENSE-pinyin-data.txt`，原版本/URL/SHA及修改见来源manifest与NOTICE。
- CC-CEDICT：CC-CEDICT contributors / MDBG，历史CEDICT归属Paul Andrew Denisowski。核心、专名和CEDICT词级补充/儿化为派生数据，CC BY-SA 4.0。完整条款见`licenses/CC-BY-SA-4.0.txt`及`data/pinyin/phrases/NOTICE.md`，来源固定时间和转换步骤保留于manifest。保留归属、链接、修改告知并以相同许可分享适用改编数据，不暗示原作者认可。
- jieba：Copyright (c) 2013 Sun Junyi，MIT；原始频次快照/许可/固定提交见`data/pinyin/phrases/sources/`及manifest。文字频率不等于读音频率；人工映射不冒称统计概率。
- THUOCL：Tsinghua Open Chinese Lexicon，MIT；完整版权、引用、许可及转换读音来源见`data/pinyin/sources/thuocl/`与`data/pinyin/categories/NOTICE.md`。分类中的CEDICT派生读音仍保留其CC BY-SA义务，不以THUOCL的MIT覆盖。
- 新增来源词表与本轮新增词目：iDvel/rime-ice contributors，固定提交`927e1cf1d3eeb9bf4be85e3f684dba4dd485b6f6`，上游声明GPL-3.0-only；完整条款见`data/pinyin/sources/rime_ice/LICENSE`，逐文件身份与转换说明见同目录manifest及`data/pinyin/rime_ice/NOTICE.md`。本次补齐静态词目并转换显式词组读音/权重，没有复制或执行上游输入法脚本。它不改变其他来源的许可，也不解决既有NOASSERTION数据的权利状态。

0.1.0将既有公开数据从Flower仓库迁出，迁移前后默认201109个词对保持不变。0.2.0保留这些既有数据与许可，并增加独立词目集合及自动注音扩充表；没有读取/收录私有用户词、排序历史、聊天或配置。

自动注音维护工具为pypinyin 0.55.0，MIT，完整条款见`licenses/LICENSE-pypinyin.txt`。新增读音经过自动推导，不能冒称人工核对。新增词目数据的公开再分发条件尚未完成核定，以`NOASSERTION`标识；本地候选不将其重新授权为完全MIT。Cargo使用本通知作为`license-file`，原有MIT、Unicode和CC BY-SA等义务继续适用，不能任意选取一种许可覆盖整个发行物。公开发布前仍须完成新增数据的权利核定。

各源完整声明、修改步骤与固定字节摘要随数据保留；完整重建原料在源码仓库，发布归档为消费子集。任何使用者须根据实际复制和分发部分遵守适用条款，本说明不替代法律意见。
