# DCVlog｜代川的化妆师Vlog编导 Skill

> V1.3.0 主线采访引擎重构版：不再默认从“客人来干嘛”开始，而是先锁定学员最想讲、记忆最深的主切口；允许少量辅料补充，但成稿前强制删减，避免把采访素材全部罗列出来。

**唯一身份：** `daichuan-ai / dcvlog / /dcvlog`  
**唯一仓库：** `https://github.com/daichuan-ai/dcvlog`

## 学员安装

复制这一句给支持 Skills CLI 的 Agent：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后重新打开 App。以后开始写：

```text
/dcvlog
```

## V1.3.0 主要变化

- 每个新对话仍重新认识化妆师基础资料；
- 当天先问客人数；
- 当前客人不再默认问“来干嘛”，先选五种主切口；
- 锁主线后只深挖 2—4 个问题，再做 1—2 个辅料扫描；
- 素材分 A/B/C，真实但带散主线的信息可删；
- 单客人成稿固定只承担五个功能：开场 → 人物事件 → 解决 → 结果画面解释 → 结尾；
- 多客人第一个最完整，后面递减；最多只在第1和第2个客人间加一次桥接；
- 前5秒继续固定四方向，后置处理；
- 标准镜头继续默认已拍齐；
- 人设结尾可放弃；
- 最后先试读，再轻量选择语气；
- 运行 references 从 19 个收拢为 6 个核心文件，开发日志/测试不参与运行。

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
- Version: `1.3.0`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
