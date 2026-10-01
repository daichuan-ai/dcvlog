# 豆包工作安装与更新

## 第一次安装

新建对话，直接发送：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装完成后完全退出并重新打开 App，再输入：

```text
/dcvlog
```

## 已安装后更新

新建对话，直接发送：

```bash
npx -y skills update dcvlog -g -y
```

更新完成后完全退出并重新打开 App，再输入 `/dcvlog`。

如果更新命令提示找不到已安装的 `dcvlog`，重新执行第一次安装命令覆盖即可。

若安装 Agent 找不到仓库，不允许它自行生成替代 Skill。唯一来源是：
`https://github.com/daichuan-ai/dcvlog`
