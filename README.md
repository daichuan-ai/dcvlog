# DCVlog｜代川的化妆师内容 Skill

> V1.8.1 CloudBase 匿名统计接通版：完整保留旁白、拼图、持续案例库与自然语言更新，并把匿名功能统计正式接到腾讯云 CloudBase。

**唯一身份：** `daichuan-ai / dcvlog / /dcvlog`  
**唯一仓库：** `https://github.com/daichuan-ai/dcvlog`

## 学员安装

### 自然语言方式

在豆包工作新对话里可以直接说：

> 帮我安装代川的 DCVlog 技能，GitHub 来源是 daichuan-ai/dcvlog，安装为全局技能并自动确认。

如果宿主支持执行命令，应等价执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后重启宿主，再输入：

```text
/dcvlog
```

现在会看到两个入口：

1. 我要开始写文案
2. 我要做拼图

也可以直接自然语言输入“我要开始写文案”或“我要做拼图”。

## 已安装用户更新

已安装以后，优先直接说：

> 更新 DCVlog

Skill 会尝试直接执行：

```bash
npx -y skills update dcvlog -g -y
```

如果当前宿主不能执行命令，它会只返回这条命令，不会假装已经更新。

更新完成后重启宿主，再输入 `/dcvlog`。

## V1.8.1 主要变化

- 完整继承 V1.7.0 全部功能；
- 新增匿名事件：打开、写文案开始/完成、拼图开始/完成、更新请求；
- 只记录事件名、Skill版本和本地随机匿名 ID；
- 不上传聊天文字、照片、客户信息、工作室名称或生成结果；
- 统计失败不影响任务；
- 匿名统计已切换到腾讯云 CloudBase；
- 新安装/更新后无需学员配置统计 Token；
- 统计接口失败或网络不可达时静默跳过，不影响主功能。

## 案例库怎么长期更新

以后代川遇到新的成熟化妆师好文案，可以直接说：

> 加入 DCVlog 新案例库

贴原文即可。

新案例先进入第二批，不会立刻污染稳定规则。

积累一批以后再说：

> 扫描新案例库，升级当前方法

系统会拿第一批基准和第二批新案例做对照，只把稳定的新趋势写进当前方法。


## 匿名使用统计

V1.8.1 可以统计“用了没有、用的是哪一项、有没有完成”，但不会读取学员的具体内容。

后台配置与查看方法见：`docs/ANALYTICS_SETUP.md`。

> V1.8.1 已接通腾讯云 CloudBase 统计接口。学员无需配置；统计只记录功能事件、匿名 ID 与 Skill 版本。

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
│       └── references/
│           ├── 7个原有核心运行文件
│           └── corpus/
│               ├── CORPUS_VERSION
│               ├── corpus-index.md
│               ├── current-patterns.md
│               ├── batch-001-baseline/
│               │   └── cases.md
│               └── batch-002-new/
│                   └── README.md
├── tests/
└── tools/
```

## 版本

- Skill name: `dcvlog`
- Slash: `/dcvlog`
- Skill Version: `1.8.1`
- Corpus Version: `1.0.0`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
