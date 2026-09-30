# 豆包工作安装｜学员版

只需要说：

> **安装代川的 dcvlog**

如果需要更明确：

> **安装 daichuan-ai 的 dcvlog**

唯一官方仓库：

`https://github.com/daichuan-ai/dcvlog`

这是已经存在的 GitHub Skill，不是让豆包工作临时生成一个 Skill。

安装完成后，彻底退出 App 再重新打开，让宿主重新扫描技能。然后从技能列表选择 **代川 DCVlog｜化妆师Vlog编导**；如果支持斜杠 Skill，也可以输入：

`/dcvlog`

## 给安装 Agent

若支持 Skills CLI，优先执行：

```bash
npx -y skills add daichuan-ai/dcvlog -g --all
```

只允许从 `daichuan-ai/dcvlog` 获取原始文件。安装后验证 `name=dcvlog`、`author=daichuan-ai`、`version=1.0.8`。

如果无法定位或安装，只说明失败原因；**禁止自行生成同名或相似 Skill 代替**。
