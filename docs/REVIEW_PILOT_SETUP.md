# DCVlog V1.8.7｜自愿完稿回收公测部署与验收

目标：让明确同意的学员继续在豆包工作正常写文案，完成稿件后尝试提交给代川人工看。**不能把「上传了 GitHub」等同于「云端收到正文」；数据库和 HTTPS 云函数须单独验收。原有 1.8.3 匿名事件统计不受影响。**

## 先检查四个事实

- 10月18日人工查询 `public.dcvlog_events` 得到：1.8.3 的 `write_vlog_complete` 有6条、不同匿名设备编号5个；证明事件上报在多个设备出现过，但不证明完整正文自动上传。
- 旧统计接口 `/dcvlog-stats` 只接收 `event_name/anonymous_id/skill_version`。新正文绝不能发送到它。
- 本版要在学员**首次明确同意**后发送，拒绝不影响继续写稿。不能追回此前学员已经完成的6篇文案。
- 自动收稿最后一跳依赖豆包工作能够把生成的正文写入UTF-8临时文件，并执行本Skill的Python脚本；如手机端缺少该能力，不能仅靠提示词保证回收，需换可控制的写作入口。

## 1. 建表（老师在腾讯云控制台操作一次）

选已有环境 `dcvlog-stats` → `PostgreSQL 管理` → `SQL 编辑器`。把 `cloudbase/review-collector/schema.sql` 全文粘贴执行。这只增加 `public.dcvlog_draft_reviews`，不碰 `public.dcvlog_events`。

表包含：唯一提交编号、匿名设备编号、Skill版本、视频客人数、稿件类型、最终旁白、简短事实依据、同意说明版本、创建和到期时间。启用RLS并撤销匿名读写授权；仅服务端 `service_role` 有权限。没有公开读取接口。

## 2. 部署独立 HTTP 云函数（老师操作一次）

在相同 CloudBase 环境新增**独立** Node.js 20 或更新的 HTTP 云函数 `dcvlog-review`。代码目录：`cloudbase/review-collector/`，入口 `index.js` 的 `exports.main`。程序只使用Node内置 `fetch`，不依赖第三方npm模块；通过腾讯云PostgreSQL REST API写入独立表。

需要在云函数**服务端环境变量**配置：

| 名称 | 内容 | 注意 |
| --- | --- | --- |
| `TCB_ENV` | 现有 CloudBase 环境真实ID | 不是函数名 |
| `CLOUDBASE_APIKEY` | 此环境服务端专用API Key（`service_role`） | **只能放在云函数环境变量**，不能贴进Skill、GitHub、截图或对话 |
| `REVIEW_PUBLIC_BETA` | 字符串 `true` | 公开公测必须明确开启；不填时保持关闭，除非配置了设备白名单 |
| `PILOT_DEVICE_IDS` | 可选的测试设备匿名UUID，英文逗号隔开 | 仅供限制性测试；开启公开公测时不按此名单限制 |

在 `HTTP 网关` → `路由管理` 为此函数增加新的 POST 访问路径，例如 `/dcvlog-review`，不要改动旧 `/dcvlog-stats` 路由。**公开模式必须在网关设置每 IP 的限频，限制请求体大小，并启用服务端的长度/同意版本校验**。不要把服务端 API Key 写入 GitHub 或发送给学员。不得在云函数里打印HTTP原文、Header或文案内容。匿名公网接口不能独立验证请求者是否真的点过同意，因此不是身份认证系统。

新函数成功返回 `{"accepted":true,...}`，失败返回一个错误码，不回显正文。公开模式测试：有有效匿名 UUID 且请求标记为同意时可写；未同意/格式错误必须拒绝，重复同一 `submission_id` 不应产生两条记录。**原先的云函数如果是三设备白名单旧代码，必须先重新上传本版 `cloudbase/review-collector/`，否则 `REVIEW_PUBLIC_BETA=true` 不会生效。**

