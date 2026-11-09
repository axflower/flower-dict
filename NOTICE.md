# 分层许可与归属

本包由独立Rust读取接口和多来源公开数据组成。它不是单一MIT词库。

- Rust接口及项目人工词表：Copyright (c) 2026 Flower contributors，MIT，完整条款见`LICENSE-MIT`。
- 单字读音：Unicode Unihan 17.0.0，Unicode-3.0；8105独立转录基线来自pinyin-data，MIT。完整条款见`licenses/UNICODE-3.0.txt`、`data/pinyin/sources/LICENSE-pinyin-data.txt`，原版本/URL/SHA及修改见来源manifest与NOTICE。
- CC-CEDICT：CC-CEDICT contributors / MDBG，历史CEDICT归属Paul Andrew Denisowski。核心、专名和CEDICT词级补充/儿化为派生数据，CC BY-SA 4.0。完整条款见`licenses/CC-BY-SA-4.0.txt`及`data/pinyin/phrases/NOTICE.md`，来源固定时间和转换步骤保留于manifest。保留归属、链接、修改告知并以相同许可分享适用改编数据，不暗示原作者认可。
- jieba：Copyright (c) 2013 Sun Junyi，MIT；原始频次快照/许可/固定提交见`data/pinyin/phrases/sources/`及manifest。文字频率不等于读音频率；人工映射不冒称统计概率。
- THUOCL：Tsinghua Open Chinese Lexicon，MIT；完整版权、引用、许可及转换读音来源见`data/pinyin/sources/thuocl/`与`data/pinyin/categories/NOTICE.md`。分类中的CEDICT派生读音仍保留其CC BY-SA义务，不以THUOCL的MIT覆盖。

新包将既有公开数据从Flower仓库迁出，未读取/收录私有用户词、排序历史、聊天或配置；迁移前后默认201109个词对保持不变。接口代码和数据许可相互独立，crate的`MIT AND Unicode-3.0 AND CC-BY-SA-4.0`表达式说明发行物的并存许可，并非可任意选一种许可覆盖全部数据。

各源完整声明、修改步骤与固定字节摘要随数据保留；完整重建原料在源码仓库，发布归档为消费子集。任何使用者须根据实际复制和分发部分遵守适用条款，本说明不替代法律意见。
