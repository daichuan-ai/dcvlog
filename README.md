# DCVlog｜代川的化妆师Vlog编导 Skill

> V1.5.1 三项实机修复版：修复“单客切口太宽、强画面开场理解错误、结尾解释过长”三个问题。现在会先区分当天实际服务人数与本条视频人数；单客主线不清楚时直接给明确切口；强画面按化妆师主角型Vlog开场处理，强情绪只用现场原声；结尾命中人设方向后直接压成3—4秒一句话。

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

## V1.5.1 主要变化

- 新增 `service_client_total` 与 `video_client_total`，彻底分开“今天实际画几位”和“这条视频讲几位”；
- 视频只讲1位时，禁止再问“这个客人大概什么情况/给我一个标签”，主线不清楚就直接给5个明确切口；
- 多客视频不再先收所有人的宽泛识别标签，直接按视频顺序逐位采访；
- 强画面重新定义为“化妆师主角型Vlog开场”：漂亮工作室远中近景/本人高审美出镜 + 身份型一句话，再进入客人；
- 没有主角型强画面时，允许从客人坐下/脸部画面直接进入；
- 强情绪必须使用当天真实现场原声，输出明确标注“（视频原声）/（现场原声）”；
- 结尾命中负责任、审美高、定制化、细节控等方向后，不再继续追问解释，直接给最多2个3—4秒人设尾巴；
- 开场/结尾用词增强记忆点，减少模糊词；表达可强，事实必须真；
- 保留V1.5.0的服务主线与成熟样本长度硬校准；运行时仍只有6个核心 references。

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
- Version: `1.5.1`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
