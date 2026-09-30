# Changelog

## 1.0.8

- **发行身份统一**：GitHub 仓库目标改为 `daichuan-ai/dcvlog`，与 Skill 内部名 `dcvlog`、斜杠入口 `/dcvlog` 完全一致。
- 学员安装口令统一为“安装代川的 dcvlog”；需要更明确时使用“安装 daichuan-ai 的 dcvlog”。
- 显示名统一为“代川 DCVlog｜化妆师Vlog编导”。
- README 与安装文档明确：安装失败时不得根据用户背景或历史聊天自行生成替代 Skill。
- 新增完整 V1.0.5→V1.0.8 开发记录，写入 WorkBuddy 云端/本地环境差异，以及豆包工作误生成替代 Skill 的真实测试结论。
- **内容层不变**：V1.0.5 已确认的采访、卡壳救援、多客人装配、开场选择、结尾、人类语气等核心逻辑全部保留。

# CHANGELOG

## 1.0.7

本版不改 V1.0.5 已确认的采访与成稿核心，只修“安装、发现、调用”这一层，并吸收 V1.0.5 之后两轮真实平台测试结果。

- Skill 内部名由 `dc-makeup-vlog` 调整为 `dcvlog`，提供更短、更稳定的 `/dcvlog` 手动入口。
- 明确支持三种入口：技能菜单选择、`/dcvlog`、自然语言暗号；宿主已经显式调用后不再要求重复暗号。
- frontmatter 精简为宿主公开支持的核心字段，并强化 description 中的真实使用场景与触发方式。
- 所有 references 按 WorkBuddy 文档推荐改为 `@references/...` 引用。
- README 顶部加入唯一官方仓库、作者、Skill 名和自然语言安装别名，增强 GitHub/Agent 搜索可发现性。
- 新增“安装一个现成 Skill，不得自行创建替代 Skill”的安装约束，针对实测中 Agent 找不到仓库后擅自生成 Skill 的错误路径。
- 安装命令统一采用 `npx -y skills add daichuan-ai/dc-makeup-vlog -g --all`，与 dbskill 同类仓库结构保持一致。
- 加入安装后重启 App/重新扫描技能的实测提示。
- 新增从 V1.0.5 到 V1.0.7 的开发记录，保留本轮真实测试结论。

## 1.0.6

- 增加专属自然语言路由暗号与“川导开工”身份回执。
- 增强多 Skill 共存时的路由边界与新项目隔离。

## 1.0.5

- 完成采访人格、卡壳救援、素材价值闸门、多客人 Vlog 装配、前 5 秒开场、结尾人设、本人口吻定型等核心流程。
