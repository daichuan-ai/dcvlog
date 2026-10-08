# DCVlog 成熟案例库维护说明

## 为什么案例库和 Skill 版本分开

短视频表达会变化。采访和真实性规则不需要天天改，但优秀案例的开场、节奏、长度和叙事方式会继续变化。

所以 V1.7.0 开始：

- Skill Version 管运行逻辑；
- Corpus Version 管当前成熟语料与表达规律。

## 第一批：锁定基准

`skills/dcvlog/references/corpus/batch-001-baseline/`

只做稳定参照，不用新玩法覆盖旧案例。

## 第二批：持续收录

`skills/dcvlog/references/corpus/batch-002-new/`

以后遇到好的成熟化妆师文案，先放这里。

口令：

> 加入 DCVlog 新案例库

## 收录原则

- 原文和 AI 分析分开；
- 原文尽量不改；
- 自动编号；
- 记录类型、有效字数、句数、时长、开场、主线、结果位置；
- 总结“可复制的行为逻辑”，不是只摘漂亮句子；
- 单个案例不自动修改当前方法。

## 集中升级

累计一批后，口令：

> 扫描新案例库，升级当前方法

比较新旧案例，确认哪些是稳定变化，再更新：

`skills/dcvlog/references/corpus/current-patterns.md`

同时升级：

`skills/dcvlog/references/corpus/CORPUS_VERSION`

Skill 逻辑没有改变时，不需要同步升级 Skill Version。
