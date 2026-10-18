# DCVlog｜代川的化妆师内容 Skill

> V1.8.4 真实原文与初级化妆师采访修复版：接入19条不改动的成熟Vlog原文，新增人物观察、审美取舍、妆后画面及反模板闸门；不再把“裙子配色+客人满意”当成熟成稿。完整继承 V1.8.3 的拼图比例保护、原有双入口与 CloudBase 匿名统计。

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

已安装以后，直接说：

> 更新 DCVlog

自 V1.8.2 起不再依赖 `skills update dcvlog`。豆包工作里有些安装会被识别成 `local`，导致 update 找不到远程来源；现在统一从官方 GitHub 仓库重新覆盖安装最新版：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

这也是推荐的手动更新命令。完成后新开聊天或重新加载，再输入 `/dcvlog`。

如果宿主不能执行命令，Skill 只会返回这条命令，不会假装更新成功，也不会自行生成一个假的本地 DCVlog。

## V1.8.4 写文案主要变化

- 新增 `references/aesthetic-interview.md`：初级化妆师只会回答技术步骤时，帮助找真实人物印象、审美选择和妆后状态。
- 新增 `references/visual-result-draft-gate.md`：不允许“生日+裙子配色+客人满意”的固定模板冒充工作Vlog；检查结果画面和真实性。
- 新增 `references/corpus/batch-003-raw-20261016/`：保存19条原始Vlog，原文逐字不改；通过独立索引找到同类型客人段落。
- 单客视频比较单个客人段落长度，不拿完整多客人Vlog全篇作标尺。
- 保留V1.8.3拼图、CloudBase功能事件统计、双入口和更新功能。**这份包还需由你安装/更新到豆包，不能视为已在手机生效。**

## V1.8.3 主要变化

- 仅更新拼图引擎：原图宽高比锁定，任何版式不得拉伸人物；
- 新增细节裁剪审美中心与失败裁法；
- 没有好细节时允许减少局部图数量，不为凑版硬裁；
- 写文案采访、写作规则、案例库与长度逻辑全部原样保留；

- 修复豆包工作里 `dcvlog` 被识别成 `local` 后，`skills update dcvlog` 报“找不到已安装 Skill”的问题；
- “更新 DCVlog”改为直接执行 `npx -y skills add daichuan-ai/dcvlog -g --all`；
- 更新时不再追问“要改哪里/换什么”，不再把维护请求误当成内容编辑任务；
- 严禁更新失败后现场生成一个假的本地 DCVlog；
- 更新成功后提示新开聊天或重新加载，再使用 `/dcvlog`；

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

V1.8.3 继续支持统计“用了没有、用的是哪一项、有没有完成”，但不会读取学员的具体内容。

后台配置与查看方法见：`docs/ANALYTICS_SETUP.md`。

> CloudBase 统计接口继续沿用；学员无需配置，统计只记录功能事件、匿名 ID 与 Skill 版本。

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
- Skill Version: `1.8.4`
- Corpus Version: `1.1.0`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
