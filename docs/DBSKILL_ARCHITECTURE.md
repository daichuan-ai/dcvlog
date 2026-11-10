# DB Skill 实现对照与 DCVlog 安装改造

本次读取的是 DB Skill v3.5.1，提交 `47f20494fbd1ee7cd739fd13049a1d04ffaaeebb`；DCVlog 集成基线为线上2.0.0，提交 `88d222873746e37fb433c5ffd7bafbdf72fcd4bf`。本机旧1.9.5工作区原文件保留，改造在独立集成目录完成。

## 实际读过的实现

| DB Skill 文件 | 实际机制 | DCVlog 对应实现 |
| --- | --- | --- |
| [README](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/README.md) | 标准 Skills CLI 安装入口 | 标准 `skills/dcvlog`；限定安装单个技能，避免写入所有 Agent |
| [.claude-plugin/plugin.json](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/.claude-plugin/plugin.json) 与 [marketplace.json](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/.claude-plugin/marketplace.json) | 主插件从仓库根加载，插件清单列出技能目录 | 两份清单；主插件 source 为仓库根，明确 skills 路径 |
| [install-skill.sh](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/skills/dbs-install-skill/scripts/install-skill.sh) | 公共技能源与宿主专属目录之间建立链接；包含 WorkBuddy | 新增独立编写的 `scripts/link_host.py`；复用 DCVlog 已有路径与整包校验；已有目录和冲突链接不覆盖 |
| [check-update.sh](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/skills/dbs/scripts/check-update.sh) | 最多每日检查一次版本，发现新版提醒用户更新 | 按代川要求保留每次启动核对提交并自动同步，不改成每日提醒 |
| [dbs-update](https://github.com/dontbesilent2025/dbskill/blob/47f20494fbd1ee7cd739fd13049a1d04ffaaeebb/skills/dbs-update/SKILL.md) | 区分插件安装与 CLI 安装；保留用户存档；需要重载 | 保留现有备份、失败恢复和用户数据；安装渠道分别验收，不拿另一个目录的更新冒充成功 |

DB Skill 现行许可对内容再分发有限制；这里借鉴工程结构，适配器由 DCVlog 独立实现，未复制它的脚本、提示词或知识库。

## 对 WorkBuddy 施工单的落实

落实标准目录、移除根 SKILL 入口、增加正确的插件双清单、标准 CLI 通道、宿主链接，以及新任务验收。DCVlog 原本已有标准目录，这次统一可安装入口，并未重新编写业务技能。root tools/references 仅保留历史兼容与开发用途。

保留完整包安装器与自动更新器：手机云端未必具备 Node/npx/Git，而 Python 标准库 ZIP 通道仍有价值；删除更新器会失去“每次使用自动同步”的现有能力。已有源能够被宿主发现时不额外复制，链接失败也不偷偷制造第二份副本。

`-g` 是运行机器／容器的全局文件范围。Skills CLI 的本地锁文件、Claude 插件清单或文件链接，都不能独立证明 WorkBuddy 账号持久注册或沙箱重建后恢复。不会把它们描述为平台账号 API。

## 手机云端的正确验收位置

[WorkBuddy 官方项目文档](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project) 说明：Web 与客户端个人技能库隔离，云上任务使用云上个人库；项目 Skill 配置在云端统一管理。

[手机官方说明](https://www.codebuddy.cn/docs/workbuddymini/features/Attachments-and-Skills) 推荐从 SkillHub 获取安装指令，安装后在技能列表选择。DCVlog 尚未取得本次可验证的 SkillHub 上架条目，不能编造市场 ID 或宣称已上架。

安装 AI 应先识别执行环境，使用当前环境的技能库／原生导入能力，然后检查：

1. 当前环境的技能列表中可见并启用 DCVlog。
2. 新建任务能发现技能，并确认本次实际加载路径。
3. 从该路径调用更新器，返回 verified:true，重读更新后的规则。
4. 相同版本发布新案例，再次启动可同步。
5. 若平台允许重建／更换沙箱，再验证列表和加载路径；仅换一个进程不等于换云容器。

本地脚本始终返回 `host_registration_verified:false`、`cloud_persistence_verified:false`，直到由宿主列表和跨任务／跨容器证据另外确认。若平台只提供手动导入而无可调用注册工具，交付完整 ZIP 并说明这一项必要操作；不能保证所有手机环境只靠聊天命令就完成账号安装。

## 不变的内容

集成基线61个现有运行文件逐一 SHA-256 对照，包括完整 SKILL.md、约妆和跟妆提示词、DB交接、全部 references、原 tools 与配置，均保持原字节。只在技能内新增宿主链接适配器。19条锁定原文仍为原有哈希。

旧版安装器仍从 `skills/dcvlog/` 下载，不依赖仓库根 SKILL，因此移除根入口不会让已安装的副本自动消失。旧版没有更新器的用户仍需按 INSTALL.md 做一次迁移。

验证结果见集成目录旁 `verification.json`。本次没有在真实手机云端或重建后的 WorkBuddy 沙箱完成验收，也没有宣称中国大陆无代理网络已验证。
