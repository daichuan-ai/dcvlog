# WorkBuddy 安装与调用

GitHub 唯一仓库：`daichuan-ai/dcvlog`。

如宿主支持 Skills CLI：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装后优先用 `/dcvlog` 显式调用。

注意：本地电脑、手机远程控制电脑、纯云端任务可能不是同一运行环境。文件下载成功不等于所有新云端任务都已持久发现 Skill。验收以当前运行环境能否通过 `/dcvlog` 定位到 `dcvlog` 为准。