> 腾讯云官方资料：`https://docs.cloudbase.net/service/access-cloud-function`、`https://docs.cloudbase.net/database/postgresql/http/insert`。具体部署页面按控制台实际显示为准。

## 3. 公测 Skill 启用

发布到 GitHub 的公测包已设定以下配置；先确认后端已开启公开模式、做好限频，再发布：

`skills/dcvlog/review-config.json`

```json
{
  "enabled": true,
  "provider": "cloudbase",
  "endpoint": "https://dcvlog-stats-d9gzdcrf2d74a0e24-1501810800.ap-shanghai.app.tcloudbase.com/dcvlog-review",
  "consent_version": "2026-10-18-v1",
  "timeout_seconds": 4.0
}
```

学员在豆包工作中更新 DCVlog 并进入写文案。宿主支持工具的情况下，首次应看到「愿意把最终旁白用于质量改进吗：同意/不同意」；只有选择同意且确实执行了脚本才会上传。若不同意，系统保留拒绝状态，不会再次追问或提交。宿主不支持 Python/临时文件或网络时，正常交稿但不会上传；不可宣称已经自动回收。

## 4. 老师如何看回收结果

仍在 `SQL 编辑器`，运行：

```sql
SELECT created_at, anonymous_id, skill_version, client_count,
       draft_status, final_text, facts_summary
FROM public.dcvlog_draft_reviews
ORDER BY created_at DESC
LIMIT 30;
```

可点开 `final_text` 单元格阅读。不要把导出的含客人信息CSV传到公共网盘。

每篇要人工标记：**主线、真实审美取舍、妆后画面感、多客人主次、是否模板化、是否有事实发明**。只看终稿不能百分百确定AI是否编造事实，`facts_summary` 只是辅助，必要时还需学员自愿提供原始聊天作深入排查。

## 5. 真实使用验收清单

1. 代川本人先在豆包工作完成1篇真实使用文案，确认数据库出现**完整最终旁白**，内容与他收到的版本一致（除明显联系方式遮盖）；再观察其他同意的学员。
2. 同一 `submission_id` 重试不会产生重复稿；另一 `submission_id` 是新的独立完成。
3. 不同意、状态文件丢失、禁用配置、无脚本权限、服务端关闭公测、网关失败，都不应上传，也不应耽误学员写稿。
4. 一位学员关闭收集后，以后的文案不再上传；已收集的旧文案由老师按匿名编号单独删除并反馈。
5. 记录实际试用者的「生成成功数」和「回收成功数」；仅查看成功上报记录**无法计算漏报率**，必须由受试学员确认总生成数。

## 6. 数据保留、停用、删除

公测期间建议最多保留30天。**`expires_at` 不会自动删除记录**；管理员需要设置定时任务至少每天执行：

```sql
DELETE FROM public.dcvlog_draft_reviews
WHERE expires_at < now();
```

个别学员退出或要求删除时，老师核对其匿名编号后在控制台执行（先用SELECT确认精确目标）：

```sql
-- 先用SELECT核对，不要盲目运行DELETE；把占位符换成该设备真实UUID。
SELECT id, created_at, left(final_text, 60) AS preview
FROM public.dcvlog_draft_reviews
WHERE anonymous_id = '<经学员确认的匿名UUID>'; 
```

删除申请无法凭真实姓名自动映射到匿名编号，应请学员提供本地编号或通过老师的课堂注册记录核实。若发生数据泄露或回收行为异常，立刻将 `review-config.json` 改回 `enabled:false` 并暂停云函数入口；旧功能统计仍能使用。

## 对外说明务必准确

- 不说“所有学员文案都会自动回收”，只说“经同意、宿主支持的情况下尝试回收”。
- 不说“内容百分百匿名”；自由文本可能仍间接识别客人。学员不应输入客人敏感个人信息。
- 未开启 HTTPS 云函数的 `REVIEW_PUBLIC_BETA=true` 且通过实机写入验证之前，**不要宣称已经能自动回收文案**。
- 公测阶段老师使用已有的 SQL 编辑器即可完成质量观察，后续再考虑教师专用查看页面。
