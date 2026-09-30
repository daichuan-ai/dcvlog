# DCVlog｜代川的化妆师Vlog编导 Skill

> **唯一身份：** `daichuan-ai` / `dcvlog` / `/dcvlog`
>
> **唯一官方仓库：** `https://github.com/daichuan-ai/dcvlog`

这是已经存在的 GitHub Skill，不是让 Agent 临时生成一个相似 Skill。

## 给普通学员：只记两句话

第一次安装，直接复制：

> **安装 GitHub 上 daichuan-ai/dcvlog 的 Skill，只安装现成仓库，不要帮我生成或创建新 Skill。**

以后每次开始写：

> **/dcvlog**

目前实机测试中，`/dcvlog` 比等待技能菜单出现更稳定。只要 `/dcvlog` 能找到已安装的 `dcvlog` 并读取它的说明，就可以直接使用。

## 正确启动应该发生什么

如果是这个新对话第一次使用，Skill 不应该直接问“今天这个客人来干嘛”，也不应该说“川导开工”这种开发测试口令。

它应该先自然认识化妆师：

> 好，那咱们开始。我先认识一下你。你是哪一年的？

随后一次只问一个：城市 → 做化妆多久 → 当前工作状态/主要业务。认识完以后再进入今天，先确认今天一共几个客人，然后逐个聊。

## 给安装 Agent：不要猜，不要创建

当用户提出安装时：

1. 这是安装现成 GitHub Skill，不是创建 Skill；
2. 唯一仓库：`daichuan-ai/dcvlog`；
3. 唯一 Skill name：`dcvlog`；
4. 不得根据用户历史、职业、旧 Skill 或聊天内容生成替代版；
5. 若宿主支持 Skills CLI，优先：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

6. 网络受限可以换 GitHub 下载通道，但源文件必须来自上述仓库；
7. 安装后验证：`name=dcvlog`、`author=daichuan-ai`、`version=1.1.0`；
8. 安装失败只报告失败原因，禁止创建“差不多”的 Skill 代替。

## 这个 Skill 做什么

它面向“会化妆，但不太会把自己做了什么说清楚”的化妆师。

AI 不先替她写稿，而是先进入目标客户的脑子里，再像一个懂化妆师的老师一样聊天式采访。一次只问一个真实问题，把当天已经发生的观察、判断、处理、变化和证据问出来，再装配成自然、可直接录音的 Vlog 旁白。

提问深度以“目标观众愿意听懂”为准，不是把化妆师所有专业知识都挖出来。

适用：日常约妆、普通顾客妆造、工作室一天多个客人的工作 Vlog、普通人化妆私教。

V1.1.0 是从 V1.0.5 开始多轮实机测试后的回归整合版：保留 V1.0.5 的采访、卡壳救援、多客人装配、前5秒选择、结尾人设、本人语气定型等核心能力，同时修复安装/调用混乱、错误替代 Skill、首次人物认识被跳过、开发测试口令残留等问题。

## 仓库结构

```text
dcvlog/
├── README.md
├── INSTALL_WORKBUDDY.md
├── INSTALL_DOUABO.md
├── VERSION
├── CHANGELOG.md
├── docs/
│   └── V1.0.5_TO_V1.0.8_DEVLOG.md
├── skills/
│   └── dcvlog/
│       ├── SKILL.md
│       └── references/
├── tests/
│   ├── ACCEPTANCE.md
│   └── REGRESSION_CASES.md
└── tools/
    └── validate_skill.py
```

## 版本身份

- GitHub owner：`daichuan-ai`
- GitHub repo：`dcvlog`
- Skill name：`dcvlog`
- Slash：`/dcvlog`
- 显示名：`代川 DCVlog｜化妆师Vlog编导`
- 当前版本：`1.1.0`

## 版权

Copyright © Daichuan. All rights reserved. 公开仓库用于安装与个人使用测试，不代表授权商业复制、转售或改造成同类收费产品。
