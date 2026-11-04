# DCVlog 一句话安装与自动更新

## 学员只需输入一次

在豆包工作或 WorkBuddy 新对话里粘贴同一句：

> 安装代川 DCVlog：https://github.com/daichuan-ai/dcvlog。请按 INSTALL.md 完成安装并启用自动更新。

安装成功后，日常只输入 `/DCVlog`。安装和更新沿用官方仓库；不要求学员操作终端、挑选目录、复制多个命令或每次重新安装。若宿主有权限或安全确认卡，仍按宿主要求操作，不绕过。

## 给执行安装的 AI：先区分首次安装和已有安装

1. 按宿主真实规则定位持久技能目录。**WorkBuddy**：当前程序 `createSkillsService` 从 `$WORKBUDDY_CONFIG_DIR/skills` 读取，未设时用 `$CODEBUDDY_CONFIG_DIR/skills`，再未设用 `~/.workbuddy/skills`；程序监听此目录变化并刷新列表，不把 `.codebuddy/skills` 或临时工作区当作同一个目录。**豆包工作**：其内置 `skill-creator-for-work` 要求安装到当前环境已存在的 `workspace/.user_skills`；从本次加载的内置 Skill 路径确定对应 workspace。macOS 实测位置为 `~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills`，Linux/云端路径可能不同。已有 DCVlog 时以本次真实加载路径为准；不扫描整个磁盘，不要求学员选路径。
2. 检查本次工具环境能否执行 Python 3、访问 GitHub 官方 HTTPS 并写入已确认的目标目录。优先使用宿主现有运行时，不擅自安装系统软件或更改网络；缺能力时只报告具体缺口，不生成替代 Skill。不先依赖 `npx skills`、Git 或系统 unzip。
3. 用 Python 标准库 urllib 下载官方主分支 ZIP：`https://codeload.github.com/daichuan-ai/dcvlog/zip/refs/heads/main`。HTTPS 最终域名只能是 GitHub 官方域名；下载最多16 MiB。用 zipfile 检查 ZIP 注释为40位十六进制提交标识，并核对 `dcvlog-main/skills/dcvlog/SKILL.md` 身份为 `dcvlog`、文件头版本与相邻 `VERSION` 一致。只将 `dcvlog-main/skills/dcvlog/tools/update_skill.py` 读入新建临时目录，不先覆盖旧目录、不执行包内其他脚本、不临时重写安装器。
4. 执行官方工具（由 AI 代为调用，学员不用复制这条终端命令）：

   ```text
   python3 "<临时目录>/update_skill.py" --install --host workbuddy
   ```

   WorkBuddy 使用上面的命令；豆包使用 `--install --host doubao --active-skill-dir "<本次已加载的内置Skill绝对目录>"`，由工具定位该 workspace 的 `.user_skills/dcvlog`。已有安装也可传 `--install --skill-dir "<实际DCVlog目录>"`。这些参数由 AI 填写，学员仍只粘贴开头那一句。

   `--install` 支持空目标的首次安装；已有正常安装则自动走原备份、更新、读回流程。遇到同名但身份不符或损坏的目录停止，不删除旧文件或创建假的占位 SKILL。临时下载必须取自本次官方 ZIP；不能调用旧副本里不支持首次安装的工具。
5. 后台执行时跟踪**原任务ID**到最终结果，不因前台等待超时重复启动。仅当返回 `installed/updated/up_to_date` 且 `verified:true`，才能说明文件安装已通过校验；核对返回的 `skill_dir` 确为本宿主目标，并读取 `SKILL.md`、`VERSION`、`tools/update_skill.py` 和三份 B002 创作范本。
6. 按宿主支持的方式完成个人技能注册/刷新/启用，使用宿主已安装列表或当前可发现技能元信息确认 `dcvlog` 可见、路径与上一步一致。安装器返回的 `host_registration_verified:false` 是明确提醒：**文件写入成功不证明技能列表已注册成功**。没有注册或发现证据时，说「文件已安装，技能列表生效尚未验证」，不能说全部完成。宿主确实要求用户点击导入或新开会话时，只说明这一个必要操作，不让用户重复安装。
7. 安装本身不要自动进入采访、调用遥测或上传文案。验证成功后前台只需回复：

   > DCVlog 已安装，自动更新已就绪。新建对话输入 /DCVlog 开始。

   若当前会话已经支持刷新则可省略「新建对话」。未验证的注册、重载、网络能力必须如实说明。

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
