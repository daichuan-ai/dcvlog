# WorkBuddy 安装｜学员版

只需要说：

> **安装代川的 dcvlog**

如果需要更明确：

> **安装 daichuan-ai 的 dcvlog**

唯一官方仓库：

`https://github.com/daichuan-ai/dcvlog`

如果安装后技能列表暂时没刷新，彻底退出 App，再重新打开一次。

以后直接从技能列表选择 **代川 DCVlog｜化妆师Vlog编导**，或者输入：

`/dcvlog`

看到“好，川导开工……”就说明进对了。

## 给安装 Agent

这是安装一个已经存在的 GitHub Skill，不是创建新 Skill。

唯一来源：`daichuan-ai/dcvlog`

优先安装：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

安装后只做验证：`name=dcvlog`、`author=daichuan-ai`、`version=1.0.8`。

如果失败，只报告失败原因。不得根据用户背景或旧聊天自行创建替代 Skill。
