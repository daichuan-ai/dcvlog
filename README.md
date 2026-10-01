# DCVlog｜代川的化妆师Vlog编导 Skill

> V1.5.2 多客人叙事权重与时长修复版：在V1.5.1的切口/开场/结尾修复基础上，新增“第1个讲故事，第2个讲重点，第3个以后看结果”的强制递减；多客人总时长随人数自然增长，不再被单客约40秒上限卡住。

**唯一身份：** `daichuan-ai / dcvlog / /dcvlog`  
**唯一仓库：** `https://github.com/daichuan-ai/dcvlog`

## 学员安装

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后重启宿主，再输入：

```text
/dcvlog
```

## 已安装用户更新

新建对话，直接执行：

```bash
npx -y skills update dcvlog -g -y
```

更新完成后重启宿主，再输入 `/dcvlog`。

若更新命令无法识别已安装 Skill，可重新执行安装命令覆盖安装。

## V1.5.2 主要变化

- 保留V1.5.1的三项实机修复：单客明确切口、主角型强画面/现场原声开场、3—4秒人设结尾；
- 多客人成稿不再“每位都像完整小作文”：第1位讲故事，第2位只讲一个最强新点，第3位以后越来越轻；
- 第2位必须减少叙事层级，不只是字数少一点；
- 单客人常见20多秒—30/40秒只作为单客参考；两位、三位、四位客人时，总时长允许自然增长；
- 禁止为了守住固定40秒，把后面客人压成信息残缺；
- 多客人优先拿同客人数/相近客人数成熟样本做长度校准；无匹配样本时不设固定总秒数；
- 单客人的110—170字/约40秒不能作为多客整条视频上限；
- 运行时仍只有6个核心 references。

## 仓库结构

```text
dcvlog/
├── README.md
├── INSTALL_DOUABO.md
├── INSTALL_WORKBUDDY.md
├── VERSION
├── CHANGELOG.md
├── docs/
├── skills/
│   └── dcvlog/
│       ├── SKILL.md
│       └── references/   # 6个运行核心文件
├── tests/
└── tools/
```

## 版本

- Skill name: `dcvlog`
- Slash: `/dcvlog`
- Version: `1.5.2`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
