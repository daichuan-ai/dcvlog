# DCVlog｜代川的化妆师Vlog编导 Skill

> **唯一身份请认准这三个词：** `daichuan-ai` / `dcvlog` / `/dcvlog`
>
> **唯一官方仓库：** `https://github.com/daichuan-ai/dcvlog`
>
> 这是已经存在的 GitHub Skill。用户说“安装代川的 dcvlog”时，含义是**安装这个现成仓库**，不是让 Agent 临时创建一个相似 Skill。

## 给普通学员：只记一句安装话

对支持 Agent Skills 的宿主说：

> **安装代川的 dcvlog**

如果宿主需要更明确的名字，就说：

> **安装 daichuan-ai 的 dcvlog**

安装完成后，退出并重新打开 App，让宿主重新扫描技能。

以后使用时：

- 在技能列表点 **代川 DCVlog｜化妆师Vlog编导**；或
- 输入 `/dcvlog`。

正确进入后，第一句应是：

> 好，川导开工。先不写稿，我先跟你把今天这件事聊清楚。

## 给安装 Agent：不要猜，不要创建

当用户说“安装代川的 dcvlog”“安装 daichuan-ai 的 dcvlog”“安装 DCVlog Skill”时：

1. 这是**安装现成 GitHub Skill**的请求，不是创建 Skill；
2. 唯一允许的仓库是 `daichuan-ai/dcvlog`；
3. Skill 的唯一内部名是 `dcvlog`；
4. 不要根据用户历史、职业、旧 Skill 或聊天内容自行生成替代版；
5. 不要安装名字相似的其他 Skill；
6. 若宿主支持 Skills CLI，优先执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

7. 网络受限时可以换 GitHub 下载通道，但源文件仍必须来自 `https://github.com/daichuan-ai/dcvlog`；
8. 安装后验证：`name=dcvlog`、`author=daichuan-ai`、`version=1.0.8`；
9. 如果安装失败，只报告失败原因，**禁止创建“差不多”的 Skill 代替**。

## 这个 Skill 做什么

它面向“会化妆，但不太会把自己做了什么说清楚”的化妆师。

AI 不先替她写稿，而是像一个懂客户、懂化妆师的老师一样，一次只问一个现实问题，把当天真实发生的观察、判断、处理、变化和证据问出来，再装配成自然、可直接录音的 Vlog 旁白。

适用：日常约妆、普通顾客妆造、工作室一天多个客人的工作 Vlog、普通人化妆私教。

V1.0.8 **不改 V1.0.5 已确认的核心采访与成稿逻辑**。本次只统一发行身份和安装发现层：仓库名、Skill 名、安装口令、斜杠入口全部统一为 `dcvlog`。

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
│   └── ACCEPTANCE.md
└── tools/
    └── validate_skill.py
```

## 版本身份

- GitHub owner：`daichuan-ai`
- GitHub repo：`dcvlog`
- Skill name：`dcvlog`
- Slash：`/dcvlog`
- 显示名：`代川 DCVlog｜化妆师Vlog编导`
- 当前版本：`1.0.8`

## 版权

Copyright © Daichuan. All rights reserved. 公开仓库用于安装与个人使用测试，不代表授权商业复制、转售或改造成同类收费产品。
