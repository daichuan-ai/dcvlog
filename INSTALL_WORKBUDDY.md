# WorkBuddy安装与自动更新（1.9.5）

## 首次安装与旧学员的一次性迁移

学员只需在聊天框说：

> 帮我按 daichuan-ai/dcvlog 官方仓库最新的安装说明，升级我在WorkBuddy实际使用的 DCVlog。

以下步骤由执行升级的宿主完成，不要求学员操作终端：

1. 从本次加载的Skill元信息确定实际SKILL.md绝对路径并解析realpath；不要猜全局目录。
2. 旧包没有 `tools/update_skill.py` 时，优先从官方 `https://codeload.github.com/daichuan-ai/dcvlog/zip/refs/heads/main` 获取完整ZIP。用Python标准库urllib下载、zipfile读取；不要拼接 `curl && unzip`，不要依赖系统unzip或第三方镜像。
3. 检查HTTPS最终地址仍在GitHub官方域名，限制下载大小；ZIP注释应为40位提交标识，标准目录 `dcvlog-main/skills/dcvlog/` 中的SKILL身份应为dcvlog，文件头版本与VERSION应一致。缺项、CRC错误、身份或版本不符时停止，保留原安装。
4. 从已验证的官方ZIP仅读取 `dcvlog-main/skills/dcvlog/tools/update_skill.py`，保存到新建临时目录；不要先覆盖WorkBuddy旧文件，不执行仓库里的其他安装脚本。
5. 执行该官方更新器：`python3 "<临时目录>/update_skill.py" --skill-dir "<本次实际加载目录>"`。更新器负责旧格式兼容、固定提交完整包验证、备份、替换、读回与恢复，不交给AI临时重写这些步骤。
6. 命令进入后台时，使用工具返回的原任务ID取得最终输出；不能把15秒前台等待结束当成失败，也不能一直重复提交安装。工具失败或不能取得结果时明确说明未验证成功。
7. 只有JSON为 `updated/up_to_date` 且 `verified:true`，并确认skill_dir为本次实际目录，才报告成功。读回SKILL.md、VERSION和三份B002范本；宿主需要重载时新开会话。不能把另一份全局安装成功当作WorkBuddy生效。

网络正常时也可以使用原安装器获取完整包：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装器的全局目标不一定是本宿主实际加载目录。1.9.2及更早入口、以及无法取得新工具的1.9.3安装，需要先完成上述一次性迁移；旧入口不会仅因GitHub发布而自行改变。以上引导仍依赖宿主能读取官方安装说明、执行Python并写入实际目录，不能宣称所有旧宿主已自动迁移。

## 之后每次使用

输入 `/DCVlog`（大小写等价的 `/dcvlog`），自动核对官方main提交，在实际加载目录备份、同步完整Skill并读回校验，不再询问“更新/继续使用”。版本号相同但新增案例也会同步。更新后展示“1.约妆 Vlog 旁白 / 2.跟妆 Vlog 旁白（测试中）”；选1进入原约妆流程，选2仅回复“敬请期待，代川正在整理中。”。单独说写文案或做拼图不能启动创作。明确说“更新 DCVlog”作为维护请求执行同一更新流程。

成功后立即重读新SKILL和本次模式所需参考文件；宿主不支持重读时，需要新开会话。缺联网、执行或写入权限时会如实说明未完成，不绕过宿主权限，不更新另一份目录冒充成功。

不同设备/隔离环境需要各自完成一次迁移；不能假定安装目录共享。不得修改网络/代理或 `~/.dcvlog/` 许可与退出设置。文案、拼图、匿名统计和首次许可后的收稿机制保持各自原有规则。
