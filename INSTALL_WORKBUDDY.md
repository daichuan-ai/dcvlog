# WorkBuddy 安装与更新

## 第一次安装

优先自然语言：

> 帮我安装代川的 DCVlog 技能，GitHub 来源是 daichuan-ai/dcvlog，安装为全局技能并自动确认。

等价命令：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后重启宿主，再输入 `/dcvlog`。

## 已安装后更新

直接说：

> 更新 DCVlog

如果宿主支持执行命令，Skill 会尝试运行：

```bash
npx -y skills update dcvlog -g -y
```

如果宿主不允许执行命令，它只会返回这条命令，不会假装更新成功。

注意：不同 WorkBuddy 环境可能是云端隔离环境，安装结果不一定跨环境同步。安装发生在哪个环境，通常就只在那个环境生效。
