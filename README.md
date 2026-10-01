# DCVlog｜代川的化妆师Vlog编导 Skill

> V1.5.0 服务主线 + 成熟样本长度校准版：采访不再默认往“五官改造”带；场景/用途、客户真实需求、具体麻烦、前后变化都可以直接成为主线。最终写稿只选一条服务故事，并用成熟化妆师同类型样本的结构、句子密度和文字长度做硬校准。

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

## V1.5.0 主要变化

- 把“场景/用途”提升为正式主线：生日、领证、约会、见家长、面试、拍照等不再只是辅料；
- 客人普通人的真实需求与专业化妆问题地位平等，不要求客户说专业话；
- 采访不再默认追问“第一眼看她哪里要改”，只有确实需要时才进入五官判断；
- 最终写稿先选唯一服务主线：场景/用途、真实需求、具体问题、变化/反差；
- 专业判断改为可选解释层，不再要求每篇必须有完整面诊或“成熟专业判断句”；
- 最终稿必须对照同类型成熟化妆师样本的有效字数、句子数和朗读长度；
- 默认以同类型成熟样本中位数的90%—110%为长度目标，防止AI因采访素材多而越写越长；
- 太长优先删信息，禁止靠超长复句压缩；太短不允许为了凑长度编事实；
- 继续维持6个运行核心 references，不继续膨胀 Skill。

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
- Version: `1.5.0`
- Author: `daichuan-ai`

Copyright © Daichuan. All rights reserved.
