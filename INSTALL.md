# DCVlog 一句话安装与自动更新

## 学员只需输入一次

在豆包工作或 WorkBuddy 新对话里粘贴同一句：

> 安装代川 DCVlog：https://github.com/daichuan-ai/dcvlog。请按 INSTALL.md 完成安装并启用自动更新。

安装成功后，日常只输入 `/DCVlog`。安装和更新沿用官方仓库；不要求学员操作终端、挑选目录、复制多个命令或每次重新安装。若宿主有权限或安全确认卡，仍按宿主要求操作，不绕过。

2.3.0的同一入口提供「1.约妆 Vlog 旁白」「2.新娘跟妆 Vlog 旁白」「3.化妆师真实表达」。第三项随完整技能包安装与自动更新，无需安装另一个 Skill；安装校验须包含 `references/self-expression/` 下的五份参考。尚未发布到官方main的开发副本不能通过真实自动更新验证，否则会被官方版本覆盖。

## 给执行安装的 AI：先识别环境和安装渠道

**先判断工具运行在手机云端沙箱、遥控电脑，还是本地电脑。** 用户设备是手机，不代表工具运行在手机；使用工具返回的实际路径和宿主能力判断。不要把 macOS 路径套进 Linux 云端。下面所有终端操作由 AI 代执行，学员只粘贴开头那一句。

### 1. 已有安装

从本次宿主技能元信息取得实际加载的 DCVlog 目录。已有完整安装直接调用该目录的 `tools/update_skill.py --skill-dir "<实际目录>"`，不要再制造第二份。目录冲突、注册和只读限制按下文处理。

### 2. 首次安装：标准源 + 宿主接入

这是参考 DB Skill 的两层方式：Skills CLI 管理标准技能源，宿主适配器把它接入真实技能目录。

宿主允许命令执行，且已有 Node.js、npx、Git 时执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --skill dcvlog -a universal -y
```

不要使用 `--all` 安装到无关 Agent。检查 CLI 实际返回的安装路径，读取其中的 `SKILL.md`、`VERSION`、更新器及案例。常见公共源是 `~/.agents/skills/dcvlog`，但以实际输出为准。`-a universal` 仅安装标准公共源，由下一步接入当前宿主，不批量写入其他 Agent。CLI 的 `-g` 只表示当前运行环境的全局目录，不是 WorkBuddy 或豆包的账号云端注册。

如果本宿主已发现该源，不再链接。否则，在**确认当前宿主的技能目录后**运行源中附带的适配器：

```text
python3 "<标准源>/scripts/link_host.py" --host workbuddy --source "<标准源>"
```

- **WorkBuddy 本地／遥控电脑**：依次遵循 `WORKBUDDY_CONFIG_DIR`、`CODEBUDDY_CONFIG_DIR`、`~/.workbuddy`，技能目录为其 `skills/dcvlog`。支持非默认配置目录。
- **豆包工作**：将 `--host workbuddy` 改为 `--host doubao --active-skill-dir "<本次已加载的内置Skill绝对目录>"`，从当前环境真实 workspace 定位已有 `.user_skills/dcvlog`。不要照搬开发机的 macOS 路径。
- **手机云端**：先读取当前宿主的内置安装技能、工具说明或技能元信息。若它明确给出可发现的技能落点，可传 `--target-dir "<宿主确认的绝对目录>/dcvlog"`；不得猜 `/root/workbuddy/skills`，也不得把当前任务临时目录称为持久库。文件接入后仍需完成下一节云端注册验收。

适配器只建立指向同一完整源的目录链接，已有真实目录、断链或其他源一律保留并报告冲突。已有完整 DCVlog 应使用其更新器；不能删除用户目录来解决冲突。源必须是正式安装目录，不能链接临时克隆／下载目录。系统不允许链接时使用下面的官方完整包安装通道，不临时重写一份技能。

### 3. 无 npx／Git 或链接能力时

使用当前环境已有 Python 3 与官方 ZIP，不要求学员安装软件：

1. 用 Python 标准库 urllib 下载 `https://codeload.github.com/daichuan-ai/dcvlog/zip/refs/heads/main`，最多16 MiB，最终域名只能是 GitHub 官方域名。
2. 用 zipfile 检查 ZIP 注释为40位提交标识；核对 `dcvlog-main/skills/dcvlog/SKILL.md` 的 name 为 dcvlog、头部版本与 VERSION 一致。只把其中 `tools/update_skill.py` 写入新临时目录。
3. 执行 `python3 "<临时目录>/update_skill.py" --install --host workbuddy`；豆包将 `--host workbuddy` 改为 `--host doubao --active-skill-dir "<内置Skill实际目录>"`。云端仅当宿主已确认目标目录时用 `--install --skill-dir "<确认目录>/dcvlog"`；不靠本地默认目录猜云端规则。
4. 仅返回 `installed/updated/up_to_date` 且 `verified:true` 才说明文件通过校验。后台执行时跟踪原任务 ID 到最终结果，不重复启动。

