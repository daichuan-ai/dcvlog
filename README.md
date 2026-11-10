# 代川 DCVlog｜化妆师 Vlog 编导

当前版本 **2.2.0**。在已安装DCVlog的WorkBuddy或其他兼容宿主中新开对话，输入 `/DCVlog`（大小写均可）。先沿用自动更新器，在本次实际加载目录同步官方main的完整包并重读，再选择：

1. **约妆 Vlog 旁白**：原有真实服务采访、成熟案例、开场与结尾确认、试读和语气定型。
2. **新娘跟妆 Vlog 旁白**：画面时间线、回忆采访、人事物因素、主切口选择、补细节、全旁白初稿、实际DB修改、中稿补充确认、原声选择、文案和剪辑提示。

## 新学员安装

在豆包工作或 WorkBuddy 的对话框输入一次：

> 安装代川 DCVlog：https://github.com/daichuan-ai/dcvlog。请按 INSTALL.md 完成安装并启用自动更新。

之后输入 `/DCVlog`。安装 AI 按 [INSTALL.md](INSTALL.md) 完成标准安装、宿主接入、技能列表和新任务验收。手机云端必须在云端技能库生效；本机文件安装不能证明跨容器恢复。网络与宿主权限满足时，每次使用自动同步官方版本，包括同版本新增案例。

支持 Skills CLI 的环境可由 AI 执行标准命令：

```bash
npx -y skills add daichuan-ai/dcvlog -g --skill dcvlog -a universal -y
```

WorkBuddy、豆包未直接发现公共源时，安装 AI 使用包内 `scripts/link_host.py` 接入本次宿主确认的目录；无 npx／Git 时保留官方 ZIP + Python 完整安装通道。不要求学员挑选路径或执行第二条命令。

可选 Claude Code 插件通道：`/plugin marketplace add daichuan-ai/dcvlog`，然后 `/plugin install dcvlog@dcvlog-skills`。这是 Claude 的插件通道，不等于 WorkBuddy 账号注册。

## 已安装学员自动更新

无需另装跟妆技能，也无需下载更新包。`/DCVlog`先调用原更新器；成功后读取新版，选2开始采访。旧会话已经加载旧规则时，新开对话再启动。

只有实际加载目录的更新结果为 `updated` 或 `up_to_date` 且 `verified:true`，才能确认该目录与本次远端提交一致。发布到GitHub不代表某台手机已完成更新；网络、命令与目录写入权限仍由宿主提供。更新失败保留可用旧版并说明原因，不修改网络设置、不假报成功。

更新时备份旧安装，移除已退役功能文件。旧更新器首次拉取本版后，由新版启动流程执行同目录的退役清理工具；旧稿、个人新增文件与许可设置不受影响。

## 跟妆的 DB 环节

DB官方来源：[dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill)。优先使用当前任务环境中已安装的DB；没有时临时获取所需原始模块和资源。包内只有定位/获取工具与交接约定，不打包或摘录DB知识库。

默认实际执行 `dbs-script-flow` 检查及标记修改，再由支持明确整稿改写请求的 `dbs-title-cover-intro` 交出完整中稿。需要时追加共鸣诊断。先核对实际模块的当前能力，不让只做检查的模块冒充全文改写器。完成后返回本包跟妆流程。准备工具只返回 `prepared_not_executed`，不是改稿完成记录。

## 文件入口

唯一可安装入口为 `skills/dcvlog/SKILL.md`；根目录不再放 SKILL.md。根目录工具和参考副本仅保留历史兼容与开发用途。跟妆入口为 `references/bridal-interview.md`；因素、DB交接、声画交付按需加载相邻参考文件。不同宿主见 `INSTALL_WORKBUDDY.md`、`INSTALL_DOUABO.md`。

约妆原始案例保持原字节。约妆匿名事件与原有自愿收稿许可沿用既有规则；跟妆不上传采访或稿件。

## 发布与验证

只维护 `skills/dcvlog/` 的正式技能；不要把 Skill-only 包展开覆盖仓库根。已安装的旧副本继续由原更新器获取标准目录，无需删除重装。此次调整安装结构与说明，并补上安装器在 Python 3.9 下的网络超时兼容；2.0.0 的提示词、采访、DB交接及案例保持原字节。

[DB Skill 源码对照与手机云端验收边界](docs/DBSKILL_ARCHITECTURE.md)

2.2.0跟妆增加作者感受线与独立开头的分阶段创作：粗稿后先生成中心判断/情绪推进/结尾回应，再交DB创作；最后按创作简报、不同范式候选、用户选择、正文回接与全文装配执行。学员不会表达感受时AI可以代创，事实与客户原话保持边界。
