# 豆包工作安装与更新

V1.9.2：每次在豆包工作输入 `/dcvlog`，Skill会在后台尝试读取官方 GitHub 最新版本；只有出现更新才询问“更新/继续使用”。无网络或检查工具不可用时照常进入功能，不保证能够检测到更新，也不会冒充成功。新增自愿收稿公测：仅在学员首次明确同意、宿主实际允许执行脚本及后台已开启接收时尝试上传最终旁白；否则正常写稿、不上传。

## 第一次安装｜优先自然语言

新建对话，直接说：

> 帮我安装代川的 DCVlog 技能，GitHub 来源是 daichuan-ai/dcvlog，安装为全局技能并自动确认。

如果豆包工作支持执行命令，它应等价执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后完全退出并重新打开 App，再输入：

```text
/dcvlog
```

若自然语言安装没有正确执行，直接复制上面的命令即可。

## 已安装后更新｜直接说“更新 DCVlog”

新建对话，直接说：

> 更新 DCVlog

已安装的 DCVlog 会直接执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

如果当前宿主不能直接执行命令，它会返回这条命令让你复制，不会假装更新成功。

更新完成后完全退出并重新打开 App，再输入 `/dcvlog`。


若安装 Agent 找不到仓库，不允许它自行生成替代 Skill。唯一来源是：
`https://github.com/daichuan-ai/dcvlog`