完整包安装保留原备份、锁定原文校验、失败恢复和本地新增文件保护。没有 Python、执行或写入能力时，准备完整技能 ZIP，走宿主原生上传／导入；明确具体缺项，不能回复“安装完成”。

### 4. 技能列表与云端持久注册

文件写入或链接成功以后，按宿主支持的技能安装／导入能力，将 DCVlog 加入**当前使用环境**的已安装列表并启用。适配器与更新器返回的 `host_registration_verified:false` 是提醒：脚本没有替平台完成账号注册。

WorkBuddy 官方说明：Web 与客户端个人 Skill 库互不相通，云上任务读云上个人库；项目配置中的 Skill 在云端保存并跨端统一。因此手机云端应核对云端已安装库；使用项目时也可导入项目的 Skill 配置。仅放进沙箱、电脑个人库或项目文件夹不等于完成云端配置。没有宿主注册工具时，准备好完整 ZIP，告知必须在当前环境的技能面板导入这一项操作，不能伪造 marketplace ID。

验收顺序：当前技能列表可见且启用 → 新任务 `/DCVlog` 可发现 → 新任务重新取得实际加载路径并执行更新器。能检查重建／更换沙箱时再验证一次；没有此证据时标注“跨容器持久性未验证”。Claude 的 marketplace 声明只用于 Claude 插件安装，不能拿它证明 WorkBuddy 或豆包账号自动恢复。

安装本身不启动采访或上传内容。文件校验、列表、新任务均通过后，回复：

> DCVlog 已安装。以后输入 /DCVlog，会在使用时自动检查并同步更新。

任何未验证项单独如实说明。不要承诺离线、只读目录或平台不允许执行时仍能取得最新版。

## 自动更新发生在何时

- 每次用户输入 `/DCVlog`，技能调用**本次实际加载目录**中的 `tools/update_skill.py --skill-dir <实际目录>`，核对官方 main 提交；版本号相同但增加范本也会同步。明确说「更新 DCVlog」走同一工具。
- 更新前保留备份，整包校验后替换，再读回文件。成功后重新读取新 SKILL 和必要参考；宿主不能重读时只需新开会话，不重新安装。
- 这是**使用时自动检查更新**，不是平台技能市场托管更新，也不是后台定时常驻。断网、GitHub 不可达、只读挂载、无命令工具时保留旧版并说明本次未更新；下次启动再尝试。
- 不修改 `~/.dcvlog/` 内匿名ID、许可和退出设置；不跨设备假定安装共享；同机的两个宿主实际目录不同就各自安装一次，之后各自在自己的目录更新。

## 验收

交付前需要分别在豆包工作和 WorkBuddy 验证：新用户一句话安装 → 技能列表可见 → 新对话 `/DCVlog` → 官方同版本增加一个范本后再启动 → 实际加载目录同步成功。Python 测试和本机网络检查不能替代这两个平台实测；也不代表中国大陆普通网络均可访问 GitHub。

WorkBuddy 官方说明：https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market

## 已读取的宿主文件与本机验收（2026-11-04）

- WorkBuddy 5.9.3 内置 `marketplace-skill-installer/SKILL.md`：市场一键安装仅针对市场条目，不能伪造市场ID。`skill-creator/SKILL.md` 里的 CodeBuddy 默认路径不能覆盖 WorkBuddy 主程序规则。
- WorkBuddy 程序 `main/server.js`：`createSkillsService`、`scanBaseSkills`、`SkillsVersionEmitter` 共同确认用户目录读取及递归监听机制。安装到 `~/.workbuddy/skills/dcvlog` 后，已安装列表实测显示 DCVlog v1.9.5；新对话调用已实际执行更新器，返回 `up_to_date` 与 `verified:true`，之后出现约妆/跟妆首屏。
- 豆包 2.34.6 内置 `skill-creator-for-work/SKILL.md`：明确要求已存在的 `workspace/.user_skills`。界面程序通过 `getLocalSkillsByWorkspace` 取得环境真实技能目录与启用状态。个人与本地列表可同时存在同名 DCVlog，不能混认路径；已看到个人1.9.5和本地旧版两个条目；本次新建本地工作任务 `/DCVlog` 已在个人技能真实目录调用更新器并返回 `up_to_date`、`verified:true`，随后显示新版首屏。不同条目仍不能混认。
- 上述是这台电脑、这些版本与当前网络的证据，不代表所有客户端版本、云端环境、手机或无代理网络已验证。无法联网时不能声称“本次是官方最新版”。
