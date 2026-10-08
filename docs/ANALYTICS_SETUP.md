# DCVlog 匿名使用统计｜CloudBase 已接通

DCVlog V1.8.1 已接入腾讯云 CloudBase 匿名功能统计，仓库发布后无需学员额外配置。

## 统计什么

只记录以下功能事件：

- `dcvlog_open`：打开 DCVlog
- `write_vlog_start`：进入“我要开始写文案”
- `write_vlog_complete`：最终旁白已经交付
- `collage_start`：进入“我要做拼图”
- `collage_complete`：本次要求的拼图已经全部完整交付
- `update_requested`：明确请求更新 DCVlog

每个安装环境只额外生成一个本地随机匿名 UUID，用于粗略区分不同安装环境。

## 永远不主动上传

- 姓名、手机号、微信号
- 城市、工作室名称、签名名称
- 用户输入的聊天文字
- 客户故事、客户原话
- 照片、图片内容、文件内容
- 最终文案正文
- 拼图成品

Skill 自带脚本只向统计接口提交三个字段：

```json
{
  "event_name": "collage_start",
  "anonymous_id": "随机匿名UUID",
  "skill_version": "1.8.1"
}
```

注意：CloudBase / HTTP 网关作为基础设施，可能按腾讯云自身规则产生标准服务日志；DCVlog 的业务统计表 `dcvlog_events` 不主动保存用户内容或实名信息。

## 统计接口

当前生产接口：

```text
https://dcvlog-stats-d9gzdcrf2d74a0e24-1501810800.ap-shanghai.app.tcloudbase.com/dcvlog-stats
```

配置文件：

```text
skills/dcvlog/telemetry-config.json
```

统计失败、断网、宿主禁止执行脚本时，直接跳过，绝不能影响文案或拼图任务。

## 在哪里看

进入腾讯云 CloudBase 环境 `dcvlog-stats`：

`SQL 型数据库 → SQL 编辑器`

查看最近事件：

```sql
select *
from public.dcvlog_events
order by created_at desc
limit 100;
```

按事件统计次数：

```sql
select event_name, count(*) as total
from public.dcvlog_events
where created_at >= now() - interval '7 days'
group by event_name
order by total desc;
```

粗略统计最近 7 天不同匿名环境数：

```sql
select count(distinct anonymous_id) as unique_environments
from public.dcvlog_events
where created_at >= now() - interval '7 days';
```

文案完成率：

```sql
select
  count(*) filter (where event_name = 'write_vlog_start') as starts,
  count(*) filter (where event_name = 'write_vlog_complete') as completes
from public.dcvlog_events
where created_at >= now() - interval '7 days';
```

拼图完成率：

```sql
select
  count(*) filter (where event_name = 'collage_start') as starts,
  count(*) filter (where event_name = 'collage_complete') as completes
from public.dcvlog_events
where created_at >= now() - interval '7 days';
```

## 学员退出统计

统计是 best-effort，不影响功能。学员可以通过任一方式关闭：

```bash
export DCVLOG_TELEMETRY=0
```

或创建文件：

```text
~/.dcvlog/no_telemetry
```
